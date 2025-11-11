import logging

from flask import Flask
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy

from config import Config

# --- Inicialización de Extensiones (Capas) ---
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"  # Vista de login
login_manager.login_message = "Por favor, inicia sesión para acceder a esta página."
login_manager.login_message_category = "info"


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
    app.logger.info("Aplicación Lúdicus Park iniciada.")

    # 3. Inicializar Extensiones (conectar capas a la app)
    db.init_app(app)
    login_manager.init_app(app)

    # --- Registrar Blueprints (Rutas Modulares) ---

    from app.auth.routes import bp as auth_bp

    app.register_blueprint(auth_bp, url_prefix="/auth")

    from app.main.routes import bp as main_bp

    app.register_blueprint(main_bp)

    from app.api.routes import bp as api_bp

    app.register_blueprint(api_bp, url_prefix="/api")

    return app


# Importar modelos al final para evitar referencias circulares
from app import models
