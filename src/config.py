import os
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# IMPORTANTE: Todas las configuraciones se obtienen del archivo .env
# No hay valores por defecto hardcodeados en este archivo.
# Si una variable no está definida en .env, el sistema fallará.

class Config:
    """Clase de configuración para manejar todas las variables de entorno"""
    
    # Configuración de SQL Server
    SQL_SERVER_HOST = os.getenv('SQL_SERVER_HOST')
    SQL_SERVER_PORT = os.getenv('SQL_SERVER_PORT')
    SQL_SERVER_DATABASE = os.getenv('SQL_SERVER_DATABASE')
    SQL_SERVER_USERNAME = os.getenv('SQL_SERVER_USERNAME')
    SQL_SERVER_PASSWORD = os.getenv('SQL_SERVER_PASSWORD')
    SQL_SERVER_TRUSTED_CONNECTION = os.getenv('SQL_SERVER_TRUSTED_CONNECTION', 'no').lower() == 'yes'
    
    # Configuración de RabbitMQ
    RABBITMQ_HOST = os.getenv('RABBITMQ_HOST')
    RABBITMQ_PORT = int(os.getenv('RABBITMQ_PORT')) if os.getenv('RABBITMQ_PORT') else None
    RABBITMQ_USERNAME = os.getenv('RABBITMQ_USERNAME')
    RABBITMQ_PASSWORD = os.getenv('RABBITMQ_PASSWORD')
    RABBITMQ_QUEUE = os.getenv('RABBITMQ_QUEUE')
    RABBITMQ_EXCHANGE = os.getenv('RABBITMQ_EXCHANGE')
    RABBITMQ_ROUTING_KEY = os.getenv('RABBITMQ_ROUTING_KEY')
    
    # Configuración de la aplicación
    LOG_LEVEL = os.getenv('LOG_LEVEL')
    SCRAPING_DELAY = int(os.getenv('SCRAPING_DELAY')) if os.getenv('SCRAPING_DELAY') else None
    MAX_RETRIES = int(os.getenv('MAX_RETRIES')) if os.getenv('MAX_RETRIES') else None
    
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
    
    @classmethod
    def validar_configuracion(cls):
        """Valida que todas las variables de entorno estén configuradas"""
        errores = []
        
        # Validar SQL Server
        if not cls.SQL_SERVER_HOST:
            errores.append("SQL_SERVER_HOST no está definido en .env")
        if not cls.SQL_SERVER_DATABASE:
            errores.append("SQL_SERVER_DATABASE no está definido en .env")
        
        # Validar RabbitMQ
        if not cls.RABBITMQ_HOST:
            errores.append("RABBITMQ_HOST no está definido en .env")
        if not cls.RABBITMQ_PORT:
            errores.append("RABBITMQ_PORT no está definido en .env")
        if not cls.RABBITMQ_USERNAME:
            errores.append("RABBITMQ_USERNAME no está definido en .env")
        if not cls.RABBITMQ_PASSWORD:
            errores.append("RABBITMQ_PASSWORD no está definido en .env")
        if not cls.RABBITMQ_QUEUE:
            errores.append("RABBITMQ_QUEUE no está definido en .env")
        if not cls.RABBITMQ_EXCHANGE:
            errores.append("RABBITMQ_EXCHANGE no está definido en .env")
        
        # Validar aplicación
        if not cls.LOG_LEVEL:
            errores.append("LOG_LEVEL no está definido en .env")
        if cls.SCRAPING_DELAY is None:
            errores.append("SCRAPING_DELAY no está definido en .env")
        if cls.MAX_RETRIES is None:
            errores.append("MAX_RETRIES no está definido en .env")
        
        return errores

# Validar configuración al importar el módulo
if __name__ == "__main__":
    errores = Config.validar_configuracion()
    if errores:
        print("❌ Errores en la configuración:")
        for error in errores:
            print(f"   • {error}")
        exit(1)
    else:
        print("✅ Configuración válida")
        print(f"📊 SQL Server: {Config.SQL_SERVER_HOST}")
        print(f"🐰 RabbitMQ: {Config.RABBITMQ_HOST}:{Config.RABBITMQ_PORT}")
        print(f"📝 Log Level: {Config.LOG_LEVEL}")
else:
    # Validar configuración al importar
    errores = Config.validar_configuracion()
    if errores:
        raise ValueError(f"Configuración incompleta. Variables faltantes: {', '.join(errores)}")
