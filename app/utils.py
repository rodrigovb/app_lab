import io
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import landscape, A4
from reportlab.lib.utils import ImageReader

def generate_pdf_in_memory(texto_nombre, full_image_path):
    """
    Genera el PDF en un buffer de memoria en lugar de un archivo.
    """
    buffer = io.BytesIO()

    # Usamos A4 landscape (841.89, 595.27) como base
    page_width, page_height = landscape(A4)
    
    pdf = canvas.Canvas(buffer, pagesize=landscape(A4))
    pdf.setTitle('Certificado de Asistencia')

    # Dibuja la imagen de fondo (desde la ruta completa)
    try:
        pdf.drawImage(ImageReader(full_image_path), 0, 0, width=page_width, height=page_height, preserveAspectRatio=False, anchor='c')
    except Exception as e:
        print(f"Error al dibujar imagen en PDF: {e}")
        # Manejo de error básico: escribe el nombre si la imagen falla
        pdf.drawString(50, page_height / 2, f"Error al cargar plantilla. Certificado para: {texto_nombre}")
        pdf.save()
        buffer.seek(0)
        return buffer

    # Configuración de la fuente (ajusta esto a tu plantilla)
    pdf.setFont("Courier-Bold", 30)
    pdf.setFillColorRGB(0, 0, 0) # Color negro

    # Centrar el texto (ajusta 'y_position' verticalmente)
    y_position = (page_height / 2) - 20
    pdf.drawCentredString(page_width / 2, y_position, texto_nombre)

    pdf.save()
    
    # Regresa el buffer al inicio para que pueda ser leído
    buffer.seek(0)
    return buffer
