from datetime import datetime

from flask import flash, render_template, request
from flask_login import login_required

from app.main import bp
from app.main.forms import PaymentForm, ReservationForm
from app.main.services import (
    get_all_reservations,
    get_payments_by_date_range,
    get_reservations_by_date_range,
)


@bp.route("/")
@bp.route("/index")
@login_required  # Proteger esta ruta
def index():
    """Página de Inicio/Dashboard (Mockup image_3e4a9e.jpg)."""
    return render_template("index.html", title="Inicio")


@bp.route("/reservas")
@login_required
def reservas():
    """Muestra la página de gestión de Reservas (Mockup image_3e4e7e.png)."""
    str_desde = request.args.get("desde")
    str_hasta = request.args.get("hasta")

    # Formulario para el modal de "Nuevo"
    reserva_form = ReservationForm()

    reservations_list = []
    if str_desde and str_hasta:
        try:
            fecha_desde = datetime.strptime(str_desde, "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(str_hasta, "%Y-%m-%d").date()

            # Llamar a la CAPA DE SERVICIO para obtener los datos
            reservations_list = get_reservations_by_date_range(fecha_desde, fecha_hasta)
            if not reservations_list:
                flash("No se encontraron reservas para ese rango de fechas.", "info")
        except ValueError:
            flash("Formato de fecha inválido. Usar YYYY-MM-DD.", "danger")

    # Renderizar la plantilla con los datos
    return render_template(
        "reservas.html",
        title="Reservas",
        reservations=reservations_list,
        reserva_form=reserva_form,  # Pasar el form al template
        search_desde=str_desde,
        search_hasta=str_hasta,
    )


@bp.route("/abonos")
@login_required
def abonos():
    """Muestra la página de gestión de Abonos (Mockup image_3e594d.jpg)."""
    str_desde = request.args.get("desde")
    str_hasta = request.args.get("hasta")

    # Formulario para el modal de "Nuevo Abono"
    payment_form = PaymentForm()

    # Precargar el dropdown 'Código de Reserva' del modal
    # Solo mostramos reservas que aún no están 'Abonado'
    reservas_pendientes = get_all_reservations(estado="Reservado")
    payment_form.reservation_id.choices = [
        (r.id, f"{r.codigo_reserva} - {r.nombre_padres}") for r in reservas_pendientes
    ]
    # Añadir una opción inicial
    payment_form.reservation_id.choices.insert(0, (0, "-- Seleccionar Reserva --"))

    payments_list = []
    if str_desde and str_hasta:
        try:
            fecha_desde = datetime.strptime(str_desde, "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(str_hasta, "%Y-%m-%d").date()

            # Llamar a la CAPA DE SERVICIO
            payments_list = get_payments_by_date_range(fecha_desde, fecha_hasta)
            if not payments_list:
                flash("No se encontraron abonos para ese rango de fechas.", "info")
        except ValueError:
            flash("Formato de fecha inválido. Usar YYYY-MM-DD.", "danger")

    return render_template(
        "abonos.html",
        title="Abonos",
        payments=payments_list,
        payment_form=payment_form,  # Pasar el form al template
        search_desde=str_desde,
        search_hasta=str_hasta,
    )
