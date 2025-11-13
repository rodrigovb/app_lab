import os
import keyring
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# --- Lógica Híbrida de "Secrets" ---
KEYRING_SERVICE_NAME = "flask-certificados"

def get_secret(key_name):
    """
    Intenta obtener el secret desde el keyring local.
    Si falla, lo busca en las variables de entorno (para producción).
    """
    secret = keyring.get_password(KEYRING_SERVICE_NAME, key_name)
    if secret is None:
        secret = os.environ.get(key_name)
    return secret

# --- Creación de la App (Patrón Factory) ---
app = Flask(__name__)

# Configurar "secrets"
app.config['SECRET_KEY'] = get_secret('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = get_secret('DATABASE_URL')

if not app.config['SECRET_KEY'] or not app.config['SQLALCHEMY_DATABASE_URI']:
    print("ADVERTENCIA: SECRET_KEY o DATABASE_URL no están configuradas.")
    print("Asegúrate de guardarlas en keyring localmente o en variables de entorno en producción.")

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
