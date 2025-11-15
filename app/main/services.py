from datetime import datetime

from app import db
from app.models import Payment, Reservation

# --- Servicios de Reservas ---


def generate_reservation_code():
    last_reservation = Reservation.query.order_by(Reservation.id.desc()).first()
    new_id = (last_reservation.id + 1) if last_reservation else 1
    return f"L{new_id:06d}"


def get_all_reservations(estado=None, sede_id=None):
    """
    Obtiene todas las reservas, filtradas por estado y/o SEDE.
    """
    query = db.select(Reservation)
    if estado:
        query = query.where(Reservation.estado == estado)
    if sede_id:
        query = query.where(Reservation.sede_id == sede_id)  # <-- FILTRO AÑADIDO

    query = query.order_by(Reservation.created_at.desc())
    return db.session.scalars(query).all()


def get_reservations_by_date_range(fecha_desde, fecha_hasta, sede_id):
    """
    Obtiene reservas en un rango de fechas PARA UNA SEDE ESPECÍFICA.
    """
    query = (
        db.select(Reservation)
        .where(
            Reservation.sede_id == sede_id,  # <-- FILTRO AÑADIDO
            Reservation.fecha_celebracion >= fecha_desde,
            Reservation.fecha_celebracion <= fecha_hasta,
        )
        .order_by(Reservation.fecha_celebracion.asc())
    )
    return db.session.scalars(query).all()


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


def get_payments_by_date_range(fecha_desde, fecha_hasta, sede_id):
    """
    Obtiene abonos en un rango de fechas PARA UNA SEDE ESPECÍFICA.
    """
    query = (
        db.select(Payment)
        .join(Reservation)  # Unimos con Reservation para filtrar por Sede
        .where(
            Reservation.sede_id == sede_id,  # <-- FILTRO AÑADIDO
            Payment.fecha_abono >= fecha_desde,
            Payment.fecha_abono <= fecha_hasta,
        )
        .order_by(Payment.fecha_abono.asc())
    )
    return db.session.scalars(query).all()


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


def get_next_reservation_code(sede_id, prefijo):
    """
    Calcula el siguiente código de reserva para una SEDE específica.
    Formato: [PREFIJO]00001 (ej: TR00001, CH00002)
    """

    # 1. Buscar la última reserva (por ID) DE ESA SEDE
    last_reservation = db.session.scalar(
        db.select(Reservation)
        .where(Reservation.sede_id == sede_id)  # <-- FILTRO POR SEDE
        .order_by(Reservation.id.desc())
    )

    if not last_reservation:
        next_number = 1
    else:
        try:
            # 2. Extraer el número del código (ej: "TR00001" -> "00001")
            prefix_length = len(prefijo)
            number_part = last_reservation.codigo_reserva[prefix_length:]
            next_number = int(number_part) + 1
        except (ValueError, TypeError):
            next_number = 1

    # 3. Rellenar con 5 ceros (ej: 1 -> "00001", 43 -> "00043")
    return f"{prefijo.upper()}{str(next_number).zfill(5)}"
