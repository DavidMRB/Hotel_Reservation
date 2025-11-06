from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, EmailStr, Field
from datetime import datetime, date, timedelta
from typing import Optional, List
import sqlite3
import hashlib
import secrets
import json
from contextlib import contextmanager

app = FastAPI(title="Hotel Booking System", version="1.0.0")

# Configurar CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# ==================== MODELOS PYDANTIC ====================

class UserRegister(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6)
    nombre: str
    apellido: str
    telefono: str

class UserLogin(BaseModel):
    email: EmailStr
    password: str

class BusquedaHabitaciones(BaseModel):
    fecha_inicio: date
    fecha_fin: date
    tipo_habitacion: Optional[str] = None
    huespedes: Optional[int] = 1

class ReservaCreate(BaseModel):
    habitacion_id: int
    fecha_inicio: date
    fecha_fin: date
    huespedes: int
    
class PagoSimulado(BaseModel):
    reserva_id: int
    metodo_pago: str
    numero_tarjeta: str
    cvv: str
    nombre_titular: str

# ==================== BASE DE DATOS ====================

DATABASE = "hotel_booking.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DATABASE)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        raise e
    finally:
        conn.close()

def init_database():
    """Inicializar base de datos con 5 tablas relacionadas"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Tabla 1: Usuarios
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                email TEXT UNIQUE NOT NULL,
                password_hash TEXT NOT NULL,
                nombre TEXT NOT NULL,
                apellido TEXT NOT NULL,
                telefono TEXT,
                fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                activo BOOLEAN DEFAULT 1
            )
        """)
        
        # Tabla 2: Sesiones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sesiones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                token TEXT UNIQUE NOT NULL,
                fecha_creacion TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                fecha_expiracion TIMESTAMP NOT NULL,
                activa BOOLEAN DEFAULT 1,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id)
            )
        """)
        
        # Tabla 3: Habitaciones
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS habitaciones (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                numero TEXT UNIQUE NOT NULL,
                tipo TEXT NOT NULL,
                capacidad INTEGER NOT NULL,
                precio_noche REAL NOT NULL,
                descripcion TEXT,
                disponible BOOLEAN DEFAULT 1
            )
        """)
        
        # Tabla 4: Reservas
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS reservas (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                usuario_id INTEGER NOT NULL,
                habitacion_id INTEGER NOT NULL,
                fecha_inicio DATE NOT NULL,
                fecha_fin DATE NOT NULL,
                huespedes INTEGER NOT NULL,
                precio_total REAL NOT NULL,
                estado TEXT DEFAULT 'pendiente',
                fecha_reserva TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (usuario_id) REFERENCES usuarios(id),
                FOREIGN KEY (habitacion_id) REFERENCES habitaciones(id)
            )
        """)
        
        # Tabla 5: Pagos
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS pagos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                reserva_id INTEGER NOT NULL,
                monto REAL NOT NULL,
                metodo_pago TEXT NOT NULL,
                ultimos_4_digitos TEXT,
                estado TEXT DEFAULT 'procesando',
                fecha_pago TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                codigo_transaccion TEXT UNIQUE,
                FOREIGN KEY (reserva_id) REFERENCES reservas(id)
            )
        """)
        
        # Insertar habitaciones de ejemplo si no existen
        cursor.execute("SELECT COUNT(*) FROM habitaciones")
        if cursor.fetchone()[0] == 0:
            habitaciones_ejemplo = [
                ('101', 'simple', 1, 50.0, 'Habitación individual con cama simple'),
                ('102', 'simple', 1, 50.0, 'Habitación individual con cama simple'),
                ('201', 'doble', 2, 80.0, 'Habitación doble con dos camas individuales'),
                ('202', 'doble', 2, 85.0, 'Habitación doble con cama matrimonial'),
                ('203', 'doble', 2, 80.0, 'Habitación doble con vista al jardín'),
                ('301', 'suite', 4, 150.0, 'Suite presidencial con sala y jacuzzi'),
                ('302', 'suite', 3, 130.0, 'Suite junior con balcón'),
                ('103', 'simple', 1, 55.0, 'Habitación individual premium'),
                ('204', 'doble', 2, 90.0, 'Habitación doble deluxe'),
                ('303', 'suite', 4, 160.0, 'Suite familiar con dos habitaciones'),
            ]
            cursor.executemany(
                "INSERT INTO habitaciones (numero, tipo, capacidad, precio_noche, descripcion) VALUES (?, ?, ?, ?, ?)",
                habitaciones_ejemplo
            )

