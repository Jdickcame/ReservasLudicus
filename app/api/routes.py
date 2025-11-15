import json  # <-- ¡AÑADE ESTA IMPORTACIÓN AL PRINCIPIO!
from decimal import Decimal

from flask import flash, jsonify, redirect, url_for
from flask_login import current_user, login_required

from app import db
from app.api import bp
from app.main.forms import PaymentForm, ReservationForm
from app.main.services import (
    create_payment,
    get_all_reservations,
    get_next_reservation_code,
)
from app.models import Reservation


@bp.route("/reservas/nueva", methods=["POST"])
@login_required
def nueva_reserva():
    # --- OBTENER SEDE DEL USUARIO ---
    if not current_user.sede:
        flash(
            "Error: Tu usuario no tiene una sede asignada. Contacta al administrador.",
            "danger",
        )
        return redirect(url_for("main.reservas"))

    user_sede = current_user.sede
    # --------------------------------
    form = ReservationForm()
    if form.validate_on_submit():
        try:
            # === GENERAR EL CÓDIGO CON SEDE ===
            codigo_reserva_generado = get_next_reservation_code(
                sede_id=user_sede.id, prefijo=user_sede.prefijo
            )
            # ==================================

            # --- LÓGICA DE TOTALES ---
            # 1. Obtener el total base de la reserva (del formulario)
            total_reserva = form.total.data or Decimal("0.0")

            # 2. Procesar los adicionales del JSON
            total_adicionales = Decimal("0.0")
            if form.adicionales.data:
                try:
                    # Lee el JSON que nuestro JavaScript creó
                    lista_adicionales = json.loads(form.adicionales.data)
                    for item in lista_adicionales:
                        total_adicionales += Decimal(item["precio"]) * Decimal(
                            item["cantidad"]
                        )
                except json.JSONDecodeError:
                    # Manejar error si el JSON está malformado
                    pass

            # 3. Sumar y asignar el Total Final
            total_final = total_reserva + total_adicionales

            # --- CREAR EL OBJETO RESERVATION ---
            nueva_reserva = Reservation(
                user_id=current_user.id,
                sede_id=user_sede.id,
                codigo_reserva=codigo_reserva_generado,
                nombre_padres=form.nombre_padres.data,
                telefono=form.telefono.data,
                nombre_cumpleanero=form.nombre_cumpleanero.data,
                dni_padres=form.dni_padres.data,
                correo=form.correo.data,
                fecha_celebracion=form.fecha_celebracion.data,
                modalidad=form.modalidad.data,
                estado=form.estado.data,
                # --- ASIGNAR CAMPOS NUEVOS ---
                total=total_final,  # El total combinado
                adicionales=form.adicionales.data,  # El JSON crudo
                accesorios=form.accesorios.data,
                comentarios=form.comentarios.data,
            )

            db.session.add(nueva_reserva)
            db.session.commit()

            flash("Reserva creada exitosamente.", "success")
            return redirect(url_for("main.reservas"))

        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear la reserva: {e}", "danger")
            # Quedarse en la página de reservas para no perder el modal
            return redirect(url_for("main.reservas"))

    # Si el formulario no es válido
    # ... (tu manejo de errores de formulario) ...
    flash("Error en el formulario. Revisa los campos.", "danger")
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


OPCIONES_RESERVA = {
    "minimos": {
        # El '1' es un ejemplo, pon 0 si no hay mínimo
        "Exclusivo": {"ninos": 0, "adultos": 0},
        "Salón 1": {"ninos": 17, "adultos": 17},
        "Salón 2": {"ninos": 12, "adultos": 12},
    },
    "precios_paquete": {
        "Exclusivo": 3200,
        "Paquete LUDI": 39.90,
        "Paquete JESSI": 49.90,
        "Paquete LUDI SUPER ESTRELLA": 59.90,
    },
    "horarios": {
        "Salón 1": [
            {"id": "3:00 PM - 5:30 PM", "texto": "3:00 PM - 5:30 PM"},
            {"id": "6:30 PM - 9:00 PM", "texto": "6:30 PM - 9:00 PM"},
            {"id": "11:00 AM - 1:30 PM", "texto": "11:00 AM - 1:30 PM"},
        ],
        "Salón 2": [
            {"id": "3:30 PM - 6:00 PM", "texto": "3:30 PM - 6:00 PM"},
            {"id": "7:00 PM - 9:30 PM", "texto": "7:00 PM - 9:30 PM"},
            {"id": "11:30 AM - 2:00 PM", "texto": "11:30 AM - 2:00 PM"},
        ],
    },
    "paquetes": {
        "Paquete LUDI": [
            {"id": "Hot Dog", "texto": "Hot Dog"},
            {"id": "Pan con Pollo", "texto": "Pan con Pollo"},
        ],
        "Paquete JESSI": [{"id": "Hot Dog", "texto": "Hot Dog"}],
        "Paquete LUDI SUPER ESTRELLA": [{"id": "Chicharrón", "texto": "Chicharrón"}],
    },
}


@bp.route("/opciones-reserva")
@login_required
def get_opciones_reserva():
    """
    Endpoint que provee las opciones dinámicas para el formulario.
    """
    return jsonify(OPCIONES_RESERVA)
