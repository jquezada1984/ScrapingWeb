# 📸 Captura de Información Post-Login - PAN AMERICAN LIFE DE ECUADOR

## 🎯 **Descripción General**

Después de un login exitoso, el sistema automáticamente captura información de la pantalla que se muestra al usuario. Esta funcionalidad está diseñada para extraer datos de formularios, campos de texto, botones y otros elementos de la interfaz web.

## 🔄 **Flujo de Trabajo**

```
1. 🔐 Login exitoso
2. 📸 Captura automática de información
3. 🗄️ Almacenamiento en base de datos
4. ✅ Confirmación de captura
```

## 🗃️ **Tabla de Datos: `informacion_capturada`**

### **Estructura de la Tabla**
```sql
CREATE TABLE [dbo].[informacion_capturada](
    [IdInformacion] [uniqueidentifier] NOT NULL,
    [IdUrl] [uniqueidentifier] NOT NULL,
    [NombreCampo] [nvarchar](100) NOT NULL,
    [ValorCampo] [ntext] NULL,
    [TipoCampo] [nvarchar](50) NOT NULL,
    [SelectorCSS] [nvarchar](500) NOT NULL,
    [Orden] [int] NOT NULL,
    [Obligatorio] [bit] NOT NULL,
    [Activo] [bit] NOT NULL,
    [FechaCreacion] [datetime] NOT NULL
)
```

### **Campos Clave**
- **`IdUrl`**: Referencia a la tabla `urls_automatizacion`
- **`NombreCampo`**: Nombre descriptivo del campo a capturar
- **`TipoCampo`**: Tipo de elemento (input, text, select, etc.)
- **`SelectorCSS`**: Selector CSS para localizar el elemento
- **`Orden`**: Orden de captura
- **`Obligatorio`**: Si el campo es obligatorio para la captura

## 🎨 **Tipos de Campos Soportados**

### **1. Input Fields (`input`)**
- **Descripción**: Campos de entrada de texto
- **Ejemplo**: `input[placeholder="Nombre"]`
- **Valor capturado**: `value` o `placeholder`

### **2. Text Elements (`text`)**
- **Descripción**: Elementos de texto estático
- **Ejemplo**: `h1, .titulo-pagina`
- **Valor capturado**: `textContent`

### **3. Select Elements (`select`)**
- **Descripción**: Listas desplegables
- **Ejemplo**: `select[name="pais"]`
- **Valor capturado**: Opción seleccionada

## 📋 **Campos Configurados para PAN AMERICAN LIFE DE ECUADOR**

### **Campos de Formulario**
| Orden | Nombre del Campo | Tipo | Selector CSS | Obligatorio |
|-------|------------------|------|--------------|-------------|
| 1 | Nombre del Paciente | input | `input[placeholder="Nombre"]` | No |
| 2 | Apellido del Paciente | input | `input[placeholder="Apellido"]` | No |
| 3 | **Identificación del Titular** | input | `#ContenidoPrincipal_CtrlBuscaAseguradoProv_txtIdentificacionAseg` | **Sí** |
| 4 | Número de Póliza | input | `input[placeholder="Póliza"]` | No |
| 5 | Número de Certificado | input | `input[placeholder="Certificado"]` | No |

### **Elementos de Interfaz**
| Orden | Nombre del Campo | Tipo | Selector CSS | Obligatorio |
|-------|------------------|------|--------------|-------------|
| 6 | Título de la Página | text | `h1, .info-asegurado-titulo` | No |
| 7 | Logo Empresa | text | `.logo, img[alt*="benefits"]` | No |
| 8 | Botón Nueva Búsqueda | text | `button:contains("NUEVA BÚSQUEDA")` | No |
| 9 | Botón Buscar Pólizas | text | `button:contains("BUSCAR PÓLIZAS")` | No |

### **Elementos de Navegación**
| Orden | Nombre del Campo | Tipo | Selector CSS | Obligatorio |
|-------|------------------|------|--------------|-------------|
| 10 | Idioma Seleccionado | text | `.idioma-activo, [data-lang="es"]` | No |
| 11 | País Seleccionado | text | `.pais-activo, [data-country="EC"]` | No |
| 12 | Menú Mis Pólizas | text | `a:contains("Mis Pólizas")` | No |
| 13 | Menú Reclamos | text | `a:contains("Reclamos")` | No |
| 14 | Menú PreAutorizaciones | text | `a:contains("PreAutorizaciones")` | No |

