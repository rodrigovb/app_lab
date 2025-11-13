import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Creación de la App (Patrón Factory) ---
app = Flask(__name__)

# --- Lógica de "Secrets" (Solo Producción) ---
# Lee las variables directamente del entorno de Render.
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# Verificación de que las variables existen en Render
if not app.config['SECRET_KEY']:
    print("ADVERTENCIA: La variable de entorno 'SECRET_KEY' no está configurada.")
if not app.config['SQLALCHEMY_DATABASE_URI']:
    print("ADVERTENCIA: La variable de entorno 'DATABASE_URL' no está configurada.")

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db = SQLAlchemy(app)
limiter = Limiter(
    app,
    key_func=get_remote_address,
    default_storage="memory://",
    default_limits=["100 per hour", "20 per minute"]
)

# Importar modelos y rutas al final para evitar importaciones circulares
from app import routes, models
