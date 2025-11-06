# 🏨 Sistema de Reservas de Hotel

Sistema completo de reservas de hotel con backend en FastAPI, incluyendo búsqueda, reservas, pago simulado y gestión de usuarios.

## 📋 Características Principales

### Módulos Implementados:

1. **👤 Gestión de Usuarios**
   - Registro de usuarios con validación
   - Login con tokens de sesión (7 días de validez)
   - Autenticación mediante Bearer Token

2. **🔍 Búsqueda de Habitaciones**
   - Búsqueda por rango de fechas
   - Filtrado por tipo (simple, doble, suite)
   - Validación de capacidad de huéspedes
   - Verificación de disponibilidad en tiempo real

3. **📅 Sistema de Reservas**
   - Validación automática de disponibilidad
   - Prevención de doble reserva
   - Cálculo automático de precios
   - Estados de reserva (pendiente, confirmada, cancelada)

4. **💳 Simulación de Pago**
   - Validación de datos de tarjeta
   - Generación de código de transacción
   - Confirmación automática de reserva
   - Registro completo del pago

5. **🗄️ Base de Datos SQLite**
   - 5 tablas relacionadas:
     - `usuarios`: Información de usuarios
     - `sesiones`: Tokens de autenticación
     - `habitaciones`: Catálogo de habitaciones
     - `reservas`: Reservas realizadas
     - `pagos`: Transacciones de pago

## 🚀 Instalación y Ejecución

### Requisitos Previos
- Python 3.8 o superior
- pip (gestor de paquetes de Python)

### Paso 1: Instalar dependencias

```bash
pip install -r requirements.txt
```

### Paso 2: Iniciar el servidor

```bash
python hotel_booking_system.py
```

El servidor se iniciará en: **http://localhost:8000**

### Paso 3: Probar el sistema

En otra terminal, ejecuta el cliente de prueba:

```bash
python test_client.py
```

## 📚 API Endpoints

### Endpoints Públicos (sin autenticación):

- `GET /` - Información del sistema
- `POST /register` - Registrar nuevo usuario
- `POST /login` - Iniciar sesión
- `GET /tipos-habitacion` - Obtener tipos de habitación

### Endpoints Protegidos (requieren token):

- `POST /buscar` - Buscar habitaciones disponibles
- `POST /reservar` - Crear nueva reserva
- `POST /pagar` - Procesar pago de reserva
- `GET /mis-reservas` - Consultar reservas del usuario

## 📖 Ejemplos de Uso

### 1. Registrar Usuario

```bash
curl -X POST http://localhost:8000/register \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "password123",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "+57 300 1234567"
  }'
```

### 2. Iniciar Sesión

```bash
curl -X POST http://localhost:8000/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "usuario@ejemplo.com",
    "password": "password123"
  }'
```

### 3. Buscar Habitaciones

```bash
curl -X POST http://localhost:8000/buscar \
  -H "Content-Type: application/json" \
  -d '{
    "fecha_inicio": "2025-11-15",
    "fecha_fin": "2025-11-18",
    "tipo_habitacion": "doble",
    "huespedes": 2
  }'
```

### 4. Crear Reserva (requiere token)

```bash
curl -X POST http://localhost:8000/reservar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "habitacion_id": 1,
    "fecha_inicio": "2025-11-15",
    "fecha_fin": "2025-11-18",
    "huespedes": 2
  }'
```

### 5. Procesar Pago (requiere token)

```bash
curl -X POST http://localhost:8000/pagar \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_TOKEN_AQUI" \
  -d '{
    "reserva_id": 1,
    "metodo_pago": "tarjeta_credito",
    "numero_tarjeta": "4532123456789012",
    "cvv": "123",
    "nombre_titular": "Juan Pérez"
  }'
```

## 🗄️ Estructura de la Base de Datos

### Tabla: usuarios
- `id` (PK)
- `email` (UNIQUE)
- `password_hash`
- `nombre`, `apellido`, `telefono`
- `fecha_registro`, `activo`

### Tabla: sesiones
- `id` (PK)
- `usuario_id` (FK → usuarios)
- `token` (UNIQUE)
- `fecha_creacion`, `fecha_expiracion`
- `activa`

