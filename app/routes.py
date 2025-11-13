import os
import io
from flask import (
    render_template, request, send_file, 
    flash, redirect, url_for, current_app
)
from app import app, db, limiter
from app.models import Evento, Asistente
from app.utils import generate_pdf_in_memory

@app.route('/')
def homepage():
    """Muestra la homepage con la grilla de eventos y el buscador."""
    search_query = request.args.get('q')

    if search_query:
        # Búsqueda .ilike() (case-insensitive)
        eventos = Evento.query.filter(
            Evento.nombre.ilike(f'%{search_query}%')
        ).order_by(Evento.fecha.desc()).all()
    else:
        # Sin búsqueda, mostrar todos
        eventos = Evento.query.order_by(Evento.fecha.desc()).all()

    return render_template(
        'homepage.html', 
        eventos=eventos, 
        search_query=search_query
    )

@app.route('/evento/<int:event_id>')
def pagina_evento(event_id):
    """Muestra la página de un evento específico con el formulario."""
    evento = Evento.query.get_or_404(event_id)
    return render_template('evento_page.html', evento=evento)

@app.route('/generar/<int:event_id>', methods=['POST'])
@limiter.limit("5 per minute; 20 per hour") # Límite de Rate Limiting
def generar_certificado(event_id):
    """
    Busca al asistente por email y genera el PDF si lo encuentra.
    """
    evento = Evento.query.get_or_404(event_id)
    email_ingresado = request.form['email']

    # 1. Buscar al asistente en la BD
    asistente = Asistente.query.filter_by(
        evento_id=evento.id, 
        email=email_ingresado
    ).first()

    # 2. Validar
    if not asistente:
        flash('Email no encontrado para este evento. Verifica que lo hayas escrito correctamente.')
        return redirect(url_for('pagina_evento', event_id=evento.id))

    # 3. Generar el PDF en memoria
    nombre_completo = asistente.nombre_completo
    
    # Construir la ruta completa a la imagen de plantilla
    try:
        image_path = os.path.join(current_app.root_path, 'static', evento.template_img)
        if not os.path.exists(image_path):
            raise FileNotFoundError
            
        buffer_pdf = generate_pdf_in_memory(nombre_completo, image_path)
        
    except FileNotFoundError:
        flash(f"Error del servidor: No se encontró el archivo de plantilla '{evento.template_img}'.")
        return redirect(url_for('pagina_evento', event_id=evento.id))
    except Exception as e:
        flash(f"Error al generar el PDF: {e}")
        return redirect(url_for('pagina_evento', event_id=evento.id))

    # 4. Enviar el archivo al navegador
    nombre_archivo_descarga = f"Certificado_{nombre_completo.replace(' ', '_')}.pdf"
    
    return send_file(
        buffer_pdf,
        mimetype='application/pdf',
        as_attachment=True,
        download_name=nombre_archivo_descarga
    )
