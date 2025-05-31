from flask import Flask

# Crear una instancia de la aplicación Flask
app = Flask(__name__)

# Definir una ruta para la página de inicio
@app.route('/')
def hello_world():
    return '¡Hola Mundo desde Flask!'

# Esto permite ejecutar la aplicación directamente con "python app.py"
# Solo para desarrollo, no para producción.
if __name__ == '__main__':
    app.run(debug=True)