import os

from dotenv import load_dotenv

# Cargar variables de entorno desde un archivo .env
basedir = os.path.abspath(os.path.dirname(__file__))
load_dotenv(os.path.join(basedir, ".env"))


class Config:
    """Configuraciones base de la aplicación Flask."""

    SECRET_KEY = (
        os.environ.get("SECRET_KEY") or "una-clave-secreta-muy-dificil-de-adivinar"
    )

    # --- Configuración de la Base de Datos MySQL (XAMPP) ---
    # Este es el setup estándar para XAMPP
    DB_USERNAME = os.environ.get("DB_USERNAME") or "root"
    DB_PASSWORD = os.environ.get("DB_PASSWORD") or ""  # Sin contraseña
    DB_HOSTNAME = os.environ.get("DB_HOSTNAME") or "localhost"
    DB_NAME = os.environ.get("DB_NAME") or "ludicus_db"  # La DB que creaste

    # URI de conexión de SQLAlchemy para MySQL
    SQLALCHEMY_DATABASE_URI = (
        f"mysql+pymysql://{DB_USERNAME}:{DB_PASSWORD}@{DB_HOSTNAME}/{DB_NAME}"
        "?charset=utf8mb4"
    )

    SQLALCHEMY_TRACK_MODIFICATIONS = False
