import json
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
from app.models import Reservation, Sede


@bp.route("/reservas/nueva", methods=["POST"])
@login_required
def nueva_reserva():
    form = ReservationForm()

    # Lógica de sedes para Admin
    if current_user.is_admin:
        form.sede_seleccionada.choices = [(s.id, s.nombre) for s in Sede.query.all()]
    else:
        form.sede_seleccionada.choices = []

    if form.validate_on_submit():
        try:
            # 1. Determinar Sede
            if current_user.is_admin:
                sede_id_final = form.sede_seleccionada.data
                sede_obj = db.session.get(Sede, sede_id_final)
                if not sede_obj:
                    flash("Error: Sede seleccionada no válida.", "danger")
                    return redirect(url_for("main.reservas"))
            else:
                if not current_user.sede:
                    flash("Error: Tu usuario no tiene una sede asignada.", "danger")
                    return redirect(url_for("main.reservas"))
                sede_obj = current_user.sede
                sede_id_final = sede_obj.id

            # 2. Generar Código
            codigo_reserva_generado = get_next_reservation_code(
                sede_id=sede_id_final, prefijo=sede_obj.prefijo
            )

            # 3. Totales
            total_reserva = form.total.data or Decimal("0.0")
            total_final = total_reserva

            # === 🔍 DEBUG: VERIFICAR DATOS ANTES DE GUARDAR ===
            print("\n" + "=" * 30)
            print("🔍 DEBUG: INTENTANDO GUARDAR RESERVA")
            print(f"👉 DATA RECIBIDA EN FORM (Adicionales): '{form.adicionales.data}'")
            print(f"👉 TIPO DE DATO: {type(form.adicionales.data)}")
            print("=" * 30 + "\n")
            # ==================================================

            # 4. Crear Objeto
            nueva_reserva = Reservation(
                user_id=current_user.id,
                sede_id=sede_id_final,
                codigo_reserva=codigo_reserva_generado,
                nombre_padres=form.nombre_padres.data,
                telefono=form.telefono.data,
                nombre_cumpleanero=form.nombre_cumpleanero.data,
                dni_padres=form.dni_padres.data,
                correo=form.correo.data,
                fecha_celebracion=form.fecha_celebracion.data,
                modalidad=form.modalidad.data,
                salon=form.salon.data,
                horario=form.horario.data,
                paquete=form.paquete.data,
                ninos=form.ninos.data,
                adultos=form.adultos.data,
                estado=form.estado.data,
                total=total_final,
                # ASIGNACIÓN DE ADICIONALES
                adicionales=form.adicionales.data,
                accesorios=form.accesorios.data,
                comentarios=form.comentarios.data,
            )

            # === 🔍 DEBUG: VERIFICAR OBJETO ===
            print(f"👉 DATA EN OBJETO SQLALCHEMY: '{nueva_reserva.adicionales}'")
            # =================================

            db.session.add(nueva_reserva)
            db.session.commit()

            flash(f"Reserva {codigo_reserva_generado} creada exitosamente.", "success")
            return redirect(url_for("main.reservas"))

        except Exception as e:
            db.session.rollback()
            print(f"❌ ERROR EXCEPCIÓN AL GUARDAR: {e}")  # Debug de error
            flash(f"Error al crear la reserva: {e}", "danger")
            return redirect(url_for("main.reservas"))

    # Debug de validación fallida
    print("\n❌ EL FORMULARIO NO ES VÁLIDO:")
    for field, errors in form.errors.items():
        print(f"   - Campo '{field}': {errors}")
        flash(
            f"Error en {getattr(form, field).label.text}: {', '.join(errors)}", "danger"
        )

    return redirect(url_for("main.reservas"))


@bp.route("/abonos/nuevo", methods=["POST"])
@login_required
def nuevo_abono():
    form = PaymentForm()
    sede_filtro = current_user.sede_id if not current_user.is_admin else None
    reservas_pendientes = get_all_reservations(estado="Reservado", sede_id=sede_filtro)

    form.reservation_id.choices = [
        (r.id, f"{r.codigo_reserva} - {r.nombre_padres}") for r in reservas_pendientes
    ]
    form.reservation_id.choices.insert(0, (0, "-- Seleccionar Reserva --"))

    if form.validate_on_submit():
        try:
            payment = create_payment(form_data=form.data, user_id=current_user.id)
            flash(
                f"Abono registrado para {payment.reservation.codigo_reserva}.",
                "success",
            )
        except Exception as e:
            db.session.rollback()
            flash(f"Error al registrar el abono: {str(e)}", "danger")
    else:
        for field, errors in form.errors.items():
            flash(f"Error en {form[field].label.text}: {', '.join(errors)}", "warning")

    return redirect(url_for("main.abonos"))


