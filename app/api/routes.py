from flask import flash, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.api import bp
from app.main.forms import PaymentForm, ReservationForm
from app.main.services import create_payment, create_reservation, get_all_reservations


@bp.route("/reservas/nueva", methods=["POST"])
@login_required
def nueva_reserva():
    """
    Endpoint de API para crear una nueva reserva (recibe datos del modal).
    """
    form = ReservationForm()

    # Validar el formulario con los datos recibidos
    if form.validate_on_submit():
        try:
            # Llamar a la CAPA DE SERVICIO para crear la reserva
            reservation = create_reservation(
                form_data=form.data, user_id=current_user.id
            )
            flash(
                f"Reserva {reservation.codigo_reserva} creada exitosamente.", "success"
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear la reserva: {str(e)}", "danger")

    else:
        # Si la validación falla, mostrar errores
        for field, errors in form.errors.items():
            for error in errors:
                flash(f"Error en {form[field].label.text}: {error}", "warning")

    # Redirigir de vuelta a la página de reservas
    return redirect(url_for("main.reservas"))


@bp.route("/abonos/nuevo", methods=["POST"])
@login_required
def nuevo_abono():
    """
    Endpoint de API para crear un nuevo abono.
    """
    form = PaymentForm()

    # Volver a poblar las opciones del SelectField (necesario para validación)
    reservas_pendientes = get_all_reservations(estado="Reservado")
    form.reservation_id.choices = [
        (r.id, f"{r.codigo_reserva} - {r.nombre_padres}") for r in reservas_pendientes
    ]
    form.reservation_id.choices.insert(0, (0, "-- Seleccionar Reserva --"))

    if form.validate_on_submit():
        try:
            # Llamar a la CAPA DE SERVICIO
            payment = create_payment(form_data=form.data, user_id=current_user.id)
            flash(
                f"Abono registrado para la reserva {payment.reservation.codigo_reserva}.",
                "success",
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar el abono: {str(e)}", "danger")

    else:
        for field, errors in form.errors.items():
            flash(f"Error en {form[field].label.text}: {', '.join(errors)}", "warning")

    # Redirigir de vuelta a la página de abonos
    return redirect(url_for("main.abonos"))
