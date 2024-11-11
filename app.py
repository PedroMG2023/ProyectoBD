from flask import Flask, render_template, request, redirect, url_for, session, flash
import pyodbc
import uuid


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

# Ruta de trabajadores para agregar un nuevo trabajador
@app.route('/trabajadores', methods=['GET', 'POST'])
def trabajadores():
    if request.method == 'POST':
        # Si el método es POST, agregamos un nuevo trabajador
        nombre = request.form['nombre']
        salario = request.form['salario']
        contrasena = request.form['contrasena']

        try:
            with pyodbc.connect(connection_string) as conn:
                cursor = conn.cursor()

                # Obtener el ID más alto actual y sumarle 1
                cursor.execute("SELECT COALESCE(MAX(ID_Trabajador), 0) + 1 AS next_id FROM Trabajador")
                next_id = cursor.fetchone().next_id  # Esto obtiene el próximo ID disponible

                # Inserta el nuevo trabajador en la base de datos, usando el nuevo ID generado
                cursor.execute("""
                    INSERT INTO Trabajador (ID_Trabajador, Nombre_Trabajador, Salario, Contraseña)
                    VALUES (?, ?, ?, ?)
                """, (next_id, nombre, salario, contrasena))
                conn.commit()  # Guardar cambios en la base de datos
                flash('Trabajador agregado correctamente', 'success')
        except Exception as e:
            flash(f'Error al agregar trabajador: {str(e)}', 'danger')

        return redirect(url_for('trabajadores'))

    # Si el método es GET, mostramos la lista de trabajadores
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT ID_Trabajador, Nombre_Trabajador, Salario, Contraseña FROM Trabajador")
        trabajadores = cursor.fetchall()

    return render_template('Jefe/trabajadores.html', trabajadores=trabajadores)

@app.route('/eliminarEmpleado/<int:valor>', methods=['GET', 'POST'])
def eliminarEmpleado(valor):
    try:
        with pyodbc.connect(connection_string) as conn:
            cursor = conn.cursor()

            # Ejecutar la consulta DELETE para borrar al trabajador con el ID especificado
            cursor.execute("DELETE FROM Trabajador WHERE ID_Trabajador = ?", (valor,))
            conn.commit()  # Guardar los cambios en la base de datos

            flash(f'Trabajador con ID {valor} eliminado correctamente.', 'success')
    except Exception as e:
        flash(f'Error al eliminar trabajador: {str(e)}', 'danger')

    return redirect(url_for('trabajadores'))



@app.route('/inventario')
def inventario():
    return render_template('Jefe/inventario.html')

@app.route('/factura')
def factura():
    with pyodbc.connect(connection_string) as conn:
        cursor = conn.cursor()
        
        # Retrieve all invoices ordered by date (most recent first), including the provider name
        cursor.execute("""
            SELECT 
                f.Numero_FacturaCompra, 
                f.ID_Proveedor, 
                p.Nombre_Proveedor,  -- Nombre del proveedor
                f.Fecha_FacturaCompra, 
                f.Precio_Unitario, 
                f.Precio_Total,
                i.Nombre_MateriaPrima, 
                fi.Cantidad_Comprada
            FROM Factura_Compra f
            LEFT JOIN FacturaCompraInsumo fi ON f.Numero_FacturaCompra = fi.Numero_FacturaCompra
            LEFT JOIN Insumo i ON fi.ID_Insumo = i.ID_Insumo
            LEFT JOIN Proveedor p ON f.ID_Proveedor = p.ID_Proveedor  -- Relación con Proveedor
            ORDER BY f.Fecha_FacturaCompra DESC, f.Numero_FacturaCompra DESC
        """)
        
        # Organize data by invoices with their insumo items
        invoices = []
        current_invoice = None

        for row in cursor:
            invoice_num = row.Numero_FacturaCompra
            if current_invoice is None or current_invoice['numero'] != invoice_num:
                # Add the previous invoice to the list and start a new one
                if current_invoice:
                    invoices.append(current_invoice)
                current_invoice = {
                    "numero": invoice_num,
                    "proveedor_id": row.ID_Proveedor,  # Keep the provider's ID
                    "proveedor": row.Nombre_Proveedor,  # Use the provider's name
                    "fecha": row.Fecha_FacturaCompra,
                    "precio_unitario": row.Precio_Unitario,
                    "precio_total": row.Precio_Total,
                    "insumos": []
                }
            
            # Append insumo details to the current invoice's list of items
            if row.Nombre_MateriaPrima:
                current_invoice["insumos"].append({
                    "nombre": row.Nombre_MateriaPrima,
                    "cantidad": row.Cantidad_Comprada
                })

        # Add the last invoice if it exists
        if current_invoice:
            invoices.append(current_invoice)

    return render_template('Jefe/factura.html', invoices=invoices)

if __name__ == '__main__':
    app.run(debug=True)
