from flask import Flask, render_template, request, redirect, session
from flask_mail import Mail, Message
from pymongo import MongoClient
from bson.objectid import ObjectId
import random
import certifi

app = Flask(__name__)
app.secret_key = "yamjarfer53"
app.config["MAIL_SERVER"] = "smtp.gmail.com"
app.config["MAIL_PORT"] = 587
app.config["MAIL_USE_TLS"] = True
app.config["MAIL_USERNAME"] = "24308060610036@cetis61.edu.mx"
app.config["MAIL_PASSWORD"] = "yamjarfer53"

mail = Mail(app)

# Configuración de MongoDB Atlas
MONGO_URI = "mongodb+srv://24308060610036_db_user:yamjarfer53@cluster0.0hepetv.mongodb.net/trevi3?retryWrites=true&w=majority"
cliente = MongoClient(
    MONGO_URI, 
    tls=True,
    tlsCAFile=certifi.where(),
    tlsAllowInvalidCertificates=True,
    serverSelectionTimeoutMS=5000,
    retryWrites=True
)
db = cliente["trevi3"]
usuarios = db["usuarios"]
pacientes = db["pacientes"]

codigo_recuperacion = {}

@app.route("/")
def inicio():
    return render_template("index.html")

# Cambiado a /register para coincidir con layout.html
@app.route("/register", methods=["GET", "POST"])
def register():

    if request.method == "POST":

        usuario = {
            "nombre": request.form["nombre"],
            "correo": request.form["correo"],
            "password": request.form["password"]
        }

        # Verificar si ya existe
        if usuarios.find_one({"correo": usuario["correo"]}):
            return "El correo ya está registrado."

        usuarios.insert_one(usuario)

        return redirect("/login")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():

    if request.method == "POST":

        correo = request.form["correo"]
        password = request.form["password"]

        usuario = usuarios.find_one({"correo": correo, "password": password})
        if usuario:
            session["usuario"] = usuario["nombre"]
            return redirect("/dashboard")

        return "Correo o contraseña incorrectos"

    return render_template("login.html")


@app.route("/forgot", methods=["GET", "POST"])
def forgot():

    if request.method == "POST":

        correo = request.form["correo"]

        usuario = usuarios.find_one({
            "correo": correo
        })

        if usuario:

            codigo = str(random.randint(1000, 9999))

            codigo_recuperacion[correo] = codigo

            mensaje = Message(
                "Recuperación de contraseña",
                sender=app.config["MAIL_USERNAME"],
                recipients=[correo]
            )

            mensaje.body = f"""
Hola {usuario['nombre']}

Tu código de recuperación es:

{codigo}
            """

            mail.send(mensaje)

            return redirect(f"/reset/{correo}")

        return "Correo no encontrado"

    return render_template("forgot.html")


@app.route("/reset/<correo>", methods=["GET", "POST"])
def reset(correo):

    if request.method == "POST":

        codigo = request.form["codigo"]

        nueva = request.form["password"]

        if codigo_recuperacion.get(correo) == codigo:

            usuarios.update_one(
                {"correo": correo},
                {
                    "$set": {
                        "password": nueva
                    }
                }
            )

            codigo_recuperacion.pop(correo)

            return redirect("/login")

        return "Código incorrecto"

    return render_template("reset.html", correo=correo)

@app.route("/dashboard")
def dashboard():

    if "usuario" in session:

        return render_template("dashboard.html", usuario=session["usuario"])

    return redirect("/login")


@app.route("/pacientes", methods=["GET", "POST"])
def pacientes_view():

    if "usuario" not in session:
        return redirect("/login")

    if request.method == "POST":

        paciente = {
            "nombre": request.form["nombre"],
            "edad": request.form["edad"],
            "enfermedad": request.form["enfermedad"],
            "telefono": request.form["telefono"]
        }

        pacientes.insert_one(paciente)
        return redirect("/pacientes")

    lista_pacientes = list(pacientes.find())
    return render_template("pacientes.html", pacientes=lista_pacientes)

@app.route("/eliminar/<id>")
def eliminar(id):

    if "usuario" not in session:
        return redirect("/login")

    pacientes.delete_one({"_id": ObjectId(id)})

    return redirect("/pacientes")


@app.route("/logout")
def logout():

    session.pop("usuario", None)

    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)