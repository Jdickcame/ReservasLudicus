"""
Formularios (Flask-WTF) para los modales.
"""

from flask_wtf import FlaskForm
from wtforms import (
    BooleanField,
    DateField,
    DecimalField,
    HiddenField,
    IntegerField,
    PasswordField,
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
    Regexp,
    ValidationError,
)


class ReservationForm(FlaskForm):
    """Formulario para el modal de Nueva Reserva."""

    sede_seleccionada = HiddenField("Sede", validators=[Optional()])
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
            ("Paquete JESSI", "Paquete JESSI"),
            ("Paquete LUDI SUPER ESTRELLA", "Paquete LUDI SUPER ESTRELLA"),
        ],
        validators=[DataRequired(message="Debe seleccionar una modalidad.")],
    )

    salon = RadioField(
        "Salón",
        choices=[("Salón 1", "Salón 1"), ("Salón 2", "Salón 2")],
        validators=[Optional()],  # Opcional, porque no siempre es visible
    )

    horario = SelectField(
        "Horario",
        choices=[],  # Vacío, se llenará con JavaScript
        validators=[Optional()],
        validate_choice=False,
    )

    paquete = SelectField(
        "Paquete",
        choices=[],  # Vacío, se llenará con JavaScript
        validators=[Optional()],
        validate_choice=False,
    )

    ninos = IntegerField(
        "Niños *",
        # Dejamos el 'min=0' aquí; el JS pondrá el mínimo real
        validators=[
            DataRequired(message="Debe indicar el N° de niños."),
            NumberRange(min=0),
        ],
        default=0,
    )

    adultos = IntegerField(
        "Adultos *",
        validators=[
            DataRequired(message="Debe indicar el N° de adultos."),
            NumberRange(min=0),
        ],
        default=0,
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

    # === AÑADIR ESTE CAMPO ===
    # Usará la columna 'adicionales' de tu modelo para guardar el JSON
    adicionales = HiddenField("Adicionales")

    comentarios = TextAreaField("Comentarios:", validators=[Optional()])
    total = DecimalField(
        "Monto Total (TOTAL):",
        validators=[Optional(), NumberRange(min=0)],
        render_kw={"readonly": True},
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


class AdicionalForm(FlaskForm):
    """Formulario para crear y editar Adicionales en el panel de admin."""

    nombre = StringField(
        "Nombre del Adicional", validators=[DataRequired(), Length(min=3, max=100)]
    )
    precio = DecimalField(
        "Precio (S/.)",
        validators=[DataRequired(message="El precio es requerido.")],
        places=2,  # Para aceptar 2 decimales
    )
    submit = SubmitField("Guardar")


class SedeForm(FlaskForm):
    """Formulario para crear y editar Sedes."""

    nombre = StringField(
        "Nombre de la Sede", validators=[DataRequired(), Length(min=3, max=100)]
    )
    prefijo = StringField(
        "Prefijo (2 o 3 letras)",
        validators=[
            DataRequired(),
            Length(min=2, max=3, message="El prefijo debe tener 2 o 3 letras."),
            Regexp("^[A-Z]+$", message="Solo letras mayúsculas."),
        ],
    )
    submit = SubmitField("Guardar Sede")


class UserForm(FlaskForm):
    """Formulario para gestionar Usuarios del sistema."""

    username = StringField(
        "Nombre de Usuario", validators=[DataRequired(), Length(min=3, max=64)]
    )

    # La contraseña es opcional al editar (si la dejan vacía, no se cambia)
    password = PasswordField("Contraseña", validators=[Optional(), Length(min=6)])

    # Select para la Sede (se llena dinámicamente en la ruta)
    sede_id = SelectField("Asignar Sede", coerce=int, validators=[DataRequired()])

    is_admin = BooleanField("¿Es Administrador General?")

    submit = SubmitField("Guardar Usuario")
