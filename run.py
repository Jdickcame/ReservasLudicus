import os

from app import create_app, db
from app.models import User

# Crear la aplicación Flask usando la factory
app = create_app()


@app.shell_context_processor
def make_shell_context():
    """Permite acceder a la base de datos y modelos en el shell de Flask"""
    from app.models import Payment, Reservation, User

    return {"db": db, "User": User, "Reservation": Reservation, "Payment": Payment}


def setup_database(app_context):
    """Crea las tablas en MySQL y el usuario admin inicial."""
    with app_context:
        print("Creando todas las tablas en la base de datos MySQL (si no existen)...")
        # Esto creará las tablas en tu DB 'ludicus_db'
        db.create_all()

        # Crear usuario 'ludireserva' del mockup de login
        if not User.query.filter_by(username="ludireserva").first():
            print("Creando usuario admin 'ludireserva'...")
            admin_user = User(username="ludireserva")
            admin_user.set_password("admin123")  # ¡Esta será tu contraseña para entrar!
            db.session.add(admin_user)
            db.session.commit()
            print("Usuario 'ludireserva' creado con contraseña 'admin123'.")
        else:
            print("El usuario 'ludireserva' ya existe.")


if __name__ == "__main__":
    # Creación de tablas al iniciar (si no existen)
    setup_database(app.app_context())

    # Iniciar el servidor de desarrollo
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)