# ==================== UTILIDADES ====================

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode()).hexdigest()

def generate_token() -> str:
    return secrets.token_urlsafe(32)

def verificar_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    token = credentials.credentials
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT s.usuario_id, u.email, u.nombre 
            FROM sesiones s
            JOIN usuarios u ON s.usuario_id = u.id
            WHERE s.token = ? AND s.activa = 1 AND s.fecha_expiracion > datetime('now')
        """, (token,))
        result = cursor.fetchone()
        
        if not result:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token inválido o expirado"
            )
        
        return {
            "usuario_id": result[0],
            "email": result[1],
            "nombre": result[2]
        }

# ==================== ENDPOINTS ====================

@app.on_event("startup")
async def startup_event():
    init_database()
    print("✅ Base de datos inicializada")

@app.get("/")
async def root():
    return {
        "mensaje": "Sistema de Reservas de Hotel API",
        "version": "1.0.0",
        "endpoints": ["/register", "/login", "/buscar", "/reservar", "/pagar"]
    }

@app.post("/register")
async def registrar_usuario(usuario: UserRegister):
    """Registro de nuevo usuario"""
    try:
        with get_db() as conn:
            cursor = conn.cursor()
            cursor.execute(
                """INSERT INTO usuarios (email, password_hash, nombre, apellido, telefono)
                   VALUES (?, ?, ?, ?, ?)""",
                (usuario.email, hash_password(usuario.password), usuario.nombre, 
                 usuario.apellido, usuario.telefono)
            )
            usuario_id = cursor.lastrowid
            
            return {
                "success": True,
                "mensaje": "Usuario registrado exitosamente",
                "usuario_id": usuario_id
            }
    except sqlite3.IntegrityError:
        raise HTTPException(status_code=400, detail="El email ya está registrado")

@app.post("/login")
async def login(credenciales: UserLogin):
    """Login y generación de token de sesión"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT id, nombre FROM usuarios WHERE email = ? AND password_hash = ? AND activo = 1",
            (credenciales.email, hash_password(credenciales.password))
        )
        usuario = cursor.fetchone()
        
        if not usuario:
            raise HTTPException(
                status_code=401,
                detail="Credenciales inválidas"
            )
        
        # Crear sesión
        token = generate_token()
        fecha_expiracion = datetime.now() + timedelta(days=7)
        
        cursor.execute(
            """INSERT INTO sesiones (usuario_id, token, fecha_expiracion)
               VALUES (?, ?, ?)""",
            (usuario[0], token, fecha_expiracion)
        )
        
        return {
            "success": True,
            "token": token,
            "usuario": {
                "id": usuario[0],
                "nombre": usuario[1],
                "email": credenciales.email
            },
            "expira": fecha_expiracion.isoformat()
        }

