from flask import Flask, render_template, request, redirect, url_for, flash
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.sql import func
from decimal import Decimal, InvalidOperation
from datetime import datetime
from sqlalchemy import or_ # <--- AÑADE O ASEGÚRATE DE QUE ESTA LÍNEA ESTÉ PRESENTE

# 1. Crear una instancia de la aplicación Flask
app = Flask(__name__)
app.secret_key = 'tu_clave_secreta_super_dificil_de_adivinar' # ¡DEBES CAMBIAR ESTO POR ALGO SEGURO!

# 2. Configuraciones para SQLAlchemy
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://root:@localhost:3306/gestor_gastos_db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Crea una instancia de SQLAlchemy
db = SQLAlchemy(app)

# 4. Definiciones de Modelos
class Personal(db.Model):
    __tablename__ = 'personal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_completo = db.Column(db.String(150), nullable=False)
    documento_identidad = db.Column(db.String(20), nullable=False, unique=True)
    cargo = db.Column(db.String(100), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion_registro = db.Column(db.DateTime, nullable=False, server_default=func.now())
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<Personal {self.id}: {self.nombre_completo}>'

class ProveedoresServicios(db.Model):
    __tablename__ = 'proveedores_servicios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_proveedor_servicio = db.Column(db.String(150), nullable=False, unique=True)
    tipo_servicio = db.Column(db.String(100), nullable=True)
    referencia_pago = db.Column(db.String(50), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion_registro = db.Column(db.DateTime, nullable=False, server_default=func.now())
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<ProveedoresServicios {self.id}: {self.nombre_proveedor_servicio}>'

class ConceptosGastoVarios(db.Model):
    __tablename__ = 'conceptos_gasto_varios'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_concepto = db.Column(db.String(150), nullable=False)
    descripcion_concepto = db.Column(db.String(255), nullable=True)
    activo = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion_registro = db.Column(db.DateTime, nullable=False, server_default=func.now())
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<ConceptosGastoVarios {self.id}: {self.nombre_concepto}>'

class CategoriasGastoPrincipales(db.Model):
    __tablename__ = 'categorias_gasto_principales'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nombre_categoria = db.Column(db.String(100), nullable=False, unique=True)
    descripcion_categoria = db.Column(db.String(255), nullable=True)
    activa = db.Column(db.Boolean, nullable=False, default=True)
    fecha_creacion_registro = db.Column(db.DateTime, nullable=False, server_default=func.now())
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f'<CategoriasGastoPrincipales {self.id}: {self.nombre_categoria}>'

class DocumentosARendir(db.Model):
    __tablename__ = 'documentos_a_rendir'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    tipo_documento = db.Column(db.String(20), nullable=False)
    numero_documento = db.Column(db.String(50), nullable=False)
    fecha_emision = db.Column(db.Date, nullable=False)
    monto_total_documento = db.Column(db.Numeric(10, 2), nullable=True)
    descripcion_general = db.Column(db.String(255), nullable=True)
    estado_documento = db.Column(db.String(25), nullable=False, default='Pendiente')
    fecha_creacion_registro = db.Column(db.DateTime, nullable=False, server_default=func.now())
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    items = db.relationship('ItemsGasto', backref='documento', lazy='dynamic', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<DocumentosARendir {self.id}: {self.tipo_documento} {self.numero_documento}>'

class ItemsGasto(db.Model):
    __tablename__ = 'items_gasto'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    documento_id = db.Column(db.Integer, db.ForeignKey('documentos_a_rendir.id'), nullable=False)
    categoria_principal_id = db.Column(db.Integer, db.ForeignKey('categorias_gasto_principales.id'), nullable=False)
    descripcion_item = db.Column(db.String(255), nullable=False)
    monto_item = db.Column(db.Numeric(10, 2), nullable=False)
    fecha_item = db.Column(db.Date, nullable=False)
    personal_id = db.Column(db.Integer, db.ForeignKey('personal.id'), nullable=True)
    proveedor_servicio_id = db.Column(db.Integer, db.ForeignKey('proveedores_servicios.id'), nullable=True)
    concepto_gasto_vario_id = db.Column(db.Integer, db.ForeignKey('conceptos_gasto_varios.id'), nullable=True)
    fecha_creacion_registro = db.Column(db.DateTime, nullable=False, server_default=func.now())
    fecha_ultima_modificacion = db.Column(db.DateTime, nullable=False, server_default=func.now(), onupdate=func.now())
    categoria = db.relationship('CategoriasGastoPrincipales', backref=db.backref('items_por_categoria', lazy=True))
    persona = db.relationship('Personal', backref=db.backref('items_para_persona', lazy=True))
    proveedor = db.relationship('ProveedoresServicios', backref=db.backref('items_para_proveedor', lazy=True))
    concepto_vario = db.relationship('ConceptosGastoVarios', backref=db.backref('items_por_concepto_vario', lazy=True))

    def __repr__(self):
        return f'<ItemsGasto {self.id}: {self.descripcion_item} - {self.monto_item}>'

# --- Función Auxiliar para Actualizar Estado del Documento ---
def actualizar_estado_documento(documento_id_a_actualizar):
    doc = DocumentosARendir.query.get(documento_id_a_actualizar)
    if not doc or doc.estado_documento == 'Anulado':
        return

    nuevo_estado = doc.estado_documento 
    if doc.monto_total_documento is not None and doc.monto_total_documento > 0:
        suma_items = sum(item.monto_item for item in doc.items if item.monto_item is not None)
        if suma_items == doc.monto_total_documento:
            nuevo_estado = 'Rendido'
        elif 0 < suma_items < doc.monto_total_documento:
            nuevo_estado = 'Parcialmente Rendido'
        elif suma_items == 0:
            nuevo_estado = 'Pendiente'
        elif suma_items > doc.monto_total_documento:
            nuevo_estado = 'Parcialmente Rendido' # O 'Excedido'
            flash(f"Advertencia: La suma de ítems ({suma_items:.2f} bs) para el documento #{doc.numero_documento} excede su monto total ({doc.monto_total_documento:.2f} bs).", "warning")
    else: 
        nuevo_estado = 'Pendiente'

    if doc.estado_documento != nuevo_estado:
        doc.estado_documento = nuevo_estado
        try:
            db.session.commit() # Solo commit si el estado realmente cambió
            flash(f"Estado del Documento #{doc.numero_documento} actualizado a '{nuevo_estado}'.", "info")
        except Exception as e:
            db.session.rollback()
            flash(f"Error al intentar actualizar estado del documento: {str(e)}", "danger")

# 5. --- Definiciones de Rutas ---
# Dentro de app.py
# Dentro de la función hello_world en app.py
# Dentro de app.py

@app.route('/')
def hello_world():
    # 1. Obtener la lista de documentos que están 'Pendiente' O 'Parcialmente Rendido'
    documentos_por_rendir = DocumentosARendir.query.filter(
        or_(
            DocumentosARendir.estado_documento == 'Pendiente',
            DocumentosARendir.estado_documento == 'Parcialmente Rendido'
        )
    ).order_by(DocumentosARendir.fecha_emision.asc()).all() # Ordenamos por los más antiguos primero

    # 2. Contar cuántos son
    num_docs_por_rendir = len(documentos_por_rendir)

    # 3. Calcular la suma de todos los saldos pendientes
    total_saldo_por_rendir = Decimal(0)
    for doc in documentos_por_rendir:
        if doc.monto_total_documento is not None:
            suma_items = sum(item.monto_item for item in doc.items if item.monto_item is not None)
            saldo_individual = doc.monto_total_documento - suma_items
            total_saldo_por_rendir += saldo_individual

    # Pasamos los nuevos datos a la plantilla
    return render_template('index.html', 
                           num_por_rendir=num_docs_por_rendir,
                           saldo_total_por_rendir=total_saldo_por_rendir,
                           documentos_a_revisar=documentos_por_rendir)
# --- CRUD Personal ---
@app.route('/personal')
def listar_personal():
    lista_de_personal = Personal.query.order_by(Personal.nombre_completo).all()
    return render_template('listar_personal.html', personal_lista=lista_de_personal)

@app.route('/personal/nuevo', methods=['GET', 'POST'])
def crear_personal():
    if request.method == 'POST':
        try:
            nueva_persona = Personal(
                nombre_completo=request.form['nombre_completo'],
                documento_identidad=request.form['documento_identidad'],
                cargo=request.form.get('cargo'),
                activo='activo' in request.form
            )
            db.session.add(nueva_persona)
            db.session.commit()
            flash('Persona añadida exitosamente!', 'success')
            return redirect(url_for('listar_personal'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al añadir persona: {str(e)}', 'danger')
    return render_template('nuevo_personal.html')

@app.route('/personal/editar/<int:id>', methods=['GET', 'POST'])
def editar_personal(id):
    persona_a_editar = Personal.query.get_or_404(id)
    if request.method == 'POST':
        try:
            persona_a_editar.nombre_completo = request.form['nombre_completo']
            persona_a_editar.documento_identidad = request.form['documento_identidad']
            persona_a_editar.cargo = request.form.get('cargo')
            persona_a_editar.activo = 'activo' in request.form
            db.session.commit()
            flash('Persona actualizada exitosamente!', 'success')
            return redirect(url_for('listar_personal'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar persona: {str(e)}', 'danger')
    return render_template('editar_personal.html', persona=persona_a_editar)

@app.route('/personal/eliminar/<int:id>', methods=['POST'])
def eliminar_personal(id):
    persona_a_eliminar = Personal.query.get_or_404(id)
    try:
        db.session.delete(persona_a_eliminar)
        db.session.commit()
        flash('Persona eliminada exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar persona: {str(e)}', 'danger')
    return redirect(url_for('listar_personal'))

# --- CRUD ProveedoresServicios ---
@app.route('/proveedores')
def listar_proveedores():
    lista_de_proveedores = ProveedoresServicios.query.order_by(ProveedoresServicios.nombre_proveedor_servicio).all()
    return render_template('listar_proveedores.html', proveedores_lista=lista_de_proveedores)

@app.route('/proveedores/nuevo', methods=['GET', 'POST'])
def crear_proveedor():
    if request.method == 'POST':
        try:
            nuevo_proveedor = ProveedoresServicios(
                nombre_proveedor_servicio=request.form['nombre_proveedor_servicio'],
                tipo_servicio=request.form.get('tipo_servicio'),
                referencia_pago=request.form.get('referencia_pago'),
                activo='activo' in request.form
            )
            db.session.add(nuevo_proveedor)
            db.session.commit()
            flash('Proveedor/Servicio añadido exitosamente!', 'success')
            return redirect(url_for('listar_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al añadir proveedor/servicio: {str(e)}', 'danger')
    return render_template('nuevo_proveedor.html')

@app.route('/proveedores/editar/<int:id>', methods=['GET', 'POST'])
def editar_proveedor(id):
    proveedor_a_editar = ProveedoresServicios.query.get_or_404(id)
    if request.method == 'POST':
        try:
            proveedor_a_editar.nombre_proveedor_servicio = request.form['nombre_proveedor_servicio']
            proveedor_a_editar.tipo_servicio = request.form.get('tipo_servicio')
            proveedor_a_editar.referencia_pago = request.form.get('referencia_pago')
            proveedor_a_editar.activo = 'activo' in request.form
            db.session.commit()
            flash('Proveedor/Servicio actualizado exitosamente!', 'success')
            return redirect(url_for('listar_proveedores'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar proveedor/servicio: {str(e)}', 'danger')
    return render_template('editar_proveedor.html', proveedor=proveedor_a_editar)

@app.route('/proveedores/eliminar/<int:id>', methods=['POST'])
def eliminar_proveedor(id):
    proveedor_a_eliminar = ProveedoresServicios.query.get_or_404(id)
    try:
        db.session.delete(proveedor_a_eliminar)
        db.session.commit()
        flash('Proveedor/Servicio eliminado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar proveedor/servicio: {str(e)}', 'danger')
    return redirect(url_for('listar_proveedores'))

# --- CRUD ConceptosGastoVarios ---
@app.route('/conceptos')
def listar_conceptos():
    lista_de_conceptos = ConceptosGastoVarios.query.order_by(ConceptosGastoVarios.nombre_concepto).all()
    return render_template('listar_conceptos.html', conceptos_lista=lista_de_conceptos)

@app.route('/conceptos/nuevo', methods=['GET', 'POST'])
def crear_concepto():
    if request.method == 'POST':
        try:
            nuevo_concepto = ConceptosGastoVarios(
                nombre_concepto=request.form['nombre_concepto'],
                descripcion_concepto=request.form.get('descripcion_concepto'),
                activo='activo' in request.form
            )
            db.session.add(nuevo_concepto)
            db.session.commit()
            flash('Concepto de gasto añadido exitosamente!', 'success')
            return redirect(url_for('listar_conceptos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al añadir concepto: {str(e)}', 'danger')
    return render_template('nuevo_concepto.html')

@app.route('/conceptos/editar/<int:id>', methods=['GET', 'POST'])
def editar_concepto(id):
    concepto_a_editar = ConceptosGastoVarios.query.get_or_404(id)
    if request.method == 'POST':
        try:
            concepto_a_editar.nombre_concepto = request.form['nombre_concepto']
            concepto_a_editar.descripcion_concepto = request.form.get('descripcion_concepto')
            concepto_a_editar.activo = 'activo' in request.form
            db.session.commit()
            flash('Concepto de gasto actualizado exitosamente!', 'success')
            return redirect(url_for('listar_conceptos'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar concepto: {str(e)}', 'danger')
    return render_template('editar_concepto.html', concepto=concepto_a_editar)

@app.route('/conceptos/eliminar/<int:id>', methods=['POST'])
def eliminar_concepto(id):
    concepto_a_eliminar = ConceptosGastoVarios.query.get_or_404(id)
    try:
        db.session.delete(concepto_a_eliminar)
        db.session.commit()
        flash('Concepto de gasto eliminado exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar concepto: {str(e)}', 'danger')
    return redirect(url_for('listar_conceptos'))

# --- CRUD CategoriasGastoPrincipales ---
@app.route('/categorias')
def listar_categorias():
    lista_de_categorias = CategoriasGastoPrincipales.query.order_by(CategoriasGastoPrincipales.nombre_categoria).all()
    return render_template('listar_categorias.html', categorias_lista=lista_de_categorias)

@app.route('/categorias/nueva', methods=['GET', 'POST'])
def crear_categoria():
    if request.method == 'POST':
        try:
            nueva_categoria = CategoriasGastoPrincipales(
                nombre_categoria=request.form['nombre_categoria'],
                descripcion_categoria=request.form.get('descripcion_categoria'),
                activa='activa' in request.form
            )
            db.session.add(nueva_categoria)
            db.session.commit()
            flash('Categoría añadida exitosamente!', 'success')
            return redirect(url_for('listar_categorias'))
        except Exception as e: 
            db.session.rollback()
            flash(f'Error al añadir categoría: {str(e)}', 'danger')
    return render_template('nueva_categoria.html')

@app.route('/categorias/editar/<int:id>', methods=['GET', 'POST'])
def editar_categoria(id):
    categoria_a_editar = CategoriasGastoPrincipales.query.get_or_404(id)
    if request.method == 'POST':
        try:
            categoria_a_editar.nombre_categoria = request.form['nombre_categoria']
            categoria_a_editar.descripcion_categoria = request.form.get('descripcion_categoria')
            categoria_a_editar.activa = 'activa' in request.form
            db.session.commit()
            flash('Categoría actualizada exitosamente!', 'success')
            return redirect(url_for('listar_categorias'))
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar categoría: {str(e)}', 'danger')
    return render_template('editar_categoria.html', categoria=categoria_a_editar)

@app.route('/categorias/eliminar/<int:id>', methods=['POST'])
def eliminar_categoria(id):
    categoria_a_eliminar = CategoriasGastoPrincipales.query.get_or_404(id)
    try:
        db.session.delete(categoria_a_eliminar)
        db.session.commit()
        flash('Categoría eliminada exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar categoría: {str(e)}', 'danger')
    return redirect(url_for('listar_categorias'))

# --- CRUD DocumentosARendir ---
@app.route('/documentos')
def listar_documentos():
    lista_de_documentos = DocumentosARendir.query.order_by(DocumentosARendir.fecha_emision.desc()).all()
    return render_template('listar_documentos.html', documentos_lista=lista_de_documentos)

@app.route('/documentos/nuevo', methods=['GET', 'POST'])
def crear_documento():
    # Lógica para manejar errores de conversión y renderizar el template con datos previos
    # en caso de error POST, o el formulario vacío en caso de GET.
    if request.method == 'POST':
        try:
            fecha_em_obj = datetime.strptime(request.form['fecha_emision'], '%Y-%m-%d').date()
            monto_doc_val = None
            monto_str = request.form.get('monto_total_documento')
            if monto_str and monto_str.strip():
                monto_doc_val = Decimal(monto_str)

            nuevo_documento = DocumentosARendir(
                tipo_documento=request.form['tipo_documento'],
                numero_documento=request.form['numero_documento'],
                fecha_emision=fecha_em_obj,
                monto_total_documento=monto_doc_val,
                descripcion_general=request.form.get('descripcion_general')
            )
            db.session.add(nuevo_documento)
            db.session.commit()
            flash('Documento añadido exitosamente!', 'success')
            # No llamamos a actualizar_estado_documento aquí porque no tiene ítems aún.
            return redirect(url_for('listar_documentos'))
        except ValueError:
            flash("Error en el formato de fecha. Use YYYY-MM-DD.", 'danger')
        except InvalidOperation:
            flash("Error en el formato del monto.", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al añadir documento: {str(e)}', 'danger')
        # Si hay error, volvemos a mostrar el formulario (GET)
        # (Considerar pasar datos previos para pre-llenar el formulario en caso de error)
    return render_template('nuevo_documento.html')


@app.route('/documentos/editar/<int:id>', methods=['GET', 'POST'])
def editar_documento(id):
    documento_a_editar = DocumentosARendir.query.get_or_404(id)
    if request.method == 'POST':
        try:
            documento_a_editar.tipo_documento = request.form['tipo_documento']
            documento_a_editar.numero_documento = request.form['numero_documento']
            fecha_em_str = request.form['fecha_emision']
            documento_a_editar.fecha_emision = datetime.strptime(fecha_em_str, '%Y-%m-%d').date()
            
            monto_str = request.form.get('monto_total_documento')
            if monto_str and monto_str.strip():
                documento_a_editar.monto_total_documento = Decimal(monto_str)
            else:
                documento_a_editar.monto_total_documento = None
                
            documento_a_editar.descripcion_general = request.form.get('descripcion_general')
            documento_a_editar.estado_documento = request.form['estado_documento']
            
            db.session.commit()
            flash('Documento actualizado exitosamente!', 'success')
            actualizar_estado_documento(documento_a_editar.id) # Llamada crucial aquí
            return redirect(url_for('listar_documentos'))
        except ValueError:
            flash("Error en el formato de fecha. Use YYYY-MM-DD.", 'danger')
        except InvalidOperation:
            flash("Error en el formato del monto.", 'danger')
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar documento: {str(e)}', 'danger')
        # En caso de error, volvemos a renderizar el formulario de edición con los datos actuales del documento
        return render_template('editar_documento.html', documento=documento_a_editar)
    
    # Si es GET
    return render_template('editar_documento.html', documento=documento_a_editar)


@app.route('/documentos/eliminar/<int:id>', methods=['POST'])
def eliminar_documento(id):
    documento_a_eliminar = DocumentosARendir.query.get_or_404(id)
    try:
        # La cascada 'all, delete-orphan' en DocumentosARendir.items debería borrar los ítems.
        db.session.delete(documento_a_eliminar)
        db.session.commit()
        flash('Documento y sus ítems asociados eliminados exitosamente!', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar documento: {str(e)}.', 'danger')
    return redirect(url_for('listar_documentos'))

# --- CRUD ItemsGasto ---
# Dentro de app.py

@app.route('/documento/<int:documento_id>/items')
def ver_documento_items(documento_id):
    documento = DocumentosARendir.query.get_or_404(documento_id)
    items_del_documento = documento.items.order_by(ItemsGasto.fecha_item.asc()).all()

    # --- Calcular suma de ítems y saldo pendiente ---
    suma_items_actual = sum(item.monto_item for item in items_del_documento if item.monto_item is not None)

    saldo_pendiente = None
    if documento.monto_total_documento is not None:
        saldo_pendiente = documento.monto_total_documento - suma_items_actual
    # --- Fin del cálculo ---

    return render_template('ver_documento_items.html', 
                           documento=documento, 
                           items_lista=items_del_documento,
                           suma_items_registrados=suma_items_actual, # <--- Nuevo dato
                           saldo_por_rendir=saldo_pendiente         # <--- Nuevo dato
                          )

@app.route('/documento/<int:documento_id>/item/nuevo', methods=['GET', 'POST'])
def crear_item_gasto(documento_id):
    documento = DocumentosARendir.query.get_or_404(documento_id)
    # Datos para los desplegables
    categorias = CategoriasGastoPrincipales.query.filter_by(activa=True).order_by(CategoriasGastoPrincipales.nombre_categoria).all()
    lista_personal = Personal.query.filter_by(activo=True).order_by(Personal.nombre_completo).all()
    lista_proveedores = ProveedoresServicios.query.filter_by(activo=True).order_by(ProveedoresServicios.nombre_proveedor_servicio).all()
    lista_conceptos = ConceptosGastoVarios.query.filter_by(activo=True).order_by(ConceptosGastoVarios.nombre_concepto).all()
    
    # Cálculo de saldos para mostrar en el formulario
    suma_items_existentes = sum(item.monto_item for item in documento.items if item.monto_item is not None)
    saldo_a_rendir = None
    if documento.monto_total_documento is not None:
        saldo_a_rendir = documento.monto_total_documento - suma_items_existentes
    
    template_context_base = {
        'documento': documento,
        'monto_total_doc': documento.monto_total_documento,
        'suma_ya_rendida': suma_items_existentes,
        'saldo_pendiente': saldo_a_rendir,
        'categorias': categorias,
        'personal_lista': lista_personal,
        'proveedores_lista': lista_proveedores,
        'conceptos_lista': lista_conceptos
    }

    if request.method == 'POST':
        form_data_prev = {
            'descripcion_item_prev': request.form.get('descripcion_item'),
            'monto_item_prev': request.form.get('monto_item'),
            'fecha_item_prev': request.form.get('fecha_item'),
            'categoria_prev': request.form.get('categoria_principal_id'),
            'personal_prev': request.form.get('personal_id'),
            'proveedor_prev': request.form.get('proveedor_servicio_id'),
            'concepto_prev': request.form.get('concepto_gasto_vario_id')
        }
        current_template_context = {**template_context_base, **form_data_prev}

        # --- INICIO DE LA NUEVA VALIDACIÓN ---
        opcionales_seleccionados = [val for val in [form_data_prev['personal_prev'], form_data_prev['proveedor_prev'], form_data_prev['concepto_prev']] if val]
        if len(opcionales_seleccionados) > 1:
            flash('Error: Solo puede seleccionar UN detalle específico (Personal, Proveedor/Servicio, o Concepto Vario), no múltiples.', 'danger')
            return render_template('nuevo_item_gasto.html', **current_template_context)
        # --- FIN DE LA NUEVA VALIDACIÓN ---

        try:
            fecha_item_obj = datetime.strptime(request.form['fecha_item'], '%Y-%m-%d').date()
            monto_nuevo_item_decimal = Decimal(request.form['monto_item'])
            if monto_nuevo_item_decimal <= 0:
                flash("El monto del ítem debe ser un número positivo.", 'danger')
                return render_template('nuevo_item_gasto.html', **current_template_context)
            categoria_id_form = request.form.get('categoria_principal_id')
            if not categoria_id_form or not categoria_id_form.isdigit():
                flash("Debe seleccionar una categoría principal válida.", 'danger')
                return render_template('nuevo_item_gasto.html', **current_template_context)

            if documento.monto_total_documento is not None:
                if (suma_items_existentes + monto_nuevo_item_decimal) > documento.monto_total_documento:
                    flash(f'Error: El monto del nuevo ítem ({monto_nuevo_item_decimal:.2f} bs) haría que la suma exceda el monto del documento ({documento.monto_total_documento:.2f} bs).', 'danger')
                    return render_template('nuevo_item_gasto.html', **current_template_context)
            
            nuevo_item = ItemsGasto(
                documento_id=documento.id,
                categoria_principal_id=int(categoria_id_form),
                descripcion_item=request.form['descripcion_item'],
                monto_item=monto_nuevo_item_decimal,
                fecha_item=fecha_item_obj,
                personal_id=int(form_data_prev['personal_prev']) if form_data_prev['personal_prev'] and form_data_prev['personal_prev'].isdigit() else None,
                proveedor_servicio_id=int(form_data_prev['proveedor_prev']) if form_data_prev['proveedor_prev'] and form_data_prev['proveedor_prev'].isdigit() else None,
                concepto_gasto_vario_id=int(form_data_prev['concepto_prev']) if form_data_prev['concepto_prev'] and form_data_prev['concepto_prev'].isdigit() else None
            )
            db.session.add(nuevo_item)
            db.session.commit()
            actualizar_estado_documento(documento.id)
            flash('Ítem de gasto añadido exitosamente!', 'success')
            return redirect(url_for('ver_documento_items', documento_id=documento.id))
        
        except InvalidOperation:
            flash("Error en el formato del monto del ítem.", 'danger')
            return render_template('nuevo_item_gasto.html', **current_template_context)
        except ValueError:
            flash("Error en el formato de fecha del ítem. Use YYYY-MM-DD.", 'danger')
            return render_template('nuevo_item_gasto.html', **current_template_context)
        except Exception as e:
            db.session.rollback()
            flash(f'Error al guardar el ítem de gasto: {str(e)}', 'danger')
            return render_template('nuevo_item_gasto.html', **current_template_context)
            
    fecha_item_default = documento.fecha_emision.strftime('%Y-%m-%d') if documento.fecha_emision else ''
    return render_template('nuevo_item_gasto.html', 
                           **template_context_base, 
                           fecha_item_prev=fecha_item_default)

@app.route('/item/editar/<int:item_id>', methods=['GET', 'POST'])
def editar_item_gasto(item_id):
    item_a_editar = ItemsGasto.query.get_or_404(item_id)
    documento_padre = item_a_editar.documento
    
    categorias = CategoriasGastoPrincipales.query.filter_by(activa=True).order_by(CategoriasGastoPrincipales.nombre_categoria).all()
    lista_personal = Personal.query.filter_by(activo=True).order_by(Personal.nombre_completo).all()
    lista_proveedores = ProveedoresServicios.query.filter_by(activo=True).order_by(ProveedoresServicios.nombre_proveedor_servicio).all()
    lista_conceptos = ConceptosGastoVarios.query.filter_by(activo=True).order_by(ConceptosGastoVarios.nombre_concepto).all()

    template_context_base_edit = {
        'item': item_a_editar,
        'documento_id': documento_padre.id,
        'categorias': categorias,
        'personal_lista': lista_personal,
        'proveedores_lista': lista_proveedores,
        'conceptos_lista': lista_conceptos
    }

    if request.method == 'POST':
        personal_id_str = request.form.get('personal_id')
        proveedor_id_str = request.form.get('proveedor_servicio_id')
        concepto_id_str = request.form.get('concepto_gasto_vario_id')

        # --- INICIO DE LA NUEVA VALIDACIÓN ---
        opcionales_seleccionados = [val for val in [personal_id_str, proveedor_id_str, concepto_id_str] if val]
        if len(opcionales_seleccionados) > 1:
            flash('Error: Solo puede seleccionar UN detalle específico (Personal, Proveedor/Servicio, o Concepto Vario), no múltiples.', 'danger')
            return render_template('editar_item_gasto.html', **template_context_base_edit)
        # --- FIN DE LA NUEVA VALIDACIÓN ---
        
        try:
            nuevo_monto_item_decimal = Decimal(request.form['monto_item'])
            
            if documento_padre.monto_total_documento is not None:
                suma_otros_items = sum(item.monto_item for item in documento_padre.items if item.id != item_a_editar.id and item.monto_item is not None)
                if (suma_otros_items + nuevo_monto_item_decimal) > documento_padre.monto_total_documento:
                    flash(f'Error: El nuevo monto del ítem ({nuevo_monto_item_decimal:.2f} bs) haría que la suma exceda el monto del documento ({documento_padre.monto_total_documento:.2f} bs).', 'danger')
                    return render_template('editar_item_gasto.html', **template_context_base_edit)
            
            item_a_editar.descripcion_item = request.form['descripcion_item']
            item_a_editar.monto_item = nuevo_monto_item_decimal
            item_a_editar.fecha_item = datetime.strptime(request.form['fecha_item'], '%Y-%m-%d').date()
            item_a_editar.categoria_principal_id = int(request.form.get('categoria_principal_id'))
            item_a_editar.personal_id = int(personal_id_str) if personal_id_str and personal_id_str.isdigit() else None
            item_a_editar.proveedor_servicio_id = int(proveedor_id_str) if proveedor_id_str and proveedor_id_str.isdigit() else None
            item_a_editar.concepto_gasto_vario_id = int(concepto_id_str) if concepto_id_str and concepto_id_str.isdigit() else None
            
            db.session.commit()
            actualizar_estado_documento(documento_padre.id)
            flash('Ítem de gasto actualizado exitosamente!', 'success')
            return redirect(url_for('ver_documento_items', documento_id=documento_padre.id))
        
        except Exception as e:
            db.session.rollback()
            flash(f'Error al actualizar el ítem de gasto: {str(e)}', 'danger')
    
    return render_template('editar_item_gasto.html', **template_context_base_edit)

@app.route('/item/eliminar/<int:item_id>', methods=['POST'])
def eliminar_item_gasto(item_id):
    item_a_eliminar = ItemsGasto.query.get_or_404(item_id)
    documento_id_padre = item_a_eliminar.documento_id
    try:
        db.session.delete(item_a_eliminar)
        db.session.commit()
        actualizar_estado_documento(documento_id_padre)
        flash('Ítem de gasto eliminado exitosamente.', 'success')
    except Exception as e:
        db.session.rollback()
        flash(f'Error al eliminar el ítem de gasto: {str(e)}', 'danger')
    return redirect(url_for('ver_documento_items', documento_id=documento_id_padre))

# 6. Bloque para ejecutar la aplicació
# # Dentro de app.py, junto con tus otras rutas

# --- Ruta para el Informe de Gastos por Categoría ---
# Dentro de app.py

@app.route('/informes/gastos_por_categoria', methods=['GET', 'POST'])
def informe_gastos_por_categoria():
    if request.method == 'POST':
        # Obtener fechas del formulario
        fecha_inicio_str = request.form.get('fecha_inicio')
        fecha_fin_str = request.form.get('fecha_fin')

        # Convertir las fechas de texto a objetos de fecha
        try:
            fecha_inicio = datetime.strptime(fecha_inicio_str, '%Y-%m-%d').date()
            fecha_fin = datetime.strptime(fecha_fin_str, '%Y-%m-%d').date()
        except (ValueError, TypeError):
            flash('Fechas inválidas. Por favor, seleccione un rango de fechas.', 'danger')
            return render_template('informe_gastos_por_categoria.html', resultados=None)

        # --- La Consulta a la Base de Datos ---
        # Seleccionamos el nombre de la categoría y la suma de los montos de los ítems
        # y le ponemos una etiqueta 'total_gastado' a la suma para fácil acceso.
        resultados = db.session.query(
            CategoriasGastoPrincipales.nombre_categoria,
            func.sum(ItemsGasto.monto_item).label('total_gastado')
        ).join( # Unimos la tabla de Ítems con la de Categorías
            ItemsGasto, CategoriasGastoPrincipales.id == ItemsGasto.categoria_principal_id
        ).filter( # Filtramos los ítems que están dentro del rango de fechas
            ItemsGasto.fecha_item.between(fecha_inicio, fecha_fin)
        ).group_by( # Agrupamos los resultados por el nombre de la categoría
            CategoriasGastoPrincipales.nombre_categoria
        ).order_by( # Ordenamos de mayor a menor gasto
            func.sum(ItemsGasto.monto_item).desc()
        ).all()
        # --- Fin de la Consulta ---

        # Calculamos el total general del informe
        total_informe = sum(res.total_gastado for res in resultados)

        # Pasamos los resultados y las fechas de vuelta a la plantilla para mostrarlos
        return render_template('informe_gastos_por_categoria.html', 
                               resultados=resultados, 
                               fecha_inicio=fecha_inicio_str, 
                               fecha_fin=fecha_fin_str,
                               total_informe=total_informe)

    # Si es GET, simplemente mostrar el formulario sin resultados
    return render_template('informe_gastos_por_categoria.html', resultados=None)
# --- Fin Ruta para Informe ---n
if __name__ == '__main__':
    app.run(debug=True)