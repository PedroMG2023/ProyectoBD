from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de conexión con la base de datos
server = 'DESKTOP-OCDVC2C'
database = 'Panaderia'
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

# Ruta para la página de inicio de sesión
@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        # Comprobar si es jefe
        if usuario == 'Jefe' and contrasena == 'ContraseñaJefe':
            session['usuario'] = 'Jefe'
            return redirect(url_for('jefe'))
        
        # Comprobar en la base de datos si es trabajador
        else:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT Nombre_Trabajador FROM Trabajador WHERE Nombre_Trabajador = ? AND Contraseña = ?", (usuario, contrasena))
                trabajador = cursor.fetchone()
                
                if trabajador:
                    session['usuario'] = trabajador.Nombre_Trabajador
                    return redirect(url_for('trabajador'))
                else:
                    flash('Credenciales incorrectas, por favor intente de nuevo.')

    return render_template('index.html')

# Página del jefe
@app.route('/jefe')
def jefe():
    if 'usuario' in session and session['usuario'] == 'Jefe':
        return render_template('Jefe/jefe.html')
    return redirect(url_for('login'))

# Página del trabajador
@app.route('/trabajador')
def trabajador():
    if 'usuario' in session and session['usuario'] != 'Jefe':
        return render_template('Trabajador/trabajador.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
