from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc

app = Flask(__name__)
app.secret_key = 'tu_clave_secreta'

# Configuración de conexión con la base de datos
server = 'DESKTOP-OCDVC2C'
database = 'Panaderia'
connection_string = f'DRIVER={{SQL Server}};SERVER={server};DATABASE={database};Trusted_Connection=yes;'

@app.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['usuario']
        contrasena = request.form['contrasena']
        
        if usuario == 'Jefe' and contrasena == 'ContraseñaJefe':
            session['usuario'] = 'Jefe'
            return redirect(url_for('jefe'))
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

@app.route('/jefe')
def jefe():
    if 'usuario' in session and session['usuario'] == 'Jefe':
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()
            
            # Obtener último trabajador con su ID, nombre y salario
            cursor.execute("SELECT TOP 1 ID_Trabajador, Nombre_Trabajador, Salario FROM Trabajador ORDER BY ID_Trabajador DESC")
            ultimo_trabajador = cursor.fetchone()
            trabajador_data = {
                "id": ultimo_trabajador.ID_Trabajador,
                "nombre": ultimo_trabajador.Nombre_Trabajador,
                "salario": ultimo_trabajador.Salario
            } if ultimo_trabajador else None

            # Obtener insumo con menor cantidad
            cursor.execute("SELECT TOP 1 Nombre_MateriaPrima, Cantidad_Insumo FROM Insumo ORDER BY Cantidad_Insumo ASC")
            insumo_minimo = cursor.fetchone()
            insumo_data = {
                "nombre": insumo_minimo.Nombre_MateriaPrima,
                "cantidad": insumo_minimo.Cantidad_Insumo
            } if insumo_minimo else None

            # Obtener producto final con menor cantidad
            cursor.execute("SELECT TOP 1 Nombre_Producto, Descripcion_Producto, Fecha_Entrada FROM Producto_Final ORDER BY Fecha_Entrada ASC")
            producto_minimo = cursor.fetchone()

            producto_data = {
                "nombre": producto_minimo.Nombre_Producto,
                "descripcion": producto_minimo.Descripcion_Producto,
                "fecha_entrada": producto_minimo.Fecha_Entrada
            } if producto_minimo else None

            # Obtener última factura gestionada
            cursor.execute("SELECT TOP 1 Numero_FacturaCompra, Precio_Unitario, Precio_Total, Fecha_FacturaCompra FROM Factura_Compra ORDER BY Fecha_FacturaCompra DESC")
            ultima_factura = cursor.fetchone()
            factura_data = {
                "numero": ultima_factura.Numero_FacturaCompra,
                "gasto": ultima_factura.Precio_Unitario,
                "gasto_total": ultima_factura.Precio_Total,
                "fecha": ultima_factura.Fecha_FacturaCompra
            } if ultima_factura else None

        return render_template(
            'Jefe/jefe.html',
            trabajador=trabajador_data,
            insumo=insumo_data,
            producto=producto_data,
            factura=factura_data
        )
    return redirect(url_for('login'))


@app.route('/trabajador')
def trabajador():
    if 'usuario' in session and session['usuario'] != 'Jefe':
        return render_template('Trabajador/trabajador.html')
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