# --- MAPA DE OPCIONES ORIGINAL (Sin agregados no solicitados) ---
OPCIONES_RESERVA = {
    "minimos": {
        "Exclusivo": {"ninos": 0, "adultos": 0},
        "Salón 1": {"ninos": 17, "adultos": 17},
        "Salón 2": {"ninos": 12, "adultos": 12},
    },
    "precios_paquete": {
        "Exclusivo": 3200.00,
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
        "Exclusivo": [],
    },
}


@bp.route("/opciones-reserva")
@login_required
def get_opciones_reserva():
    return jsonify(OPCIONES_RESERVA)


@bp.route("/proximo-codigo/<int:sede_id>")
@login_required
def proximo_codigo_sede(sede_id):
    sede = db.session.get(Sede, sede_id)
    if not sede:
        return jsonify({"codigo": "Error"})
    codigo = get_next_reservation_code(sede.id, sede.prefijo)
    return jsonify({"codigo": codigo})


@bp.route("/reservas/<int:id>", methods=["GET"])
@login_required
def obtener_detalle_reserva(id):
    reserva = db.session.get(Reservation, id)
    if not reserva:
        return jsonify({"error": "Reserva no encontrada"}), 404

    lista_adicionales = []
    if reserva.adicionales:
        try:
            lista_adicionales = json.loads(reserva.adicionales)
        except json.JSONDecodeError:
            lista_adicionales = []

    fecha_fmt = (
        reserva.fecha_celebracion.strftime("%d/%m/%Y")
        if reserva.fecha_celebracion
        else "-"
    )

    return jsonify(
        {
            "codigo": reserva.codigo_reserva,
            "estado": reserva.estado,
            "nombre_padres": reserva.nombre_padres,
            "dni": reserva.dni_padres or "-",
            "telefono": reserva.telefono,
            "correo": reserva.correo or "-",
            "nombre_cumpleanero": reserva.nombre_cumpleanero or "-",
            "fecha": fecha_fmt,
            "horario": reserva.horario or "-",
            "salon": reserva.salon or "-",
            "modalidad": reserva.modalidad,
            "paquete": reserva.paquete or "-",
            "ninos": reserva.ninos,
            "adultos": reserva.adultos,
            "total": float(reserva.total),
            "accesorios": reserva.accesorios or "Ninguno",
            "comentarios": reserva.comentarios or "Ninguno",
            "adicionales": lista_adicionales,
        }
    )


@bp.route("/reservas/editar/<int:id>", methods=["POST"])
@login_required
def editar_reserva(id):
    reserva = db.session.get(Reservation, id)
    if not reserva:
        flash("Error: Reserva no encontrada.", "danger")
        return redirect(url_for("main.reservas"))

    form = ReservationForm()

    # Lógica de Sedes para validación (igual que en nueva)
    if current_user.is_admin:
        form.sede_seleccionada.choices = [(s.id, s.nombre) for s in Sede.query.all()]
    else:
        form.sede_seleccionada.choices = []

    if form.validate_on_submit():
        try:
            # 1. Actualizar campos básicos
            reserva.nombre_padres = form.nombre_padres.data
            reserva.correo = form.correo.data
            reserva.telefono = form.telefono.data
            reserva.dni_padres = form.dni_padres.data
            reserva.nombre_cumpleanero = form.nombre_cumpleanero.data
            reserva.fecha_celebracion = form.fecha_celebracion.data

            # 2. Actualizar campos dinámicos
            reserva.modalidad = form.modalidad.data
            reserva.salon = form.salon.data
            reserva.horario = form.horario.data
            reserva.paquete = form.paquete.data
            reserva.ninos = form.ninos.data
            reserva.adultos = form.adultos.data
            reserva.estado = form.estado.data

            # 3. Actualizar Extras y Totales
            reserva.accesorios = form.accesorios.data
            reserva.comentarios = form.comentarios.data

            # El total ya viene calculado desde el JS en el campo readonly
            reserva.total = form.total.data or Decimal("0.0")

            # JSON de adicionales actualizado
            reserva.adicionales = form.adicionales.data

            db.session.commit()
            flash(
                f"Reserva {reserva.codigo_reserva} actualizada correctamente.",
                "success",
            )

        except Exception as e:
            db.session.rollback()
            flash(f"Error al actualizar: {e}", "danger")

    else:
        for field, errors in form.errors.items():
            flash(
                f"Error en {getattr(form, field).label.text}: {', '.join(errors)}",
                "danger",
            )

    return redirect(url_for("main.reservas"))