@app.post("/buscar")
async def buscar_habitaciones(busqueda: BusquedaHabitaciones):
    """Búsqueda de habitaciones disponibles por fecha y tipo"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Validar fechas
        if busqueda.fecha_inicio >= busqueda.fecha_fin:
            raise HTTPException(status_code=400, detail="La fecha de fin debe ser posterior a la fecha de inicio")
        
        if busqueda.fecha_inicio < date.today():
            raise HTTPException(status_code=400, detail="No se pueden buscar fechas pasadas")
        
        # Construir query
        query = """
            SELECT h.* FROM habitaciones h
            WHERE h.disponible = 1
            AND h.capacidad >= ?
            AND h.id NOT IN (
                SELECT habitacion_id FROM reservas
                WHERE estado IN ('confirmada', 'pendiente')
                AND (
                    (fecha_inicio <= ? AND fecha_fin > ?)
                    OR (fecha_inicio < ? AND fecha_fin >= ?)
                    OR (fecha_inicio >= ? AND fecha_fin <= ?)
                )
            )
        """
        
        params = [
            busqueda.huespedes,
            busqueda.fecha_inicio, busqueda.fecha_inicio,
            busqueda.fecha_fin, busqueda.fecha_fin,
            busqueda.fecha_inicio, busqueda.fecha_fin
        ]
        
        if busqueda.tipo_habitacion:
            query += " AND h.tipo = ?"
            params.append(busqueda.tipo_habitacion)
        
        query += " ORDER BY h.tipo, h.precio_noche"
        
        cursor.execute(query, params)
        habitaciones = cursor.fetchall()
        
        # Calcular noches y precio total
        noches = (busqueda.fecha_fin - busqueda.fecha_inicio).days
        
        resultado = []
        for hab in habitaciones:
            resultado.append({
                "id": hab[0],
                "numero": hab[1],
                "tipo": hab[2],
                "capacidad": hab[3],
                "precio_noche": hab[4],
                "precio_total": hab[4] * noches,
                "noches": noches,
                "descripcion": hab[5]
            })
        
        return {
            "success": True,
            "habitaciones_disponibles": len(resultado),
            "fecha_inicio": str(busqueda.fecha_inicio),
            "fecha_fin": str(busqueda.fecha_fin),
            "noches": noches,
            "habitaciones": resultado
        }

@app.post("/reservar")
async def crear_reserva(reserva: ReservaCreate, usuario_actual = Depends(verificar_token)):
    """Crear nueva reserva con validación de disponibilidad"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Validar fechas
        if reserva.fecha_inicio >= reserva.fecha_fin:
            raise HTTPException(status_code=400, detail="Fechas inválidas")
        
        # Verificar disponibilidad
        cursor.execute("""
            SELECT COUNT(*) FROM reservas
            WHERE habitacion_id = ?
            AND estado IN ('confirmada', 'pendiente')
            AND (
                (fecha_inicio <= ? AND fecha_fin > ?)
                OR (fecha_inicio < ? AND fecha_fin >= ?)
                OR (fecha_inicio >= ? AND fecha_fin <= ?)
            )
        """, (
            reserva.habitacion_id,
            reserva.fecha_inicio, reserva.fecha_inicio,
            reserva.fecha_fin, reserva.fecha_fin,
            reserva.fecha_inicio, reserva.fecha_fin
        ))
        
        if cursor.fetchone()[0] > 0:
            raise HTTPException(status_code=409, detail="Habitación no disponible en las fechas seleccionadas")
        
        # Obtener precio de habitación
        cursor.execute("SELECT precio_noche, capacidad FROM habitaciones WHERE id = ?", 
                      (reserva.habitacion_id,))
        habitacion = cursor.fetchone()
        
        if not habitacion:
            raise HTTPException(status_code=404, detail="Habitación no encontrada")
        
        if habitacion[1] < reserva.huespedes:
            raise HTTPException(status_code=400, detail="La habitación no tiene capacidad suficiente")
        
        # Calcular precio total
        noches = (reserva.fecha_fin - reserva.fecha_inicio).days
        precio_total = habitacion[0] * noches
        
        # Crear reserva
        cursor.execute("""
            INSERT INTO reservas (usuario_id, habitacion_id, fecha_inicio, fecha_fin, huespedes, precio_total, estado)
            VALUES (?, ?, ?, ?, ?, ?, 'pendiente')
        """, (
            usuario_actual["usuario_id"],
            reserva.habitacion_id,
            reserva.fecha_inicio,
            reserva.fecha_fin,
            reserva.huespedes,
            precio_total
        ))
        
        reserva_id = cursor.lastrowid
        
        return {
            "success": True,
            "mensaje": "Reserva creada exitosamente",
            "reserva_id": reserva_id,
            "precio_total": precio_total,
            "noches": noches,
            "estado": "pendiente"
        }

