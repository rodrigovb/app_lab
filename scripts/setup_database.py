import pandas as pd
import sys
import os

# Añade la carpeta raíz (app_lab) al path para que podamos importar 'app'
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

try:
    from app import app, db
    from app.models import Evento, Asistente
except ImportError:
    print("Error: No se pudo importar 'app'. Asegúrate de correr este script desde la raíz (app_lab/).")
    print("Ejemplo: python scripts/setup_database.py")
    sys.exit(1)

# --- Configuración ---
CSV_FILE_PATH = "InscriptosTest--original.csv"
EVENTO_NOMBRE = "Kavacon 2023"
EVENTO_FECHA = "2023-10-25" # (Puedes cambiar esto)
EVENTO_TEMPLATE_IMG = "certificado.png"
EVENTO_AFICHE_IMG = "afiches/kavacon_2023.jpg" # (Nombra tu afiche así)


def load_data():
    """
    Crea las tablas y carga los datos del CSV en la BD.
    """
    # Usa el contexto de la app para conectar a la BD
    with app.app_context():
        print("Creando todas las tablas (si no existen)...")
        db.create_all()

        # 1. Crear o encontrar el Evento
        evento = Evento.query.filter_by(nombre=EVENTO_NOMBRE).first()
        if not evento:
            print(f"Creando evento: {EVENTO_NOMBRE}")
            evento = Evento(
                nombre=EVENTO_NOMBRE,
                fecha=EVENTO_FECHA,
                template_img=EVENTO_TEMPLATE_IMG,
                afiche_img=EVENTO_AFICHE_IMG
            )
            db.session.add(evento)
            db.session.commit()
        else:
            print(f"Evento '{EVENTO_NOMBRE}' ya existe.")

        # 2. Leer el CSV y cargar Asistentes
        try:
            df = pd.read_csv(CSV_FILE_PATH, sep=";", encoding='latin-1')
            print(f"CSV leído. Se encontraron {len(df)} registros.")
        except FileNotFoundError:
            print(f"Error: No se encontró el archivo '{CSV_FILE_PATH}' en la raíz del proyecto.")
            return

        print("Cargando asistentes (esto puede tardar)...")
        nuevos_asistentes = 0
        for _, row in df.iterrows():
            email = row['Email']
            if not isinstance(email, str) or '@' not in email:
                print(f"Saltando registro sin email válido: {row['Nro de pedido']}")
                continue

            # Revisar si el asistente ya existe PARA ESTE EVENTO
            existe = Asistente.query.filter_by(
                email=email, 
                evento_id=evento.id
            ).first()

            if not existe:
                asistente = Asistente(
                    nro_pedido=str(row['Nro de pedido']),
                    nombre_completo=f"{row['Nombre']} {row['Apellido']}",
                    email=email,
                    filename_ref=row['filename'],
                    evento=evento
                )
                db.session.add(asistente)
                nuevos_asistentes += 1
        
        # Guardar todos los nuevos asistentes en la BD
        db.session.commit()
        print(f"¡Carga completada! Se agregaron {nuevos_asistentes} nuevos asistentes.")

if __name__ == "__main__":
    load_data()
