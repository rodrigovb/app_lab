import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address # <-- Asegúrate que esto esté importado

# --- Creación de la App (Patrón Factory) ---
app = Flask(__name__)

# --- Lógica de "Secrets" (Solo Producción) ---
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')

# ... (tus verificaciones) ...

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Inicializar extensiones
db = SQLAlchemy(app)

# --- CORRECCIÓN AQUÍ ---
limiter = Limiter(
    get_remote_address,  # 1. Pasa 'get_remote_address' como primer argumento
    app=app,             # 2. Pasa 'app' usando su nombre (keyword)
    default_limits=["100 per hour", "20 per minute"]
)
# --- FIN DE LA CORRECCIÓN ---

# Importar modelos y rutas al final
from app import routes, models
