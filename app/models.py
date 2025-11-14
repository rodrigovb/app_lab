from app import db

# Este modelo le dice a SQLAlchemy cómo "ver" tu tabla 'inscriptostable'
# que ya existe en CockroachDB.
class InscriptosTable(db.Model):
    __tablename__ = 'inscriptostable'
    
    # Define las columnas para que coincidan con tu imagen de DBeaver
    # Necesitamos una Llave Primaria (Primary Key) para que SQLAlchemy funcione.
    nro_pedido = db.Column(db.BigInteger, primary_key=True) 
    nombre = db.Column(db.String)
    apellido = db.Column(db.String)
    email = db.Column(db.String, index=True) # Ponemos un índice para búsquedas rápidas
    na = db.Column(db.String)
    filename = db.Column(db.String)

    # Propiedad útil para obtener el nombre completo
    @property
    def nombre_completo(self):
        # Combina las columnas 'nombre' y 'apellido'
        return f"{self.nombre} {self.apellido}"
