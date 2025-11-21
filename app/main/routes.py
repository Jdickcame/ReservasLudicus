from datetime import datetime

from flask import flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required

from app import db
from app.main import bp
from app.main.forms import (
    AdicionalForm,
    PaymentForm,
    ReservationForm,
    SedeForm,
    UserForm,
)
from app.main.services import (
    get_all_reservations,
    get_next_reservation_code,
    get_payments_by_date_range,
    get_reservations_by_date_range,
)
from app.models import Adicional, Sede, User


@bp.route("/")
@bp.route("/index")
@login_required  # Proteger esta ruta
def index():
    """Página de Inicio/Dashboard."""
    return render_template("index.html", title="Inicio")


@bp.route("/reservas")
@login_required
def reservas():
    """Muestra la página de gestión de Reservas."""

    # 1. Obtener parámetros de filtro
    str_desde = request.args.get("desde")
    str_hasta = request.args.get("hasta")
    sede_filtro_id = request.args.get("sede_filtro", type=int)

    # 2. Determinar la SEDE ACTIVA (para mostrar y para crear)
    sede_activa = None

    if current_user.is_admin:
        # ADMIN: Puede elegir sede. Si eligió una, esa es la activa.
        # Si no eligió (o es la primera carga), usa su propia sede por defecto.
        if sede_filtro_id:
            sede_activa = db.session.get(Sede, sede_filtro_id)
        else:
            sede_activa = current_user.sede
    else:
        # NO ADMIN: Siempre está atado a su sede asignada.
        sede_activa = current_user.sede

    # 3. Preparar el Formulario y Datos para el Modal
    reserva_form = ReservationForm()
    lista_de_adicionales = Adicional.query.order_by(Adicional.nombre).all()

    # Si hay una sede activa, la pre-seleccionamos en el formulario (campo oculto)
    # Esto es vital para que la API sepa a qué sede guardar si es admin.
    if sede_activa:
        reserva_form.sede_seleccionada.data = sede_activa.id

    # 4. Generar el Código de Reserva (Visual)
    next_code_display = "S/Sede"  # Valor por defecto
    if sede_activa:
        next_code_display = get_next_reservation_code(
            sede_activa.id, sede_activa.prefijo
        )

    # 5. Buscar Reservas (Filtradas por la Sede Activa)
    reservations_list = []
    if str_desde and str_hasta:
        try:
            fecha_desde = datetime.strptime(str_desde, "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(str_hasta, "%Y-%m-%d").date()

            # Llamar a la CAPA DE SERVICIO (pasando el ID de la sede activa)
            # Si sede_activa es None (ej: admin sin sede y sin filtro), trae todo o nada según tu lógica.
            # Aquí asumimos que si es None, no filtra (o filtra por None).
            filtro_sede_id = sede_activa.id if sede_activa else None

            reservations_list = get_reservations_by_date_range(
                fecha_desde, fecha_hasta, sede_id=filtro_sede_id
            )

            if not reservations_list:
                flash("No se encontraron reservas para ese rango de fechas.", "info")
        except ValueError:
            flash("Formato de fecha inválido. Usar YYYY-MM-DD.", "danger")

    # 6. Preparar lista de sedes para el dropdown del Admin
    all_sedes = []
    if current_user.is_admin:
        all_sedes = Sede.query.order_by(Sede.nombre).all()

    # Renderizar la plantilla
    return render_template(
        "reservas.html",
        title="Reservas",
        reservations=reservations_list,
        reserva_form=reserva_form,
        # Datos Extra
        next_reservation_code=next_code_display,
        lista_adicionales=lista_de_adicionales,
        # Filtros
        search_desde=str_desde,
        search_hasta=str_hasta,
        # Datos para el filtro de Sede (Admin)
        sedes=all_sedes,
        sede_actual_id=sede_activa.id if sede_activa else None,
    )


@bp.route("/abonos")
@login_required
def abonos():
    """Muestra la página de gestión de Abonos."""
    str_desde = request.args.get("desde")
    str_hasta = request.args.get("hasta")
    sede_filtro_id = request.args.get("sede_filtro", type=int)

    # 1. Determinar la sede activa (Igual que en reservas)
    sede_activa = None
    if current_user.is_admin:
        if sede_filtro_id:
            sede_activa = db.session.get(Sede, sede_filtro_id)
        # Si es admin y no elige filtro, ve todo (sede_activa = None)
    else:
        sede_activa = current_user.sede

    # 2. Preparar Formulario de Nuevo Abono
    payment_form = PaymentForm()

    # Filtrar el dropdown de reservas por la sede activa
    # Si sede_activa es None (Admin viendo todo), mostramos reservas de todas las sedes
    id_filtro_reservas = sede_activa.id if sede_activa else None

    reservas_pendientes = get_all_reservations(
        estado="Reservado", sede_id=id_filtro_reservas
    )

    payment_form.reservation_id.choices = [
        (r.id, f"{r.codigo_reserva} - {r.nombre_padres}") for r in reservas_pendientes
    ]
    payment_form.reservation_id.choices.insert(0, (0, "-- Seleccionar Reserva --"))

    # 3. Buscar Abonos
    payments_list = []
    if str_desde and str_hasta:
        try:
            fecha_desde = datetime.strptime(str_desde, "%Y-%m-%d").date()
            fecha_hasta = datetime.strptime(str_hasta, "%Y-%m-%d").date()

            # Usamos el ID de la sede activa para filtrar los pagos
            payments_list = get_payments_by_date_range(
                fecha_desde, fecha_hasta, sede_id=id_filtro_reservas
            )

            if not payments_list:
                flash("No se encontraron abonos para ese rango de fechas.", "info")
        except ValueError:
            flash("Formato de fecha inválido. Usar YYYY-MM-DD.", "danger")

    # 4. Preparar lista de sedes para el filtro (Solo Admin)
    all_sedes = []
    if current_user.is_admin:
        all_sedes = Sede.query.order_by(Sede.nombre).all()

    return render_template(
        "abonos.html",
        title="Abonos",
        payments=payments_list,
        payment_form=payment_form,
        search_desde=str_desde,
        search_hasta=str_hasta,
        # Variables nuevas para el filtro
        sedes=all_sedes,
        sede_actual_id=sede_activa.id if sede_activa else None,
    )


# ==========================================================
# === RUTAS DEL PANEL DE ADMIN (ADICIONALES) ===
# ==========================================================


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


# ==========================================================
# === RUTAS DEL PANEL DE ADMIN (SEDES) ===
# ==========================================================


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
            # Convertimos prefijo a mayúsculas automáticamente
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


@bp.route("/admin/sedes/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_sede(id):
    """Elimina una sede (solo por POST)."""
    sede = Sede.query.get_or_404(id)
    try:
        nombre = sede.nombre
        # Opcional: Verificar si hay usuarios o reservas antes de borrar
        # if sede.users.count() > 0 or sede.reservations.count() > 0:
        #     flash("No puedes eliminar una sede que tiene usuarios o reservas.", "warning")
        #     return redirect(url_for("main.admin_sedes"))

        db.session.delete(sede)
        db.session.commit()
        flash(f"Sede '{nombre}' ha sido eliminada.", "danger")
    except Exception as e:
        db.session.rollback()
        flash(f"Error al eliminar la sede: {e}", "danger")

    return redirect(url_for("main.admin_sedes"))


# ==========================================================
# === RUTAS DEL PANEL DE ADMIN (USUARIOS) ===
# ==========================================================


@bp.route("/admin/usuarios")
@login_required
def admin_usuarios():
    """Lista todos los usuarios y sus sedes."""
    # Solo un admin debería ver esto
    if not current_user.is_admin:
        flash("Acceso denegado.", "danger")
        return redirect(url_for("main.index"))

    users = User.query.order_by(User.username).all()
    return render_template(
        "admin/usuarios.html", title="Gestión de Usuarios", users=users
    )


@bp.route("/admin/usuarios/nuevo", methods=["GET", "POST"])
@login_required
def nuevo_usuario():
    form = UserForm()
    # Llenar el select de Sedes
    form.sede_id.choices = [
        (s.id, f"{s.nombre} ({s.prefijo})") for s in Sede.query.all()
    ]

    if form.validate_on_submit():
        if User.query.filter_by(username=form.username.data).first():
            flash("El nombre de usuario ya existe.", "warning")
        else:
            try:
                nuevo_user = User(
                    username=form.username.data,
                    sede_id=form.sede_id.data,
                    is_admin=form.is_admin.data,
                )
                # Encriptar contraseña (obligatoria al crear)
                if form.password.data:
                    nuevo_user.set_password(form.password.data)
                else:
                    flash(
                        "La contraseña es obligatoria para usuarios nuevos.", "danger"
                    )
                    return render_template(
                        "admin/gestionar_usuario.html", form=form, title="Nuevo Usuario"
                    )

                db.session.add(nuevo_user)
                db.session.commit()
                flash(f"Usuario {nuevo_user.username} creado exitosamente.", "success")
                return redirect(url_for("main.admin_usuarios"))
            except Exception as e:
                db.session.rollback()
                flash(f"Error al crear usuario: {e}", "danger")

    return render_template(
        "admin/gestionar_usuario.html", form=form, title="Nuevo Usuario"
    )


@bp.route("/admin/usuarios/editar/<int:id>", methods=["GET", "POST"])
@login_required
def editar_usuario(id):
    user = User.query.get_or_404(id)
    form = UserForm(obj=user)
    form.sede_id.choices = [
        (s.id, f"{s.nombre} ({s.prefijo})") for s in Sede.query.all()
    ]

    if form.validate_on_submit():
        try:
            user.username = form.username.data
            user.sede_id = form.sede_id.data
            user.is_admin = form.is_admin.data

            # Solo cambiamos la contraseña si escribieron algo nuevo
            if form.password.data:
                user.set_password(form.password.data)

            db.session.commit()
            flash(f"Usuario {user.username} actualizado.", "info")
            return redirect(url_for("main.admin_usuarios"))
        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {e}", "danger")

    return render_template(
        "admin/gestionar_usuario.html", form=form, title="Editar Usuario"
    )


@bp.route("/admin/usuarios/eliminar/<int:id>", methods=["POST"])
@login_required
def eliminar_usuario(id):
    if id == current_user.id:
        flash(
            "No puedes eliminar tu propio usuario mientras estás conectado.", "warning"
        )
        return redirect(url_for("main.admin_usuarios"))

    user = User.query.get_or_404(id)
    db.session.delete(user)
    db.session.commit()
    flash(f"Usuario {user.username} eliminado.", "danger")
    return redirect(url_for("main.admin_usuarios"))
