import logging
from logging.config import fileConfig
from sqlalchemy import create_engine # Asegúrate de que esta importación esté
from flask import current_app # Asegúrate de que esta importación esté
from alembic import context
import os # Asegúrate de que esta importación esté
# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
# Interpret the config file for Python logging.
fileConfig(config.config_file_name)
logger = logging.getLogger('alembic.env')
# IMPORTANTE: No debe haber asignaciones de variables de entorno como FLASK_SECRET_KEY=valor_aqui
# en este archivo, excepto si las lees con os.environ.get() o config.get_main_option().
# Si la línea 25 es 'FLASK_SECRET_KEY=...', ELIMÍNALA.
# Importa tu aplicación Flask y la instancia de db
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))) # Ruta más robusta
from app import app, db # <--- Importa app y db
target_metadata = db.metadata # Usa el metadata de tu instancia de db
# --- CAMBIO CLAVE: Asegurarse de que la URL de la base de datos se obtenga correctamente ---
# Priorizar la variable de entorno DATABASE_URL
DATABASE_URL = os.environ.get('DATABASE_URL') # activar en produccion 
#DATABASE_URL="mysql+pymysql://root:@localhost:3306/gestor_gastos_db" # desactivar en produccion

if DATABASE_URL:
    config.set_main_option("sqlalchemy.url", DATABASE_URL)
else:
    # Si DATABASE_URL no está en el entorno (lo cual NO debería pasar si .env funciona),
    # Alembic usará la URL de alembic.ini, que suele ser una conexión de desarrollo.
    logger.warning("DATABASE_URL no encontrada en el entorno al ejecutar migraciones. Usando la de alembic.ini (podría ser de desarrollo/root).")
def get_metadata():
    # Usamos db.metadata directamente ya que importamos la instancia 'db'
    return db.metadata
def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url, target_metadata=get_metadata(), literal_binds=True
    )
    with context.begin_transaction():
        context.run_migrations()

def run_migrations_online():
    """Run migrations in 'online' mode."""
    # Obtener la URL del config (que ya debería haber sido seteada por DATABASE_URL)
    connectable_url = config.get_main_option("sqlalchemy.url")
    # Si por alguna razón la URL aún es None, eso indica un problema con la carga de la variable.
    if connectable_url is None:
        raise Exception("SQLALCHEMY_DATABASE_URI no está configurada para las migraciones. Asegura que DATABASE_URL está definida en .env o en el entorno.")
    logger.info(f"DEBUG ENV.PY: Migrando con URL: {connectable_url}")
    connectable = create_engine(connectable_url) # Crear el motor con la URL obtenida
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=get_metadata()
            # No se necesita conf_args aquí a menos que tengas directivas personalizadas
        )
        with context.begin_transaction():
            context.run_migrations()
if context.is_offline_mode():
    run_migrations_offline()
else:
    # Asegúrate de que Flask esté en el contexto de la aplicación para que db y app.config estén disponibles.
    # Alembic lo maneja automáticamente con Flask-Migrate, pero es bueno ser explícito.
    with app.app_context():
