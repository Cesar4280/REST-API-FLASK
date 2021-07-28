# modulos
from flask_mysqldb import MySQL
from flask import Flask, jsonify, request
from flask_cors import CORS, cross_origin
from helper import fields, params, values, safekey, timestamp

# incializacion
app = Flask(__name__)

# configuraciones (conexion Mysql) y (CORS)
app.config.update({
    "MYSQL_USER": "root",
    "SECRET_KEY": safekey(),
    "CORS_HEADERS": "Content-Type",
    "MYSQL_CURSORCLASS": "DictCursor",
    "MYSQL_DB": "bd_correccion_canadop"
})


# conectarse
cors = CORS(app)
mysql = MySQL(app)


# rutas (solicitudes a la API)


# prueba
@app.route("/api/test/ping", methods=["GET"])
def ping():
    return jsonify({
        "status": 200,
        "error": False,
        "message": {
            "info": "Todo está bien",
            "success": "Solicitud recibida"
        },
        "timestamp": timestamp()
    })


# todos los perros
@app.route("/api/perros/todos", methods=["GET"])
def getDogs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM perro")
    dogs = cur.fetchall()
    cur.close()
    return jsonify({
        "dogs": dogs,
        "status": 200,
        "error": False,
        "timestamp": timestamp(),
        "message": "Lista de perros"
    })


# los perros en adopción
@app.route("/api/perros/adopcion", methods=["GET"])
def getAdoptableDogs():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM perro WHERE PRR_EMPAREJADO IS NULL AND PRR_DESPARASITADO=1")
    dogs = cur.fetchall()
    cur.close()
    return jsonify({
        "dogs": dogs,
        "status": 200,
        "error": False,
        "timestamp": timestamp(),
        "message": "Lista de perros en adopción"
    })


