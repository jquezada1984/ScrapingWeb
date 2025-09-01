#!/usr/bin/env python3
"""
Script para probar la consulta a la base de datos
"""

from src.database import DatabaseManager

def test_db_query():
    """Prueba la consulta a la base de datos"""
    try:
        db_manager = DatabaseManager()
        
        # Consulta de prueba
        query = """
            SELECT id, nombre, url_login, url_destino, descripcion, fecha_creacion
            FROM urls_automatizacion 
            WHERE nombre = :nombre
        """
        
        nombre_aseguradora = "PAN AMERICAN LIFE DE ECUADOR"
        
        print(f"🔍 Probando consulta para: {nombre_aseguradora}")
        print(f"📝 Query: {query}")
        
        # Ejecutar consulta
        results = db_manager.execute_query(query, {'nombre': nombre_aseguradora})
        
        if results and len(results) > 0:
            print(f"✅ Encontrados {len(results)} resultados:")
            for i, row in enumerate(results):
                print(f"\n📋 Resultado {i+1}:")
                print(f"   ID: {row['id']}")
                print(f"   Nombre: {row['nombre']}")
                print(f"   URL Login: {row['url_login']}")
                print(f"   URL Destino: {row['url_destino']}")
                print(f"   Descripción: {row['descripcion']}")
                print(f"   Fecha Creación: {row['fecha_creacion']}")
        else:
            print("⚠️  No se encontraron resultados")
            
    except Exception as e:
        print(f"❌ Error en la consulta: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("🚀 Probando consulta a la base de datos...")
    test_db_query()
