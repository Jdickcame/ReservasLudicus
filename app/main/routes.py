from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import AdicionalForm, PaymentForm, ReservationForm, SedeForm
from app.main.services import (
    get_all_reservations,
    get_next_reservation_code,
    get_payments_by_date_range,
    get_reservations_by_date_range,
)
from app.models import Adicional, Sede


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

    lista_de_adicionales = Adicional.query.order_by(Adicional.nombre).all()

    # ¡Usa la sede del usuario para el código!
    next_code_display = "Error"
    if current_user.sede:
        next_code_display = get_next_reservation_code(
            current_user.sede.id, current_user.sede.prefijo
        )

    reservations_list = []
    if str_desde and str_hasta:
        try:
            fecha_desde = datetime.strptime(str_desde, "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(str_hasta, "%Y-%m-%d").date()

            # Llamar a la CAPA DE SERVICIO para obtener los datos
            reservations_list = get_reservations_by_date_range(
                fecha_desde, fecha_hasta, sede_id=current_user.sede_id
            )
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
        next_reservation_code=next_code_display,
        lista_adicionales=lista_de_adicionales,
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

    # ¡FILTRAR RESERVAS PENDIENTES POR SEDE!
    reservas_pendientes = get_all_reservations(
        estado="Reservado", sede_id=current_user.sede_id
    )
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
            payments_list = get_payments_by_date_range(
                fecha_desde, fecha_hasta, sede_id=current_user.sede_id
            )
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


@bp.route("/admin/adicionales")
@login_required
def admin_adicionales():
    """Muestra la lista de todos los adicionales."""
    adicionales = Adicional.query.order_by(Adicional.nombre).all()
    return render_template(
        "admin/adicionales.html", title="Admin Adicionales", adicionales=adicionales
    )


@bp.route("/admin/adicionales/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_adicional():
    """Crea un nuevo adicional."""
    form = AdicionalForm()
    if form.validate_on_submit():
        try:
            nuevo = Adicional(nombre=form.nombre.data, precio=form.precio.data)
            db.session.add(nuevo)
            db.session.commit()
            flash(f"Adicional '{nuevo.nombre}' creado exitosamente.", "success")
            return redirect(url_for("main.admin_adicionales"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al crear el adicional: {e}", "danger")

    return render_template(
        "admin/gestionar_adicional.html", title="Nuevo Adicional", form=form
    )


@bp.route("/admin/adicionales/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_adicional(id):
    """Edita un adicional existente."""
    adicional = Adicional.query.get_or_404(id)
    form = AdicionalForm(obj=adicional)  # Carga el form con datos existentes

    if form.validate_on_submit():
        try:
            adicional.nombre = form.nombre.data
            adicional.precio = form.precio.data
            db.session.commit()
            flash(f"Adicional '{adicional.nombre}' actualizado.", "info")
            return redirect(url_for("main.admin_adicionales"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar el adicional: {e}", "danger")

    return render_template(
        "admin/gestionar_adicional.html", title="Editar Adicional", form=form
    )


@bp.route("/admin/adicionales/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_adicional(id):
    """Elimina un adicional (solo por POST)."""
    adicional = Adicional.query.get_or_404(id)
    try:
        nombre = adicional.nombre
        db.session.delete(adicional)
        db.session.commit()
        flash(f"Adicional '{nombre}' ha sido eliminado.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar el adicional: {e}", "danger")

    return redirect(url_for("main.admin_adicionales"))


@bp.route("/admin/sedes")
@login_required
def admin_sedes():
    sedes = Sede.query.order_by(Sede.nombre).all()
    return render_template("admin/sedes.html", title="Admin Sedes", sedes=sedes)


@bp.route("/admin/sedes/nuevo", methods=["GET", "POST"])
@login_required
def nueva_sede():
    form = SedeForm()
    if form.validate_on_submit():
        try:
            nueva = Sede(nombre=form.nombre.data, prefijo=form.prefijo.data.upper())
            db.session.add(nueva)
            db.session.commit()
            flash(
                f"Sede '{nueva.nombre}' creada con prefijo '{nueva.prefijo}'.",
                "success",
            )
            return redirect(url_for("main.admin_sedes"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error: El nombre o prefijo ya existe. {e}", "danger")
    return render_template("admin/gestionar_sede.html", title="Nueva Sede", form=form)


@bp.route("/admin/sedes/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_sede(id):
    sede = Sede.query.get_or_404(id)
    form = SedeForm(obj=sede)
    if form.validate_on_submit():
        try:
            sede.nombre = form.nombre.data
            sede.prefijo = form.prefijo.data.upper()
            db.session.commit()
            flash(f"Sede '{sede.nombre}' actualizada.", "info")
            return redirect(url_for("main.admin_sedes"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar la sede. {e}", "danger")
    return render_template("admin/gestionar_sede.html", title="Editar Sede", form=form)