### Tabla: habitaciones
- `id` (PK)
- `numero` (UNIQUE)
- `tipo` (simple/doble/suite)
- `capacidad`, `precio_noche`
- `descripcion`, `disponible`

### Tabla: reservas
- `id` (PK)
- `usuario_id` (FK → usuarios)
- `habitacion_id` (FK → habitaciones)
- `fecha_inicio`, `fecha_fin`
- `huespedes`, `precio_total`
- `estado`, `fecha_reserva`

### Tabla: pagos
- `id` (PK)
- `reserva_id` (FK → reservas)
- `monto`, `metodo_pago`
- `ultimos_4_digitos`
- `estado`, `codigo_transaccion`
- `fecha_pago`

## 🎯 Habitaciones Disponibles

El sistema incluye 10 habitaciones pre-configuradas:

- **Simple** (101, 102, 103): $50-55/noche - 1 huésped
- **Doble** (201-204): $80-90/noche - 2 huéspedes
- **Suite** (301-303): $130-160/noche - 3-4 huéspedes

## 🔒 Seguridad

- Contraseñas hasheadas con SHA-256
- Tokens seguros con `secrets.token_urlsafe()`
- Validación de sesiones activas
- Expiración de tokens (7 días)
- Validación de datos en todos los endpoints

## 📊 Validaciones Implementadas

1. **Fechas**: No se permiten fechas pasadas o inválidas
2. **Disponibilidad**: Prevención de dobles reservas
3. **Capacidad**: Verificación de número de huéspedes
4. **Pago**: Validación básica de tarjetas (16 dígitos, CVV 3 dígitos)
5. **Autenticación**: Tokens requeridos para operaciones sensibles

## 📖 Documentación Interactiva

Una vez iniciado el servidor, visita:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🧪 Testing

Para ejecutar las pruebas automatizadas (FASE 2):

```bash
pytest tests/ -v --html=report.html
```

## 📝 Notas Técnicas

- **Framework**: FastAPI 0.104.1
- **Base de datos**: SQLite3 (archivo: hotel_booking.db)
- **Autenticación**: Bearer Token con HTTPBearer
- **Validación**: Pydantic models
- **CORS**: Habilitado para todos los orígenes

## 🏗️ Próximos Pasos (FASE 2)

1. Documentar funcionalidades críticas
2. Calcular RPN (Severidad × Ocurrencia × Detección)
3. Crear plan de pruebas según IEEE 829
4. Implementar suite de pruebas automatizadas
5. Generar dashboard de métricas

---

# 📊 FASE 2: Sistema de Métricas de Testing

Sistema completo de métricas, análisis de tendencias y simulación de 5 días de testing para el Sistema de Reservas de Hotel.

## 🎯 Componentes Implementados

### 1. Sistema de Métricas (`metricas_testing.py`)

Clase `MetricasTesting` con **8 indicadores principales**:

1. **Cobertura de Pruebas** = (Casos Ejecutados / Casos Planificados) × 100
   - Meta: ≥ 85%

2. **Tasa de Éxito** = (Casos Pasados / Casos Ejecutados) × 100
   - Meta: ≥ 90%

3. **Densidad de Defectos** = (Total Defectos / Casos Ejecutados) × 100
   - Meta: ≤ 15 defectos por 100 casos

4. **Efectividad del Testing** = (Defectos Encontrados / Total Defectos Potenciales) × 100
   - Meta: ≥ 80%

5. **Tasa de Resolución** = (Defectos Resueltos / Defectos Abiertos) × 100
   - Meta: ≥ 70%

6. **Backlog de Defectos** = Defectos Abiertos - Defectos Resueltos
   - Meta: Tendencia descendente

7. **Velocidad de Testing** = Casos Ejecutados / Día
   - Meta: Tendencia estable o ascendente

8. **Índice de Calidad** = (Tasa Éxito × 0.4) + ((100 - Densidad) × 0.3) + (Cobertura × 0.3)
   - Meta: ≥ 80

### 2. Dashboard Visual (`dashboard_visual.py`)

Genera visualizaciones con **matplotlib**:
- Gráficos de tendencia de todas las métricas
- Semáforos de estado (verde/amarillo/rojo)
- Distribución de casos y defectos
- Tablas resumen históricas
- Reportes HTML interactivos

