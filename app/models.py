from app import db

# Este modelo le dice a SQLAlchemy cómo "ver" tu tabla 'inscriptostable'
class InscriptosTable(db.Model):
    __tablename__ = 'inscriptostable'
    
    # Define las columnas para que coincidan con tu DBeaver
    nro_pedido = db.Column(db.BigInteger, primary_key=True) 
    nombre = db.Column(db.String)
    apellido = db.Column(db.String)
    email = db.Column(db.String, index=True)
    na = db.Column(db.String)
    filename = db.Column(db.String)
    
    # --- COLUMNA FALTANTE AÑADIDA AQUÍ ---
    evento = db.Column(db.String, index=True) # Añadimos índice para búsquedas rápidas

    # Propiedad útil para obtener el nombre completo
    @property
    def nombre_completo(self):
        # Combina las columnas 'nombre' y 'apellido'
        return f"{self.nombre} {self.apellido}"