@app.post("/pagar")
async def procesar_pago(pago: PagoSimulado, usuario_actual = Depends(verificar_token)):
    """Simulación de proceso de pago"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Verificar que la reserva existe y pertenece al usuario
        cursor.execute("""
            SELECT id, precio_total, estado FROM reservas
            WHERE id = ? AND usuario_id = ?
        """, (pago.reserva_id, usuario_actual["usuario_id"]))
        
        reserva = cursor.fetchone()
        
        if not reserva:
            raise HTTPException(status_code=404, detail="Reserva no encontrada")
        
        if reserva[2] != 'pendiente':
            raise HTTPException(status_code=400, detail="La reserva ya fue procesada")
        
        # Validaciones básicas de tarjeta (simuladas)
        if len(pago.numero_tarjeta) != 16 or not pago.numero_tarjeta.isdigit():
            raise HTTPException(status_code=400, detail="Número de tarjeta inválido")
        
        if len(pago.cvv) != 3 or not pago.cvv.isdigit():
            raise HTTPException(status_code=400, detail="CVV inválido")
        
        # Simular procesamiento de pago (siempre exitoso en esta versión)
        codigo_transaccion = f"TXN-{secrets.token_hex(8).upper()}"
        ultimos_4 = pago.numero_tarjeta[-4:]
        
        # Registrar pago
        cursor.execute("""
            INSERT INTO pagos (reserva_id, monto, metodo_pago, ultimos_4_digitos, estado, codigo_transaccion)
            VALUES (?, ?, ?, ?, 'aprobado', ?)
        """, (pago.reserva_id, reserva[1], pago.metodo_pago, ultimos_4, codigo_transaccion))
        
        # Actualizar estado de reserva
        cursor.execute("""
            UPDATE reservas SET estado = 'confirmada' WHERE id = ?
        """, (pago.reserva_id,))
        
        return {
            "success": True,
            "mensaje": "Pago procesado exitosamente",
            "codigo_transaccion": codigo_transaccion,
            "monto": reserva[1],
            "metodo_pago": pago.metodo_pago,
            "ultimos_4_digitos": ultimos_4,
            "estado": "aprobado"
        }

@app.get("/mis-reservas")
async def obtener_mis_reservas(usuario_actual = Depends(verificar_token)):
    """Obtener todas las reservas del usuario autenticado"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT r.id, r.fecha_inicio, r.fecha_fin, r.huespedes, r.precio_total, r.estado,
                   h.numero, h.tipo, h.descripcion
            FROM reservas r
            JOIN habitaciones h ON r.habitacion_id = h.id
            WHERE r.usuario_id = ?
            ORDER BY r.fecha_reserva DESC
        """, (usuario_actual["usuario_id"],))
        
        reservas = cursor.fetchall()
        
        resultado = []
        for r in reservas:
            resultado.append({
                "id": r[0],
                "fecha_inicio": r[1],
                "fecha_fin": r[2],
                "huespedes": r[3],
                "precio_total": r[4],
                "estado": r[5],
                "habitacion": {
                    "numero": r[6],
                    "tipo": r[7],
                    "descripcion": r[8]
                }
            })
        
        return {
            "success": True,
            "total_reservas": len(resultado),
            "reservas": resultado
        }

@app.get("/tipos-habitacion")
async def obtener_tipos_habitacion():
    """Obtener tipos de habitación disponibles"""
    return {
        "success": True,
        "tipos": [
            {"valor": "simple", "nombre": "Individual", "descripcion": "Para 1 persona"},
            {"valor": "doble", "nombre": "Doble", "descripcion": "Para 2 personas"},
            {"valor": "suite", "nombre": "Suite", "descripcion": "Para 3-4 personas"}
        ]
    }

# ==================== EJECUCIÓN ====================

if __name__ == "__main__":
    import uvicorn
    print("🏨 Iniciando servidor de Sistema de Reservas de Hotel...")
    print("📍 Servidor corriendo en: http://localhost:8000")
    print("📚 Documentación API: http://localhost:8000/docs")
    uvicorn.run(app, host="0.0.0.0", port=8000)