from flask import Flask, render_template, request, redirect, session
from pymongo import MongoClient
from bson.objectid import ObjectId
import certifi

app = Flask(__name__)
app.secret_key = "yayi0821"

MONGO_URI = "mongodb+srv://24308060610121_db_user:yayi0821@cluster0.0hepetv.mongodb.net/trevi3?retryWrites=true&w=majority"

try:
    cliente = MongoClient("mongodb://localhost:27017/"
        dbname="trevi3",
        username="24308060610121_db_user",
        password="yayi0821",
        tls=true
    )
    cliente.admin.command("ping")
    print("Conectado a MongoDB Atlas")
except Exception as error:
    print("Error de conexión:", error)

db = cliente["trevi3"]
usuarios = db["usuarios"]
pacientes = db["pacientes"]

@app.route("/")
def inicio():
    return render_template("index.html")


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        nuevo_usuario = {
            "nombre": request.form["nombre"],
            "correo": request.form["correo"],
            "password": request.form["password"]
        }
        
        if usuarios.find_one({"correo": nuevo_usuario["correo"]}):
            return "El correo ya está registrado. <a href='/register'>Intentar de nuevo</a>"
            
        usuarios.insert_one(nuevo_usuario)
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


@app.route("/dashboard")
def dashboard():
    if "usuario" not in session:
        return redirect("/login")
    return render_template("dashboard.html", usuario=session["usuario"])


@app.route("/pacientes", methods=["GET", "POST"])
def pacientes_view():
    if "usuario" not in session:
        return redirect("/login")
    if request.method == "POST":
        nuevo_paciente = {
            "nombre": request.form["nombre"],
            "edad": request.form["edad"],
            "enfermedad": request.form["enfermedad"],
            "telefono": request.form["telefono"]
        }
        pacientes.insert_one(nuevo_paciente)
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