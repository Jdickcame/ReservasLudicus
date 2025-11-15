import logging

from flask import Flask
from flask_login import LoginManager
from flask_migrate import Migrate
from flask_sqlalchemy import SQLAlchemy

from config import Config

# --- Inicialización de Extensiones (Capas) ---
db = SQLAlchemy()
login = LoginManager()
login.login_view = "auth.login"  # Vista de login
migrate = Migrate()
login.login_message = "Por favor, inicia sesión para acceder a esta página."
login.login_message_category = "info"


def create_app(config_class=Config):
    """
    Patrón Factory: Crea y configura la instancia de la aplicación Flask.
    """

    app = Flask(__name__)

    # 1. Cargar Configuración
    app.config.from_object(config_class)
    app.logger.info(
        f"Conectando a la base de datos: {app.config['SQLALCHEMY_DATABASE_URI']}"
    )

    # 2. Configurar Logging
    logging.basicConfig(level=logging.DEBUG)

    # 3. Inicializar Extensiones (conectar capas a la app)
    #    ¡ESTE ES EL ORDEN CRÍTICO! db y login PRIMERO.
    db.init_app(app)
    login.init_app(app)
    migrate.init_app(app, db)  # Migrate DESPUÉS, ya que depende de db.

    # --- Registrar Blueprints (Rutas Modulares) ---
    # Los blueprints deben registrarse ANTES de usar el user_loader,
    # ya que los blueprints importan los modelos.

    from app.auth.routes import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main.routes import bp as main_bp

    app.register_blueprint(main_bp)

    from app.api.routes import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    # --- Configurar el User Loader ---
    # Esto ahora funciona porque 'login' está inicializado
    # y los blueprints han importado 'app.models'.
    from app.models import User

    @login.user_loader
    def load_user(user_id):
        return db.session.get(User, int(user_id))

    # ---------------------------------

    app.logger.info("Aplicación Lúdicus Park iniciada.")
    return app
