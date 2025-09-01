import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

class Config:
    """Clase de configuración para manejar todas las variables de entorno"""
    
    # Configuración de SQL Server
    SQL_SERVER_HOST = os.getenv('SQL_SERVER_HOST', 'localhost')
    SQL_SERVER_PORT = os.getenv('SQL_SERVER_PORT', '1433')
    SQL_SERVER_DATABASE = os.getenv('SQL_SERVER_DATABASE', 'scraping_db')
    SQL_SERVER_USERNAME = os.getenv('SQL_SERVER_USERNAME', '')
    SQL_SERVER_PASSWORD = os.getenv('SQL_SERVER_PASSWORD', '')
    SQL_SERVER_TRUSTED_CONNECTION = os.getenv('SQL_SERVER_TRUSTED_CONNECTION', 'no').lower() == 'yes'
    
    # Configuración de RabbitMQ
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST', 'localhost')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT', '5672'))
    RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME', 'guest')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD', 'guest')
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE', 'aseguradora_queue')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE', 'aseguradora_exchange')
    RABBITMQ_ROUTING_KEY = os.getenv('RABBITMQ_ROUTING_KEY', 'aseguradora')
    
    # Configuración de la aplicación
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY', '2'))
    MAX_RETRIES = int(os.getenv('MAX_RETRIES', '3'))
    
    @classmethod
    def get_sql_connection_string(cls):
        """Genera la cadena de conexión para SQL Server"""
        if cls.SQL_SERVER_TRUSTED_CONNECTION:
            # Autenticación de Windows - usar solo el nombre del servidor sin puerto
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={cls.SQL_SERVER_HOST};"
                f"DATABASE={cls.SQL_SERVER_DATABASE};"
                f"Trusted_Connection=yes;"
                f"TrustServerCertificate=yes;"
            )
        else:
            # Autenticación con usuario y contraseña
            return (
                f"DRIVER={{ODBC Driver 17 for SQL Server}};"
                f"SERVER={cls.SQL_SERVER_HOST},{cls.SQL_SERVER_PORT};"
                f"DATABASE={cls.SQL_SERVER_DATABASE};"
                f"UID={cls.SQL_SERVER_USERNAME};"
                f"PWD={cls.SQL_SERVER_PASSWORD};"
                f"TrustServerCertificate=yes;"
            )
    
    @classmethod
    def get_rabbitmq_url(cls):
        """Genera la URL de conexión para RabbitMQ"""
        return f"amqp://{cls.RABBITMQ_USERNAME}:{cls.RABBITMQ_PASSWORD}@{cls.RABBITMQ_HOST}:{cls.RABBITMQ_PORT}/"
