from datetime import datetime

from app import db
from app.models import Payment, Reservation

# --- Servicios de Reservas ---


def generate_reservation_code():
    # Esta función parece obsoleta, ahora usamos get_next_reservation_code
    # La mantengo por si acaso la usas en otro lado
    last_reservation = Reservation.query.order_by(Reservation.id.desc()).first()
    new_id = (last_reservation.id + 1) if last_reservation else 1
    return f"L{new_id:06d}"


def get_all_reservations(estado=None, sede_id=None):
    """
    Obtiene todas las reservas.
    Si sede_id es None, ignora el filtro de sede (trae todas).
    """
    query = db.select(Reservation)

    if estado:
        query = query.where(Reservation.estado == estado)

    # === CORRECCIÓN: Solo filtrar si hay un ID válido ===
    if sede_id:
        query = query.where(Reservation.sede_id == sede_id)
    # ===================================================

    query = query.order_by(Reservation.created_at.desc())
    return db.session.scalars(query).all()


def get_reservations_by_date_range(fecha_desde, fecha_hasta, sede_id=None):
    """
    Obtiene reservas en un rango de fechas.
    Si sede_id es None, ignora el filtro de sede.
    """
    query = db.select(Reservation)

    # 1. Filtros de Fecha (Siempre se aplican)
    query = query.where(
        Reservation.fecha_celebracion >= fecha_desde,
        Reservation.fecha_celebracion <= fecha_hasta,
    )

    # 2. Filtro de Sede (Condicional)
    # === CORRECCIÓN: Solo filtrar si hay un ID válido ===
    if sede_id:
        query = query.where(Reservation.sede_id == sede_id)
    # ===================================================

    query = query.order_by(Reservation.fecha_celebracion.asc())
    return db.session.scalars(query).all()


def create_reservation(form_data, user_id):
    # Nota: Parece que ahora usas la lógica directa en routes.py
    # Mantengo esto por compatibilidad, pero asegúrate de que use la sede
    pass


# --- Servicios de Abonos ---


def get_payments_by_date_range(fecha_desde, fecha_hasta, sede_id=None):
    """
    Obtiene abonos en un rango de fechas.
    Si sede_id es None, ignora el filtro de sede.
    """
    query = db.select(Payment).join(Reservation)

    # 1. Filtros de Fecha
    query = query.where(
        Payment.fecha_abono >= fecha_desde,
        Payment.fecha_abono <= fecha_hasta,
    )

    # 2. Filtro de Sede
    # === CORRECCIÓN: Solo filtrar si hay un ID válido ===
    if sede_id:
        query = query.where(Reservation.sede_id == sede_id)
    # ===================================================

    query = query.order_by(Payment.fecha_abono.asc())
    return db.session.scalars(query).all()


def create_payment(form_data, user_id):
    reservation_id = form_data["reservation_id"]
    reservation = db.session.get(Reservation, reservation_id)

    if not reservation:
        raise Exception(f"No se encontró la reserva con ID {reservation_id}")

    # Opcional: Validar estado si es necesario
    # if reservation.estado != "Reservado": ...

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

    # Actualizar estado de reserva
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

    # 3. Rellenar con 5 ceros
    return f"{prefijo.upper()}{str(next_number).zfill(5)}"
