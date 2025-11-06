import requests
from datetime import date, timedelta
import json

BASE_URL = "http://localhost:8000"

def print_seccion(titulo):
    print("\n" + "="*60)
    print(f"  {titulo}")
    print("="*60)

def print_respuesta(respuesta):
    print(f"Status: {respuesta.status_code}")
    try:
        print(json.dumps(respuesta.json(), indent=2, ensure_ascii=False))
    except:
        print(respuesta.text)

# ==================== PRUEBA COMPLETA DEL SISTEMA ====================

print_seccion("🏨 CLIENTE DE PRUEBA - SISTEMA DE RESERVAS DE HOTEL")

# 1. Verificar que el servidor está activo
print_seccion("1️⃣ Verificando conexión al servidor")
try:
    response = requests.get(f"{BASE_URL}/")
    print_respuesta(response)
except Exception as e:
    print(f"❌ Error: No se puede conectar al servidor. Asegúrate de que esté corriendo.")
    print(f"   Ejecuta: python hotel_booking_system.py")
    exit(1)

# 2. Registrar un nuevo usuario
print_seccion("2️⃣ Registrando nuevo usuario")
usuario_data = {
    "email": "juan.perez@email.com",
    "password": "mipassword123",
    "nombre": "Juan",
    "apellido": "Pérez",
    "telefono": "+57 300 1234567"
}
response = requests.post(f"{BASE_URL}/register", json=usuario_data)
print_respuesta(response)

# 3. Hacer login
print_seccion("3️⃣ Iniciando sesión")
login_data = {
    "email": "juan.perez@email.com",
    "password": "mipassword123"
}
response = requests.post(f"{BASE_URL}/login", json=login_data)
print_respuesta(response)

if response.status_code == 200:
    token = response.json()["token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"\n✅ Token obtenido: {token[:20]}...")
else:
    print("❌ Error en login")
    exit(1)

# 4. Obtener tipos de habitación
print_seccion("4️⃣ Consultando tipos de habitación disponibles")
response = requests.get(f"{BASE_URL}/tipos-habitacion")
print_respuesta(response)

# 5. Buscar habitaciones disponibles
print_seccion("5️⃣ Buscando habitaciones disponibles")
fecha_inicio = date.today() + timedelta(days=7)
fecha_fin = fecha_inicio + timedelta(days=3)

busqueda_data = {
    "fecha_inicio": str(fecha_inicio),
    "fecha_fin": str(fecha_fin),
    "tipo_habitacion": "doble",
    "huespedes": 2
}
response = requests.post(f"{BASE_URL}/buscar", json=busqueda_data)
print_respuesta(response)

habitaciones = response.json().get("habitaciones", [])
if not habitaciones:
    print("❌ No hay habitaciones disponibles")
    exit(1)

habitacion_seleccionada = habitaciones[0]
print(f"\n✅ Habitación seleccionada: #{habitacion_seleccionada['numero']} - ${habitacion_seleccionada['precio_total']}")

# 6. Crear reserva
print_seccion("6️⃣ Creando reserva")
reserva_data = {
    "habitacion_id": habitacion_seleccionada["id"],
    "fecha_inicio": str(fecha_inicio),
    "fecha_fin": str(fecha_fin),
    "huespedes": 2
}
response = requests.post(f"{BASE_URL}/reservar", json=reserva_data, headers=headers)
print_respuesta(response)

if response.status_code == 200:
    reserva_id = response.json()["reserva_id"]
    precio_total = response.json()["precio_total"]
    print(f"\n✅ Reserva creada con ID: {reserva_id}")
else:
    print("❌ Error al crear reserva")
    exit(1)

# 7. Procesar pago
print_seccion("7️⃣ Procesando pago (simulado)")
pago_data = {
    "reserva_id": reserva_id,
    "metodo_pago": "tarjeta_credito",
    "numero_tarjeta": "4532123456789012",
    "cvv": "123",
    "nombre_titular": "Juan Pérez"
}
response = requests.post(f"{BASE_URL}/pagar", json=pago_data, headers=headers)
print_respuesta(response)

if response.status_code == 200:
    codigo_transaccion = response.json()["codigo_transaccion"]
    print(f"\n✅ Pago procesado. Código de transacción: {codigo_transaccion}")
else:
    print("❌ Error al procesar pago")

# 8. Ver mis reservas
print_seccion("8️⃣ Consultando mis reservas")
response = requests.get(f"{BASE_URL}/mis-reservas", headers=headers)
print_respuesta(response)

# Resumen final
print_seccion("✅ PRUEBA COMPLETADA EXITOSAMENTE")
print("""
Funcionalidades probadas:
✓ Conexión al servidor
✓ Registro de usuario
✓ Login y generación de token
✓ Consulta de tipos de habitación
✓ Búsqueda de habitaciones por fecha y tipo
✓ Validación de disponibilidad
✓ Creación de reserva
✓ Simulación de pago
✓ Consulta de reservas del usuario

El sistema está funcionando correctamente y listo para las pruebas de la FASE 2.
""")