import os
import io
from flask import (
    render_template, request, send_file, 
    flash, redirect, url_for, current_app
)
from app import app, db, limiter
from app.models import InscriptosTable
from app.utils import generate_pdf_in_memory

@app.route('/')
def homepage():
    """
    Muestra la homepage con la grilla de eventos y el buscador.
    Busca en la tabla 'inscriptostable' los nombres de eventos únicos.
    """
    search_query = request.args.get('q')
    
    query = db.session.query(InscriptosTable.evento).distinct()

    if search_query:
        query = query.filter(InscriptosTable.evento.ilike(f'%{search_query}%'))

    eventos_tuplas = query.order_by(InscriptosTable.evento.desc()).all()
    eventos = [item[0] for item in eventos_tuplas if item[0]]

    return render_template(
        'homepage.html', 
        eventos=eventos, 
        search_query=search_query
    )

@app.route('/evento/<string:evento_nombre>')
def pagina_evento(evento_nombre):
    """
    Muestra la página de un evento específico con el formulario.
    """
    return render_template('evento_page.html', evento_nombre=evento_nombre)


@app.route('/generar/<string:evento_nombre>', methods=['POST'])
@limiter.limit("5 per minute; 20 per hour")
def generar_certificado(evento_nombre):
    """
    Busca al asistente por email Y por evento, y genera el PDF.
    Usa una plantilla de certificado dinámica basada en el nombre del evento.
    """
    email_ingresado = request.form['email']

    # 1. BUSCAMOS POR EMAIL Y POR NOMBRE DE EVENTO
    asistente = InscriptosTable.query.filter_by(
        email=email_ingresado,
        evento=evento_nombre
    ).first()

    # 2. Validar
    if not asistente:
        flash(f'Email no encontrado para el evento "{evento_nombre}". Verifica que esté escrito correctamente.')
        return redirect(url_for('pagina_evento', evento_nombre=evento_nombre))

    # 3. Generar el PDF
    nombre_completo = asistente.nombre_completo

    # --- INICIO: LÓGICA DE PLANTILLA DINÁMICA ---
    
    # 1. Convertir el nombre del evento a un nombre de archivo seguro
    # Ej: "Kavacon 2025" -> "kavacon_2025"
    # Ej: "OWASP PY Web Quiz 2025" -> "owasp_py_web_quiz_2025"
    safe_event_name = evento_nombre.lower().replace(' ', '_').replace('-', '_')
    
    # 2. Construir el nombre del archivo de plantilla
    template_filename = f"template_{safe_event_name}.png"

    # 3. Definir la ruta relativa de la plantilla (dentro de static/)
    template_img_path = os.path.join("img", template_filename)
    
    # --- FIN: LÓGICA DE PLANTILLA DINÁMICA ---
    
    try:
        # Construir la ruta completa al archivo
        image_path = os.path.join(current_app.root_path, 'static', template_img_path)
        
        if not os.path.exists(image_path):
            # Si el archivo no existe, lanzar un error claro
            raise FileNotFoundError(f"No se encontró el archivo de plantilla: {template_filename}")
            
        buffer_pdf = generate_pdf_in_memory(nombre_completo, image_path)
        
    except FileNotFoundError as e:
        flash(f"Error del servidor: {e}") # Muestra el error (ej. "No se encontró...")
        return redirect(url_for('pagina_evento', evento_nombre=evento_nombre))
    except Exception as e:
        flash(f"Error al generar el PDF: {e}")
        return redirect(url_for('pagina_evento', evento_nombre=evento_nombre))

    # 4. Enviar el archivo al navegador
    nombre_archivo_descarga = f"Certificado_{nombre_completo.replace(' ', '_')}.pdf"
    
    return send_file(
        buffer_pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=nombre_archivo_descarga
    )
