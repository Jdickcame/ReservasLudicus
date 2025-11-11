from flask_wtf import FlaskForm
from wtforms import BooleanField, PasswordField, StringField, SubmitField
from wtforms.validators import DataRequired


class LoginForm(FlaskForm):
    """Formulario de Login (basado en mockup image_3e4a7f.png)."""

    username = StringField(
        "Usuario:",
        validators=[DataRequired(message="El usuario es requerido.")],
        render_kw={"placeholder": "ludireserva"},
    )
    password = PasswordField(
        "Contraseña:",
        validators=[DataRequired(message="La contraseña es requerida.")],
        render_kw={"placeholder": "••••••••"},
    )
    remember_me = BooleanField("Recordarme")
    submit = SubmitField("Ingresar")
