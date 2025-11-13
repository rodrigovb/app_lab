from app import db

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), nullable=False, unique=True)
    fecha = db.Column(db.String(50))
    template_img = db.Column(db.String(100), nullable=False, default='certificado.png')
    afiche_img = db.Column(db.String(100), nullable=True) # ej: 'afiches/evento.jpg'
    
    # Relación: Un evento tiene muchos asistentes
    asistentes = db.relationship('Asistente', backref='evento', lazy=True)

    def __repr__(self):
        return f'<Evento {self.nombre}>'

class Asistente(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nro_pedido = db.Column(db.String(50), nullable=True) # Nro de pedido
    nombre_completo = db.Column(db.String(200), nullable=False)
    email = db.Column(db.String(120), nullable=False)
    filename_ref = db.Column(db.String(255)) # Tu 'filename'
    
    # Clave foránea para la relación
    evento_id = db.Column(db.Integer, db.ForeignKey('evento.id'), nullable=False)

    def __repr__(self):
        return f'<Asistente {self.nombre_completo}>'
