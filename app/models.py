from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from app import db

# --- MODELO DE SEDE ---


class Sede(db.Model):
    __tablename__ = "sede"
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)  # ej: "Trujillo"
    prefijo = db.Column(db.String(3), unique=True, nullable=False)  # ej: "TR"

    # Conexiones
    users = db.relationship("User", back_populates="sede", lazy="dynamic")
    reservations = db.relationship("Reservation", back_populates="sede", lazy="dynamic")

    def __repr__(self):
        return f"<Sede {self.nombre}>"


# --- Modelo de Autenticación ---
class User(UserMixin, db.Model):
    """Modelo para los colaboradores (Propietario)."""

    __tablename__ = "user"
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), index=True, unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    is_active = db.Column(db.Boolean, default=True)
    sede_id = db.Column(
        db.Integer, db.ForeignKey("sede.id"), nullable=True
    )  # Nullable=True para super-admins
    sede = db.relationship("Sede", back_populates="users")

    is_admin = db.Column(db.Boolean, default=False)

    reservations = db.relationship(
        "Reservation", back_populates="propietario", lazy="dynamic"
    )
    payments = db.relationship("Payment", back_populates="propietario", lazy="dynamic")

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


def load_user(user_id):
    return db.session.get(User, int(user_id))


# --- Modelos de Negocio ---


class Reservation(db.Model):
    """Modelo para la tabla de Reservas (ReservasBD.csv)."""

    __tablename__ = "reservation"

    id = db.Column(db.Integer, primary_key=True)  # Reemplaza 'ID' de Wix
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )  # Reemplaza 'Fecha de creación'
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )  # Reemplaza 'Actualización'
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # Reemplaza 'Propietario'
    propietario = db.relationship("User", back_populates="reservations")

    sede_id = db.Column(
        db.Integer, db.ForeignKey("sede.id"), nullable=False, index=True
    )
    sede = db.relationship("Sede", back_populates="reservations")

    # Campos de tu CSV (mapeados)
    codigo_reserva = db.Column(db.String(20), unique=True, nullable=False, index=True)
    nombre_padres = db.Column(db.String(200), nullable=False)
    telefono = db.Column(db.String(20), nullable=False)
    nombre_cumpleanero = db.Column(db.String(200))
    dni_padres = db.Column(db.String(15))
    correo = db.Column(db.String(120), index=True)
    fecha_celebracion = db.Column(
        db.DateTime, nullable=False, index=True
    )  # Mapeado de 'Fecha de Reserva'
    modalidad = db.Column(db.String(100), nullable=False)
    paquete = db.Column(db.String(100))
    horario = db.Column(db.String(50))
    salon = db.Column(db.String(50))
    ninos = db.Column(db.Integer)
    adultos = db.Column(db.Integer)
    accesorios = db.Column(db.Text)
    adicionales = db.Column(db.Text)
    comentarios = db.Column(db.Text)
    estado = db.Column(db.String(50), nullable=False, default="Reservado", index=True)
    total = db.Column(db.Numeric(10, 2), default=0.00)

    payments = db.relationship(
        "Payment",
        back_populates="reservation",
        lazy="dynamic",
        cascade="all, delete-orphan",
    )


class Payment(db.Model):
    """Modelo para la tabla de Abonos (AbonosBD.csv)."""

    __tablename__ = "payment"

    id = db.Column(db.Integer, primary_key=True)  # Reemplaza 'ID' de Wix
    created_at = db.Column(
        db.DateTime, default=datetime.utcnow
    )  # Reemplaza 'Fecha de creación'
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow
    )  # Reemplaza 'Actualización'
    user_id = db.Column(db.Integer, db.ForeignKey("user.id"))  # Reemplaza 'Propietario'
    propietario = db.relationship("User", back_populates="payments")

    reservation_id = db.Column(
        db.Integer, db.ForeignKey("reservation.id"), nullable=False, index=True
    )
    reservation = db.relationship("Reservation", back_populates="payments")

    # Campos de tu CSV (mapeados)
    codigo_reserva_str = db.Column(
        db.String(20), index=True
    )  # 'Código de Reserva' (para referencia)
    fecha_abono = db.Column(db.Date, nullable=False, index=True)
    metodo_pago = db.Column(db.String(50), nullable=False)
    monto = db.Column(db.Numeric(10, 2), nullable=False)
    referencia = db.Column(db.String(100))  # 'Referencia' (Nro. Operación del mockup)
    modalidad = db.Column(db.String(100))
    comentarios = db.Column(db.Text)


class Adicional(db.Model):
    """Modelo para los Adicionales (extras) de las reservas."""

    __tablename__ = "adicionales"

    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(100), unique=True, nullable=False)
    precio = db.Column(
        db.Numeric(10, 2), nullable=False
    )  # Numeric es ideal para dinero

    def __repr__(self):
        return f"<Adicional {self.nombre} | S/ {self.precio}>"
