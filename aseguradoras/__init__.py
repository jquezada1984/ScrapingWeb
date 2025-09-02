#!/usr/bin/env python3
"""
Paquete principal de aseguradoras
Contiene implementaciones específicas para cada aseguradora
"""

import os
import importlib
from typing import Dict, List, Optional

# Información del paquete principal
__version__ = "1.0.0"
__author__ = "Sistema de Automatización"
__description__ = "Paquete principal para manejo de múltiples aseguradoras"

class GestorAseguradoras:
    """Gestor principal para manejar múltiples aseguradoras"""
    
    def __init__(self):
        self.aseguradoras_disponibles = {}
        self.cargar_aseguradoras()
    
    def cargar_aseguradoras(self):
        """Carga dinámicamente todas las aseguradoras disponibles"""
        try:
            # Obtener la ruta del directorio actual
            directorio_actual = os.path.dirname(os.path.abspath(__file__))
            
            # Buscar carpetas de aseguradoras
            for item in os.listdir(directorio_actual):
                ruta_completa = os.path.join(directorio_actual, item)
                
                # Verificar que sea un directorio y tenga __init__.py
                if (os.path.isdir(ruta_completa) and 
                    os.path.exists(os.path.join(ruta_completa, '__init__.py'))):
                    
                    try:
                        # Intentar importar el módulo
                        modulo = importlib.import_module(f"aseguradoras.{item}")
                        
                        # Verificar si tiene la información necesaria
                        if hasattr(modulo, 'get_aseguradora_info'):
                            info = modulo.get_aseguradora_info()
                            self.aseguradoras_disponibles[item] = {
                                'modulo': modulo,
                                'info': info,
                                'ruta': ruta_completa
                            }
                            print(f"✅ Aseguradora cargada: {info.get('nombre', item)}")
                        
                    except Exception as e:
                        print(f"⚠️  Error cargando aseguradora {item}: {e}")
            
            print(f"📊 Total aseguradoras cargadas: {len(self.aseguradoras_disponibles)}")
            
        except Exception as e:
            print(f"❌ Error cargando aseguradoras: {e}")
    
    def listar_aseguradoras(self) -> List[Dict]:
        """Lista todas las aseguradoras disponibles"""
        return [
            {
                'codigo': codigo,
                'nombre': info['info'].get('nombre', codigo),
                'pais': info['info'].get('pais', 'N/A'),
                'activa': info['info'].get('activa', False),
                'ruta': info['ruta']
            }
            for codigo, info in self.aseguradoras_disponibles.items()
        ]
    
    def obtener_aseguradora(self, codigo: str) -> Optional[Dict]:
        """Obtiene una aseguradora específica por código"""
        if codigo in self.aseguradoras_disponibles:
            return self.aseguradoras_disponibles[codigo]
        return None
    
    def crear_procesador(self, codigo: str):
        """Crea un procesador para una aseguradora específica"""
        aseguradora = self.obtener_aseguradora(codigo)
        if aseguradora and hasattr(aseguradora['modulo'], 'crear_procesador'):
            return aseguradora['modulo'].crear_procesador()
        return None
    
    def validar_aseguradora(self, codigo: str) -> bool:
        """Valida que una aseguradora esté correctamente configurada"""
        aseguradora = self.obtener_aseguradora(codigo)
        if aseguradora and hasattr(aseguradora['modulo'], 'validar_configuracion'):
            try:
                errores = aseguradora['modulo'].validar_configuracion()
                return len(errores) == 0
            except:
                return False
        return False
    
    def obtener_configuracion(self, codigo: str) -> Optional[Dict]:
        """Obtiene la configuración de una aseguradora"""
        aseguradora = self.obtener_aseguradora(codigo)
        if aseguradora and hasattr(aseguradora['modulo'], 'get_config_completa'):
            return aseguradora['modulo'].get_config_completa()
        return None

# Instancia global del gestor
gestor = GestorAseguradoras()

# Funciones de conveniencia
def listar_aseguradoras():
    """Lista todas las aseguradoras disponibles"""
    return gestor.listar_aseguradoras()

def obtener_aseguradora(codigo: str):
    """Obtiene una aseguradora específica"""
    return gestor.obtener_aseguradora(codigo)

def crear_procesador(codigo: str):
    """Crea un procesador para una aseguradora"""
    return gestor.crear_procesador(codigo)

def validar_aseguradora(codigo: str) -> bool:
    """Valida una aseguradora"""
    return gestor.validar_aseguradora(codigo)

def obtener_configuracion(codigo: str):
    """Obtiene la configuración de una aseguradora"""
    return gestor.obtener_configuracion(codigo)

# Exportar funciones principales
__all__ = [
    'GestorAseguradoras',
    'gestor',
    'listar_aseguradoras',
    'obtener_aseguradora',
    'crear_procesador',
    'validar_aseguradora',
    'obtener_configuracion'
]

if __name__ == "__main__":
    print("🏢 Gestor de Aseguradoras")
    print("=" * 40)
    
    # Listar aseguradoras disponibles
    aseguradoras = listar_aseguradoras()
    
    if aseguradoras:
        print("📋 Aseguradoras disponibles:")
        for aseguradora in aseguradoras:
            estado = "🟢 Activa" if aseguradora['activa'] else "🔴 Inactiva"
            print(f"   • {aseguradora['nombre']} ({aseguradora['codigo']}) - {aseguradora['pais']} - {estado}")
        
        # Probar validación de la primera aseguradora
        primera = aseguradoras[0]
        codigo = primera['codigo']
        
        print(f"\n🧪 Probando validación de {primera['nombre']}...")
        if validar_aseguradora(codigo):
            print("✅ Aseguradora válida")
            
            # Obtener configuración
            config = obtener_configuracion(codigo)
            if config:
                print(f"📊 Configuración obtenida: {len(config)} secciones")
                
                # Crear procesador
                procesador = crear_procesador(codigo)
                if procesador:
                    print("✅ Procesador creado correctamente")
                else:
                    print("❌ Error creando procesador")
            else:
                print("❌ Error obteniendo configuración")
        else:
            print("❌ Aseguradora no válida")
    else:
        print("⚠️  No hay aseguradoras disponibles")