### 3. Simulador de 5 Días (`simulador_5_dias.py`)

Simula proceso completo de testing:
- Genera dataset de 500 defectos
- Simula ejecución diaria de casos
- Toma decisiones basadas en métricas
- Evalúa criterios de salida
- Genera snapshots diarios

## 🚀 Instalación

```bash
pip install pandas matplotlib numpy
```

O usando el archivo de requisitos:

```bash
pip install -r requirements.txt
```

## 📖 Uso

### Opción 1: Ejecutar Simulación Completa

```bash
python simulador_5_dias.py
```

Esto ejecutará:
1. Generación de dataset de 500 defectos
2. Simulación de 5 días de testing
3. Toma de decisiones diarias
4. Generación de dashboards y reportes
5. Evaluación de criterios de salida

### Opción 2: Sistema de Métricas Individual

```python
from metricas_testing import MetricasTesting

# Crear sistema
sistema = MetricasTesting()

# Registrar métricas de un día
metricas = {
    'casos_planificados': 100,
    'casos_ejecutados': 85,
    'casos_pasados': 75,
    'casos_fallados': 8,
    'casos_bloqueados': 2,
    'defectos_nuevos': 10,
    'defectos_abiertos': 15,
    'defectos_resueltos': 5,
    'defectos_criticos': 1,
    'defectos_altos': 3,
    'defectos_medios': 4,
    'defectos_bajos': 2
}

dia = sistema.registrar_dia(metricas)

# Ver reporte
print(sistema.generar_reporte_dia())

# Analizar tendencias
tendencias = sistema.analizar_todas_tendencias()
print(tendencias)

# Evaluar criterios de salida
cumple, razones = sistema.criterios_salida()
print(f"Cumple criterios: {cumple}")
```

### Opción 3: Dashboard Visual

```python
from metricas_testing import MetricasTesting
from dashboard_visual import DashboardVisual

# Cargar datos
sistema = MetricasTesting()

# Crear dashboard
dashboard = DashboardVisual(sistema)

# Generar gráficos
dashboard.generar_dashboard_completo("mi_dashboard.png")

# Generar reporte HTML
dashboard.generar_reporte_html("mi_reporte.html")
```

## 📊 Análisis de Tendencias

El sistema detecta automáticamente tendencias en las métricas:

```python
# Detectar tendencia de una métrica específica
tendencia = sistema.detectar_tendencia('cobertura', ventana=3)
# Retorna: 'ascendente', 'descendente', 'estable' o 'insuficiente_datos'

# Analizar todas las tendencias
todas = sistema.analizar_todas_tendencias()
# Retorna dict con tendencias de todas las métricas clave
```

## ✅ Criterios de Salida

El sistema evalúa 7 criterios para determinar si se puede liberar a producción:

1. **Cobertura mínima**: ≥ 85%
2. **Tasa de éxito mínima**: ≥ 90%
3. **Defectos críticos**: 0
4. **Defectos altos**: ≤ 2
5. **Densidad de defectos**: ≤ 15
6. **Tendencia de defectos**: Descendente o estable
7. **Estabilidad**: 2 días consecutivos sin críticos

```python
cumple, razones = sistema.criterios_salida()

if cumple:
    print("✅ Sistema listo para producción")
else:
    print("❌ No cumple criterios:")
    for razon in razones:
        print(f"  • {razon}")
```

## 📁 Archivos Generados

Después de ejecutar la simulación completa:

```
proyecto/
├── dataset_defectos.csv          # 500 defectos simulados
├── simulacion_5_dias.json        # Datos históricos
├── dashboard_dia_1.png           # Dashboard día 1
├── dashboard_dia_2.png           # Dashboard día 2
├── dashboard_dia_3.png           # Dashboard día 3
├── dashboard_dia_4.png           # Dashboard día 4
├── dashboard_dia_5.png           # Dashboard día 5
├── dashboard_final.png           # Dashboard consolidado
├── reporte_dia_1.html            # Reporte HTML día 1
├── reporte_dia_2.html            # Reporte HTML día 2
├── reporte_dia_3.html            # Reporte HTML día 3
├── reporte_dia_4.html            # Reporte HTML día 4
├── reporte_dia_5.html            # Reporte HTML día 5
└── reporte_final.html            # Reporte ejecutivo final
```