## 🚀 **Implementación Técnica**

### **Método Principal**
```python
def capturar_informacion_pantalla(self, id_url):
    """Captura información de la pantalla post-login"""
```

### **Proceso de Captura**
1. **Consulta Base de Datos**: Obtiene campos configurados para `id_url`
2. **Navegación por Elementos**: Recorre cada campo en orden
3. **Localización**: Usa Selenium para encontrar elementos por CSS selector
4. **Extracción**: Captura valores según el tipo de campo
5. **Validación**: Verifica campos obligatorios
6. **Logging**: Registra el proceso de captura

### **Manejo de Errores**
- **Campos Obligatorios**: Si fallan, la captura se detiene
- **Campos Opcionales**: Si fallan, se registra warning pero continúa
- **Timeouts**: Espera máxima de 10 segundos por elemento

## 📊 **Ejemplo de Uso**

### **1. Configurar Campos en Base de Datos**
```sql
-- Ejecutar el script SQL de ejemplo
-- aseguradoras/pan_american_life_ecuador/datos_ejemplo_informacion_capturada.sql
```

### **2. Ejecutar el Worker**
```bash
python run_production_worker.py
```

### **3. Resultado Esperado**
```
✅ Login completado exitosamente!
📸 Capturando información de la pantalla post-login...
🎯 Campos a capturar: 15
🔍 Capturando campo: Nombre del Paciente (input)
✅ Campo Nombre del Paciente capturado: Nombre...
🔍 Capturando campo: Apellido del Paciente (input)
✅ Campo Apellido del Paciente capturado: Apellido...
...
✅ Información de la pantalla capturada exitosamente
```

## 🔧 **Personalización**

### **Agregar Nuevos Campos**
1. **Insertar en Base de Datos**:
```sql
INSERT INTO [dbo].[informacion_capturada] 
([IdInformacion], [IdUrl], [NombreCampo], [ValorCampo], [TipoCampo], [SelectorCSS], [Orden], [Obligatorio], [Activo], [FechaCreacion])
VALUES
(NEWID(), 'E2D185C1-F1F0-46F4-A074-F115DE74A9AD', 'Nuevo Campo', 'Valor', 'input', 'selector_css', 16, 0, 1, GETDATE());
```

2. **Verificar Selector CSS**: Usar herramientas de desarrollador del navegador
3. **Probar Captura**: Ejecutar el worker para verificar

### **Modificar Campos Existentes**
```sql
UPDATE [dbo].[informacion_capturada]
SET SelectorCSS = 'nuevo_selector',
    Obligatorio = 1,
    Orden = 5
WHERE IdUrl = 'E2D185C1-F1F0-46F4-A074-F115DE74A9AD'
AND NombreCampo = 'Nombre del Campo';
```

## 📝 **Logs y Monitoreo**

### **Niveles de Log**
- **INFO**: Proceso normal de captura
- **WARNING**: Campos opcionales no encontrados
- **ERROR**: Campos obligatorios no encontrados o errores críticos

### **Métricas de Captura**
- Total de campos configurados
- Campos capturados exitosamente
- Campos que fallaron
- Tiempo total de captura

## 🚨 **Consideraciones Importantes**

### **Selectores CSS**
- **Específicos**: Usar selectores únicos cuando sea posible
- **Robustos**: Evitar selectores que cambien frecuentemente
- **Fallbacks**: Considerar múltiples selectores para elementos críticos

### **Campos Obligatorios**
- **Mínimo**: Solo marcar como obligatorios los campos esenciales
- **Validación**: Verificar que los selectores sean correctos
- **Testing**: Probar en diferentes estados de la página

### **Performance**
- **Orden**: Campos más importantes primero
- **Timeouts**: Ajustar según la velocidad de la página
- **Caché**: Reutilizar información cuando sea posible

## 🔄 **Próximas Mejoras**

- [ ] **Almacenamiento en Base de Datos**: Guardar valores capturados
- [ ] **Validación de Datos**: Verificar formato y contenido
- [ ] **Captura de Imágenes**: Screenshots de elementos
- [ ] **Comparación Temporal**: Detectar cambios en la interfaz
- [ ] **Reportes Automáticos**: Generar reportes de captura

---

**Desarrollado por**: Sistema de Automatización  
**Última actualización**: Enero 2025  
**Estado**: Funcional ✅