# un perro por id
@app.route("/api/perros/id/<int:id>", methods=["GET"])
def getDogById(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM perro WHERE PRR_ID=%s", (id,))
    dog = cur.fetchone()
    cur.close()
    res = {"dog": dog, "timestamp": timestamp()}
    res.update(
        {"status": 200, "error": False, "message": "Perro encontrado"}
        if dog else
        {"status": 404, "error": True, "message": "Perro no encontrado"}
    )
    return jsonify(res)


# un perro por codigo
@app.route("/api/perros/codigo/<string:code>", methods=["GET"])
def getDogByCode(code):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM perro WHERE PRR_COD=%s", (code,))
    dog = cur.fetchone()
    cur.close()
    res = {"dog": dog, "timestamp": timestamp()}
    res.update(
        {"status": 200, "error": False, "message": "Perro encontrado"}
        if dog else
        {"status": 404, "error": True, "message": "Perro no encontrado"}
    )
    return jsonify(res)


# registrar perro
@app.route("/api/perros/agregar", methods=["POST"])
def addDog():
    cur, dog = mysql.connection.cursor(), dict(request.json)
    cur.execute(f"INSERT INTO perro({fields(dog)}) VALUES({params(len(dog))})", values(dog))
    cur.execute("UPDATE perro SET PRR_COD=CONCAT(PRR_COD,PRR_ID) WHERE PRR_ID=%s", (cur.lastrowid,))
    mysql.connection.commit()
    cur.close()
    return jsonify({
        "status": 200, 
        "error": False, 
        "timestamp": timestamp(),
        "message": "Registro exitoso"
    })


# actualizar los datos de un perro por id
@app.route("/api/perros/actualizar/id/<int:id>", methods=["POST"])
def editDog(id):
    dog = dict(request.json)
    cur = mysql.connection.cursor()
    keys = ",".join([f"{key}=%s" for key in dog])
    cur.execute(f"UPDATE perro SET {keys} WHERE PRR_ID=%s", (*dog.values(), id))
    mysql.connection.commit()
    cur.close()
    return jsonify({
        "status": 200,
        "error": False,
        "timestamp": timestamp(),
        "message": "Perro actualizado"
    })


# todas las razas
@app.route("/api/razas/todas", methods=["GET"])
def getBreeds():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM raza")
    breeds = cur.fetchall()
    cur.close()
    return jsonify({
        "status": 200,
        "error": False,
        "breeds": breeds,
        "timestamp": timestamp(),
        "message": "Lista de razas caninas"
    })


# una raza por id
@app.route("/api/razas/id/<int:id>", methods=["GET"])
def getBreedById(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM raza WHERE RAZA_ID=%s", (id,))
    breed = cur.fetchone()
    cur.close()
    res = {"breed": breed, "timestamp": timestamp()}
    res.update(
        {"status": 200, "error": False, "message": "Raza encontrada"}
        if breed else
        {"status": 404, "error": True, "message": "Raza no encontrada"}
    )
    return jsonify(res)


# seguimiento de todos los caninos
@app.route("/api/admin/tablero", methods=["GET"])
def getDashboard():
    cur = mysql.connection.cursor()
    cur.execute("""
        SELECT 
            PRR_ID,
            PRR_COD,
            PRR_NOMBRE,
            RAZA_NOMBRE,
            IF(PRR_SEXO='M','Macho','Hembra') AS PRR_SEXO,
            PRR_FING,
            PRR_TAMANO,
            PRR_LONGEVIDAD,
            CONCAT_WS(' ',PRR_ALTURA,'cm') AS PRR_ALTURA,
            PRR_COLOR,
            IF(ISNULL(PRR_DESPARASITADO),'No','Si') AS PRR_DESPARASITADO,
            IF(ISNULL(PRR_ESTERILIZADO),'No','Si') AS PRR_ESTERILIZADO,
            PRR_SALUD 
        FROM 
            perro P JOIN raza R ON P.RAZA_ID=R.RAZA_ID
    """)
    dogs = cur.fetchall()
    cur.close()
    return jsonify({
        "dogs": dogs,
        "status": 200,
        "error": False,
        "timestamp": timestamp(),
        "message": "Lista de perros"
    })


# un adoptante por id
@app.route("/api/adoptantes/id/<int:id>", methods=["GET"])
def getAdopterById(id):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM adoptante WHERE ADOP_ID=%s", (id,))
    ado = cur.fetchone()
    cur.close()
    res = {"adopter": ado, "timestamp": timestamp()}
    res.update(
        {"status": 200, "error": False, "message": "Adoptante encontrado"}
        if ado else
        {"status": 404, "error": True, "message": "Adoptante no encontrado"}
    )
    return jsonify(res)


# un adoptante por cedula
@app.route("/api/adoptantes/cedula/<string:dni>", methods=["GET"])
@cross_origin()
def getAdopterByDni(dni):
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM adoptante WHERE ADOP_CC=%s", (dni,))
    ado = cur.fetchone()
    cur.close()
    res = {"adopter": ado, "timestamp": timestamp()}
    res.update(
        {"status": 200, "error": False, "message": "Adoptante encontrado"}
        if ado else
        {"status": 404, "error": True, "message": "Adoptante no encontrado"}
    )
    return jsonify(res)


# registrar adoptante
@app.route("/api/adoptantes/registrar", methods=["POST"])
def addAdopter():
    cur, ado = mysql.connection.cursor(), dict(request.json)
    cur.execute(f"INSERT INTO adoptante({fields(ado)}) VALUES({params(len(ado))})", values(ado))
    mysql.connection.commit()
    cur.close()
    return jsonify({
        "status": 200, 
        "error": False, 
        "timestamp": timestamp(),
        "message": "Registro exitoso"
    })


# registrar proceso de adopcion
@app.route("/api/adopciones/registrar", methods=["POST"])
def addAdoption():
    cur, rep = mysql.connection.cursor(), dict(request.json)
    cur.execute(f"INSERT INTO adoptar({fields(rep)}) VALUES({params(len(rep))})", values(rep))
    mysql.connection.commit()
    cur.close()
    return jsonify({
        "status": 200, 
        "error": False, 
        "timestamp": timestamp(),
        "message": "Registro exitoso"
    })


# actualizar los datos de un adoptante por id
@app.route("/api/adoptantes/actualizar/id/<int:id>", methods=["POST"])
def editAdopterById(id):
    ado = dict(request.json)
    cur = mysql.connection.cursor()
    keys = ",".join([f"{key}=%s" for key in ado])
    cur.execute(f"UPDATE adoptante SET {keys} WHERE ADOP_ID=%s", (*ado.values(), id))
    mysql.connection.commit()
    cur.close()
    return jsonify({
        "status": 200,
        "error": False,
        "timestamp": timestamp(),
        "message": "Adoptante actualizado"
    })


# actualizar los datos de un adoptante por cedula
@app.route("/api/adoptantes/actualizar/cedula/<string:dni>", methods=["POST"])
def editAdopterByDni(dni):
    ado = dict(request.json)
    cur = mysql.connection.cursor()
    keys = ",".join([f"{key}=%s" for key in ado])
    cur.execute(f"UPDATE adoptante SET {keys} WHERE ADOP_CC=%s", (*ado.values(), dni))
    mysql.connection.commit()
    cur.close()
    return jsonify({
        "status": 200,
        "error": False,
        "timestamp": timestamp(),
        "message": "Adoptante actualizado"
    })


# todos los usuarios
@app.route("/api/usuarios/todos", methods=["GET"])
def getUsers():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM usuario")
    users = cur.fetchall()
    cur.close()
    return jsonify({
        "status": 200,
        "error": False,
        "users": users,
        "timestamp": timestamp(),
        "message": "Lista de usuarios"
    })


# arranque de la aplicacion
if __name__ == "__main__":
    app.run(port=3000, debug=True)