## 🎯 Ejemplo de Salida

```
📅 DÍA 1 - 2025-11-06
======================================================================

📊 RESUMEN DEL DÍA 1
├─ Casos ejecutados: 60/100 (60.0%)
├─ Casos pasados: 45 (75.0%)
├─ Casos fallados: 12
├─ Nuevos defectos: 15
│  ├─ Críticos: 2
│  ├─ Altos: 5
│  ├─ Medios: 6
│  └─ Bajos: 2
├─ Defectos abiertos: 15
├─ Defectos resueltos: 0
└─ Índice de calidad: 68.5

🎯 DECISIÓN DEL DÍA
├─ Acción: CONTINUAR CON TESTING INTENSIVO
├─ Justificación: Primer día de ejecución, fase de descubrimiento
└─ Recomendaciones:
   • Priorizar pruebas de funcionalidad crítica
   • Documentar todos los defectos encontrados
   • Establecer reunión diaria con desarrollo

⚠️ CRITERIOS DE SALIDA: NO CUMPLIDOS
Razones de incumplimiento:
   • Cobertura insuficiente: 60.0% (min: 85.0%)
   • Tasa de éxito baja: 75.0% (min: 90.0%)
   • Defectos críticos abiertos: 2
   • ...
```

## 🔧 Configuración Avanzada

### Personalizar Criterios de Salida

```python
sistema = MetricasTesting()

# Modificar criterios
sistema.criterios_salida = {
    "cobertura_minima": 90.0,          # Más estricto
    "tasa_exito_minima": 95.0,         # Más estricto
    "defectos_criticos_max": 0,
    "defectos_altos_max": 1,           # Más estricto
    "densidad_defectos_max": 10.0,     # Más estricto
    "tendencia_defectos": "descendente",
    "dias_consecutivos_estables": 3     # Más días requeridos
}
```

### Personalizar Colores del Dashboard

```python
dashboard = DashboardVisual(sistema)

# Modificar paleta de colores
dashboard.colores = {
    'exito': '#00ff00',
    'warning': '#ffaa00',
    'critico': '#ff0000',
    'info': '#0000ff',
    'neutro': '#808080'
}
```

## 📈 Interpretación de Resultados

### Semáforo de Estado

- 🟢 **Verde**: Métrica cumple objetivo
- 🟡 **Amarillo**: Métrica cercana al objetivo, requiere monitoreo
- 🔴 **Rojo**: Métrica no cumple objetivo, requiere acción inmediata

### Tendencias

- **↑ Ascendente**: El valor está aumentando
- **↓ Descendente**: El valor está disminuyendo
- **→ Estable**: El valor se mantiene constante

**Nota**: Algunas tendencias ascendentes son buenas (cobertura, tasa de éxito) y otras son malas (densidad de defectos, defectos abiertos).

## 🐛 Resolución de Problemas

### Error: No se puede importar matplotlib

```bash
pip install matplotlib
```

### Error: No se encuentra el archivo JSON

El sistema crea automáticamente el archivo en la primera ejecución. Si quieres resetear:

```python
import os
if os.path.exists("metricas_historico.json"):
    os.remove("metricas_historico.json")
```

### Las gráficas no se muestran

Asegúrate de tener un entorno gráfico. Si estás en servidor sin GUI:

```python
import matplotlib
matplotlib.use('Agg')  # Backend sin GUI
```

## 📚 Referencias

- **IEEE 829**: Estándar para documentación de testing
- **pandas**: Análisis de datos
- **matplotlib**: Visualización de datos
- **numpy**: Cálculos numéricos

## 🎓 Conceptos Clave

### Métricas de Proceso vs Producto

- **Proceso**: Cobertura, velocidad, eficiencia
- **Producto**: Densidad de defectos, calidad, estabilidad

### Análisis de Tendencias

El sistema usa ventanas deslizantes de 3 días para detectar tendencias, evitando ruido en datos puntuales.

### Criterios de Salida

Basados en estándares de la industria y mejores prácticas de testing.

---

**Desarrollado para el proyecto de Testing de Software**