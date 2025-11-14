import os
import io
from flask import (
    render_template, request, send_file, 
    flash, redirect, url_for, current_app
)
from app import app, db, limiter
from app.models import InscriptosTable  # <-- Importa el modelo correcto
from app.utils import generate_pdf_in_memory

@app.route('/', methods=['GET', 'POST'])
@limiter.limit("5 per minute; 20 per hour") # Protege la ruta principal
def homepage():
    """
    Página principal de la app.
    - GET: Muestra el formulario para ingresar el email.
    - POST: Busca el email y genera el certificado.
    """
    
    # Si el usuario envía el formulario (método POST)
    if request.method == 'POST':
        email_ingresado = request.form['email']
        
        # 1. Busca en 'InscriptosTable' por email
        asistente = InscriptosTable.query.filter_by(email=email_ingresado).first()

        # 2. Validar
        if not asistente:
            flash('Email no encontrado. Verifica que lo hayas escrito correctamente.')
            return redirect(url_for('homepage')) # Recarga la página

        # 3. Generar el PDF
        nombre_completo = asistente.nombre_completo # Usa la propiedad del modelo
        
        # --- RUTA DE IMAGEN ACTUALIZADA ---
        # Apunta a la nueva carpeta app/static/img/
        template_img_path = "img/certificado.png" 
        
        try:
            # Construye la ruta completa al archivo de plantilla
            image_path = os.path.join(current_app.root_path, 'static', template_img_path)
            if not os.path.exists(image_path):
                raise FileNotFoundError
                
            buffer_pdf = generate_pdf_in_memory(nombre_completo, image_path)
            
        except FileNotFoundError:
            flash(f"Error del servidor: No se encontró el archivo de plantilla '{template_img_path}'.")
            return redirect(url_for('homepage'))
        except Exception as e:
            flash(f"Error al generar el PDF: {e}")
            return redirect(url_for('homepage'))

        # 4. Enviar el archivo al navegador
        nombre_archivo_descarga = f"Certificado_{nombre_completo.replace(' ', '_')}.pdf"
        
        return send_file(
            buffer_pdf,
            mimetype='application/pdf',
            as_attachment=
