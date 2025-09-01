import pyodbc
import logging
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from sqlalchemy.exc import SQLAlchemyError
from typing import Optional, List, Dict, Any
from .config import Config

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Clase para manejar la conexión y operaciones con SQL Server"""
    
    def __init__(self):
        self.connection_string = Config.get_sql_connection_string()
        self.engine = None
        self.Session = None
        self._initialize_engine()
    
    def _initialize_engine(self):
        """Inicializa el motor de SQLAlchemy"""
        try:
            self.engine = create_engine(
                f"mssql+pyodbc:///?odbc_connect={self.connection_string}",
                echo=False
            )
            self.Session = sessionmaker(bind=self.engine)
            logger.info("Motor de base de datos inicializado correctamente")
        except Exception as e:
            logger.error(f"Error al inicializar el motor de base de datos: {e}")
            raise
    
    def test_connection(self) -> bool:
        """Prueba la conexión a la base de datos"""
        try:
            with self.engine.connect() as connection:
                result = connection.execute(text("SELECT 1"))
                logger.info("Conexión a la base de datos exitosa")
                return True
        except Exception as e:
            logger.error(f"Error al conectar con la base de datos: {e}")
            return False
    
    def execute_query(self, query: str, params: Optional[Dict] = None) -> List[Dict]:
        """Ejecuta una consulta SQL y retorna los resultados"""
        try:
            with self.Session() as session:
                if params:
                    result = session.execute(text(query), params)
                else:
                    result = session.execute(text(query))
                
                if result.returns_rows:
                    columns = result.keys()
                    return [dict(zip(columns, row)) for row in result.fetchall()]
                else:
                    session.commit()
                    return []
        except SQLAlchemyError as e:
            logger.error(f"Error al ejecutar consulta: {e}")
            raise
    
    def insert_data(self, table_name: str, data: Dict[str, Any]) -> bool:
        """Inserta datos en una tabla específica"""
        try:
            columns = ', '.join(data.keys())
            placeholders = ', '.join([f':{key}' for key in data.keys()])
            query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            with self.Session() as session:
                session.execute(text(query), data)
                session.commit()
                logger.info(f"Datos insertados exitosamente en {table_name}")
                return True
        except SQLAlchemyError as e:
            logger.error(f"Error al insertar datos en {table_name}: {e}")
            return False
    
    def create_table_if_not_exists(self, table_name: str, columns: Dict[str, str]):
        """Crea una tabla si no existe"""
        try:
            column_definitions = []
            for column_name, column_type in columns.items():
                column_definitions.append(f"{column_name} {column_type}")
            
            create_table_sql = f"""
            IF NOT EXISTS (SELECT * FROM sysobjects WHERE name='{table_name}' AND xtype='U')
            CREATE TABLE {table_name} (
                {', '.join(column_definitions)}
            )
            """
            
            with self.Session() as session:
                session.execute(text(create_table_sql))
                session.commit()
                logger.info(f"Tabla {table_name} creada o verificada exitosamente")
        except SQLAlchemyError as e:
            logger.error(f"Error al crear tabla {table_name}: {e}")
            raise
    
    def close(self):
        """Cierra la conexión a la base de datos"""
        if self.engine:
            self.engine.dispose()
            logger.info("Conexión a la base de datos cerrada")
