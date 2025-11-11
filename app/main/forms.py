"""
Formularios (Flask-WTF) para los modales,
adaptados a los campos de tu CSV y los mockups.
"""

from flask_wtf import FlaskForm
from wtforms import (
    DateField,
    DecimalField,
    RadioField,
    SelectField,
    StringField,
    SubmitField,
    TextAreaField,
)
from wtforms.fields import TelField
from wtforms.validators import (
    DataRequired,
    Email,
    Length,
    NumberRange,
    Optional,
    ValidationError,
)


class ReservationForm(FlaskForm):
    """Formulario para el modal de Nueva Reserva (CSV + mockup image_3e5282.png)."""

    # Mapeados de CSV y Mockup
    nombre_padres = StringField(
        "Nombre y Apellidos (Padres):", validators=[DataRequired()]
    )
    correo = StringField("Correo:", validators=[Optional(), Email()])
    telefono = TelField("Teléfono:", validators=[DataRequired(), Length(min=7, max=15)])
    dni_padres = StringField(
        "DNI (Padres):", validators=[Optional(), Length(min=8, max=15)]
    )

    # Campo "Cumpleañero / Edad" del mockup
    nombre_cumpleanero = StringField("Cumpleañero / Edad:", validators=[DataRequired()])

    fecha_celebracion = DateField(
        "Fecha de Celebración:", validators=[DataRequired()], format="%Y-%m-%d"
    )

    # Modalidad (del mockup)
    modalidad = RadioField(
        "Modalidad:",
        choices=[
            ("Exclusivo", "Exclusivo"),
            ("Paquete LUDI", "Paquete LUDI"),
            ("NUEVO Paquete LUDI", "NUEVO Paquete LUDI"),
            ("Paquete JESSI", "Paquete JESSI"),
            ("Paquete LUDI SUPER ESTRELLA", "Paquete LUDI SUPER ESTRELLA"),
        ],
        validators=[DataRequired(message="Debe seleccionar una modalidad.")],
    )

    estado = SelectField(
        "Estado:",
        choices=[
            ("Reservado", "Reservado"),
            ("Abonado", "Abonado"),
            ("Cancelado", "Cancelado"),
        ],
        validators=[DataRequired()],
    )

    # Campos adicionales del CSV y Mockup
    accesorios = TextAreaField("Accesorios:", validators=[Optional()])
    comentarios = TextAreaField("Comentarios:", validators=[Optional()])
    total = DecimalField(
        "Monto Total (TOTAL):", validators=[Optional(), NumberRange(min=0)]
    )

    # Botón de envío del modal
    submit = SubmitField("Reservar")


# Validador personalizado para el SelectField de Abonos
def must_be_valid_reservation(form, field):
    """Asegura que el valor seleccionado no sea el placeholder '0'."""
    if field.data == 0:
        raise ValidationError("Debe seleccionar una reserva válida.")


class PaymentForm(FlaskForm):
    """Formulario para el modal de Nuevo Abono (CSV + mockup image_3e59a3.png)."""

    # 'Código de Reserva' del mockup
    # Usamos SelectField, se poblará dinámicamente en la ruta
    reservation_id = SelectField(
        "Código de Reserva:",
        coerce=int,
        validators=[
            DataRequired(message="Debe seleccionar una reserva."),
            must_be_valid_reservation,
        ],
    )

    # 'Modalidad' (se autocompleta)
    modalidad = StringField(
        "Modalidad:", validators=[Optional()], render_kw={"readonly": True}
    )

    # 'Boleta, Factura y/o Nro. de Operación' del mockup (mapeado a 'Referencia' del CSV)
    referencia = StringField(
        "Boleta, Factura y/o Nro. de Operación (Referencia):", validators=[Optional()]
    )

    # 'Método de pago' del mockup
    metodo_pago = SelectField(
        "Método de pago:",
        choices=[
            ("", "-- Seleccionar --"),
            ("Efectivo", "Efectivo"),
            ("Yape/Plin", "Yape/Plin"),
            ("Transferencia", "Transferencia"),
            ("Tarjeta", "Tarjeta"),
        ],
        validators=[DataRequired(message="Debe seleccionar un método de pago.")],
    )

    # 'Monto' del mockup
    monto = DecimalField("Monto:", validators=[DataRequired(), NumberRange(min=0.01)])

    comentarios = TextAreaField("Comentarios:", validators=[Optional()])

    submit = SubmitField("Abonar")
