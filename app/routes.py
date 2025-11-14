import os
import io
from flask import (
    render_template, request, send_file, 
    flash, redirect, url_for, current_app
)
from app import app, db, limiter
from app.models import InscriptosTable  # Importamos el modelo de la tabla
from app.utils import generate_pdf_in_memory

@app.route('/')
def homepage():
    """
    Muestra la homepage con la grilla de eventos y el buscador.
    Busca en la tabla 'inscriptostable' los nombres de eventos únicos.
    """
    search_query = request.args.get('q')
    
    # Inicia una consulta para obtener nombres de eventos ÚNICOS (distinct)
    query = db.session.query(InscriptosTable.evento).distinct()

    if search_query:
        # Si hay un término de búsqueda, filtra los eventos
        query = query.filter(InscriptosTable.evento.ilike(f'%{search_query}%'))

    # Ejecuta la consulta y ordena
    # query.all() devuelve una lista de tuplas, ej: [('Kavacon 2023',), ('Kavacon 2024',)]
    eventos_tuplas = query.order_by(InscriptosTable.evento.desc()).all()
    
    # Aplanamos la lista de tuplas a una lista simple de strings
    eventos = [item[0] for item in eventos_tuplas if item[0]] # Ignora 'None'

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
    # Pasamos el nombre del evento (desde la URL) a la plantilla
    return render_template('evento_page.html', evento_nombre=evento_nombre)


@app.route('/generar/<string:evento_nombre>', methods=['POST'])
@limiter.limit("5 per minute; 20 per hour") # Límite de Rate Limiting
def generar_certificado(evento_nombre):
    """
    Busca al asistente por email Y por evento, y genera el PDF.
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
        # Redirige de vuelta a la página del formulario
        return redirect(url_for('pagina_evento', evento_nombre=evento_nombre))

    # 3. Generar el PDF
    nombre_completo = asistente.nombre_completo
    template_img_path = "img/certificado.png" # Usamos la plantilla genérica
    
    try:
        image_path = os.path.join(current_app.root_path, 'static', template_img_path)
        if not os.path.exists(image_path):
            raise FileNotFoundError
            
        buffer_pdf = generate_pdf_in_memory(nombre_completo, image_path)
        
    except FileNotFoundError:
        flash(f"Error del servidor: No se encontró el archivo de plantilla '{template_img_path}'.")
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
