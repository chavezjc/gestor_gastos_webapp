from flask import Flask, render_template # Añadimos render_template aquí

app = Flask(__name__)

@app.route('/')
def hello_world():
    # Esta era la línea antigua:
    # return '¡Hola Mundo desde Flask!'
    # Esta es la nueva línea:
    return render_template('index.html') 

if __name__ == '__main__':
    app.run(debug=True)