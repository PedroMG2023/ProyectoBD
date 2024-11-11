from flask import Flask, render_template

app = Flask(__name__)


@app.route('/')
def hello_world():  # put application's code here
    return render_template("index.html")

@app.route('/EmpleadoProducto')
def EmpleadoProducto():  # put application's code here
    return render_template("VistasEmpleado/IngresarProducto.html")

@app.route('/EmpleadoFactura')
def EmpleadoFactura():  # put application's code here
    return render_template("VistasEmpleado/EmpleadoFactura.html")


if __name__ == '__main__':
    app.run()
