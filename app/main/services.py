from datetime import datetime

from app import db
from app.models import Payment, Reservation

# --- Servicios de Reservas ---


def generate_reservation_code():
    last_reservation = Reservation.query.order_by(Reservation.id.desc()).first()
    new_id = (last_reservation.id + 1) if last_reservation else 1
    return f"L{new_id:06d}"


def get_all_reservations(estado=None):
    query = Reservation.query
    if estado:
        query = query.filter(Reservation.estado == estado)
    return query.order_by(Reservation.fecha_celebracion.desc()).all()


def get_reservations_by_date_range(start_date, end_date):
    start_datetime = datetime.combine(start_date, datetime.min.time())
    end_datetime = datetime.combine(end_date, datetime.max.time())
    query = Reservation.query.filter(
        Reservation.fecha_celebracion >= start_datetime,
        Reservation.fecha_celebracion <= end_datetime,
    )
    return query.order_by(Reservation.fecha_celebracion.desc()).all()


def create_reservation(form_data, user_id):
    new_reservation = Reservation(
        codigo_reserva=generate_reservation_code(),
        nombre_padres=form_data["nombre_padres"],
        telefono=form_data["telefono"],
        nombre_cumpleanero=form_data["nombre_cumpleanero"],
        dni_padres=form_data.get("dni_padres"),
        correo=form_data.get("correo"),
        fecha_celebracion=form_data["fecha_celebracion"],
        modalidad=form_data["modalidad"],
        estado=form_data["estado"],
        accesorios=form_data.get("accesorios"),
        comentarios=form_data.get("comentarios"),
        total=form_data.get("total"),
        user_id=user_id,
        salon="Salon1"
        if form_data["modalidad"] in ["Paquete LUDI", "Paquete JESSI"]
        else "Salon2",
        horario="3:00 PM - 5:30 PM",
    )
    db.session.add(new_reservation)
    db.session.commit()
    return new_reservation


# --- Servicios de Abonos ---


def get_payments_by_date_range(start_date, end_date):
    query = Payment.query.filter(
        Payment.fecha_abono >= start_date, Payment.fecha_abono <= end_date
    )
    return query.order_by(Payment.fecha_abono.desc()).all()


def create_payment(form_data, user_id):
    reservation_id = form_data["reservation_id"]
    reservation = db.session.get(Reservation, reservation_id)

    if not reservation:
        raise Exception(f"No se encontró la reserva con ID {reservation_id}")
    if reservation.estado != "Reservado":
        raise Exception(
            f"La reserva {reservation.codigo_reserva} ya está {reservation.estado.lower()}."
        )

    new_payment = Payment(
        reservation_id=reservation_id,
        codigo_reserva_str=reservation.codigo_reserva,
        fecha_abono=datetime.utcnow().date(),
        metodo_pago=form_data["metodo_pago"],
        monto=form_data["monto"],
        referencia=form_data.get("referencia"),
        modalidad=reservation.modalidad,
        comentarios=form_data.get("comentarios"),
        user_id=user_id,
    )

    reservation.estado = "Abonado"
    reservation.updated_at = datetime.utcnow()

    db.session.add(new_payment)
    db.session.add(reservation)
    db.session.commit()
    return new_payment
