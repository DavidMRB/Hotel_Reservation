import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Tuple
import json
from dataclasses import dataclass, asdict
import os

@dataclass
class MetricasDia:
    """Métricas diarias del proceso de testing"""
    dia: int
    fecha: str
    
    # Métricas de ejecución
    casos_planificados: int
    casos_ejecutados: int
    casos_pasados: int
    casos_fallados: int
    casos_bloqueados: int
    
    # Métricas de defectos
    defectos_nuevos: int
    defectos_abiertos: int
    defectos_resueltos: int
    defectos_criticos: int
    defectos_altos: int
    defectos_medios: int
    defectos_bajos: int
    
    # Métricas calculadas
    cobertura: float = 0.0
    tasa_exito: float = 0.0
    densidad_defectos: float = 0.0
    efectividad_testing: float = 0.0
    tasa_resolucion: float = 0.0
    backlog_defectos: int = 0
    velocidad_testing: float = 0.0
    indice_calidad: float = 0.0


class MetricasTesting:
    """
    Sistema completo de métricas para testing
    Incluye 8 indicadores principales y análisis de tendencias
    """
    
    def __init__(self, archivo_historico: str = "metricas_historico.json"):
        self.archivo_historico = archivo_historico
        self.historico: List[MetricasDia] = []
        self.criterios_salida_config = {
            "cobertura_minima": 85.0,
            "tasa_exito_minima": 90.0,
            "defectos_criticos_max": 0,
            "defectos_altos_max": 2,
            "densidad_defectos_max": 15.0,
            "tendencia_defectos": "descendente",
            "dias_consecutivos_estables": 2
        }
        self.cargar_historico()
    
    def cargar_historico(self):
        """Cargar datos históricos desde archivo JSON"""
        if os.path.exists(self.archivo_historico):
            try:
                with open(self.archivo_historico, 'r', encoding='utf-8') as f:
                    datos = json.load(f)
                    self.historico = [MetricasDia(**m) for m in datos]
                print(f"✅ Histórico cargado: {len(self.historico)} días")
            except Exception as e:
                print(f"⚠️ Error al cargar histórico: {e}")
                self.historico = []
        else:
            self.historico = []
    
    def guardar_historico(self):
        """Guardar datos históricos en archivo JSON"""
        try:
            with open(self.archivo_historico, 'w', encoding='utf-8') as f:
                datos = [asdict(m) for m in self.historico]
                json.dump(datos, f, indent=2, ensure_ascii=False)
            print(f"💾 Histórico guardado: {len(self.historico)} días")
        except Exception as e:
            print(f"❌ Error al guardar histórico: {e}")
    
    def registrar_dia(self, metricas: Dict) -> MetricasDia:
        """
        Registrar métricas de un día y calcular indicadores
        
        Args:
            metricas: Diccionario con métricas del día
            
        Returns:
            MetricasDia con todos los indicadores calculados
        """
        dia = len(self.historico) + 1
        fecha = (datetime.now() + timedelta(days=dia-1)).strftime("%Y-%m-%d")
        
        # Crear objeto de métricas
        m = MetricasDia(
            dia=dia,
            fecha=fecha,
            casos_planificados=metricas['casos_planificados'],
            casos_ejecutados=metricas['casos_ejecutados'],
            casos_pasados=metricas['casos_pasados'],
            casos_fallados=metricas['casos_fallados'],
            casos_bloqueados=metricas['casos_bloqueados'],
            defectos_nuevos=metricas['defectos_nuevos'],
            defectos_abiertos=metricas['defectos_abiertos'],
            defectos_resueltos=metricas['defectos_resueltos'],
            defectos_criticos=metricas['defectos_criticos'],
            defectos_altos=metricas['defectos_altos'],
            defectos_medios=metricas['defectos_medios'],
            defectos_bajos=metricas['defectos_bajos']
        )
        
        # Calcular métricas derivadas
        m.cobertura = self.calcular_cobertura(m)
        m.tasa_exito = self.calcular_tasa_exito(m)
        m.densidad_defectos = self.calcular_densidad_defectos(m)
        m.efectividad_testing = self.calcular_efectividad_testing(m)
        m.tasa_resolucion = self.calcular_tasa_resolucion(m)
        m.backlog_defectos = self.calcular_backlog_defectos(m)
        m.velocidad_testing = self.calcular_velocidad_testing(m)
        m.indice_calidad = self.calcular_indice_calidad(m)
        
        # Agregar al histórico
        self.historico.append(m)
        self.guardar_historico()
        
        return m
    
    # ==================== INDICADOR 1: COBERTURA DE PRUEBAS ====================
    
    def calcular_cobertura(self, metricas: MetricasDia) -> float:
        """
        Cobertura de Pruebas = (Casos Ejecutados / Casos Planificados) × 100
        
        Indica el porcentaje de casos de prueba ejecutados respecto a los planificados
        Meta: ≥ 85%
        """
        if metricas.casos_planificados == 0:
            return 0.0
        return round((metricas.casos_ejecutados / metricas.casos_planificados) * 100, 2)
    
    # ==================== INDICADOR 2: TASA DE ÉXITO ====================
    
    def calcular_tasa_exito(self, metricas: MetricasDia) -> float:
        """
        Tasa de Éxito = (Casos Pasados / Casos Ejecutados) × 100
        
        Porcentaje de casos de prueba que pasaron exitosamente
        Meta: ≥ 90%
        """
        if metricas.casos_ejecutados == 0:
            return 0.0
        return round((metricas.casos_pasados / metricas.casos_ejecutados) * 100, 2)
    
    # ==================== INDICADOR 3: DENSIDAD DE DEFECTOS ====================
    
    def calcular_densidad_defectos(self, metricas: MetricasDia) -> float:
        """
        Densidad de Defectos = (Total Defectos / Casos Ejecutados) × 100
        
        Número de defectos encontrados por cada 100 casos ejecutados
        Meta: ≤ 15 defectos por 100 casos
        """
        if metricas.casos_ejecutados == 0:
            return 0.0
        total_defectos = (metricas.defectos_criticos + metricas.defectos_altos + 
                         metricas.defectos_medios + metricas.defectos_bajos)
        return round((total_defectos / metricas.casos_ejecutados) * 100, 2)
    
    # ==================== INDICADOR 4: EFECTIVIDAD DEL TESTING ====================
    
    def calcular_efectividad_testing(self, metricas: MetricasDia) -> float:
        """
        Efectividad = (Defectos Encontrados / (Defectos Encontrados + Defectos Post-Release)) × 100
        
        Para simulación, asumimos que encontramos 95% de defectos antes del release
        Meta: ≥ 80%
        """
        if metricas.defectos_nuevos == 0:
            return 100.0
        # Simulación: asumimos 5% de defectos escapan
        defectos_potenciales = metricas.defectos_nuevos / 0.95
        return round((metricas.defectos_nuevos / defectos_potenciales) * 100, 2)
    
    # ==================== INDICADOR 5: TASA DE RESOLUCIÓN ====================
    
    def calcular_tasa_resolucion(self, metricas: MetricasDia) -> float:
        """
        Tasa de Resolución = (Defectos Resueltos / Defectos Abiertos) × 100
        
        Velocidad de resolución de defectos
        Meta: ≥ 70%
        """
        if metricas.defectos_abiertos == 0:
            return 100.0
        return round((metricas.defectos_resueltos / metricas.defectos_abiertos) * 100, 2)
    
    # ==================== INDICADOR 6: BACKLOG DE DEFECTOS ====================
    
    def calcular_backlog_defectos(self, metricas: MetricasDia) -> int:
        """
        Backlog = Defectos Abiertos - Defectos Resueltos
        
        Acumulación de defectos pendientes
        Meta: Tendencia descendente
        """
        return metricas.defectos_abiertos - metricas.defectos_resueltos
    
    # ==================== INDICADOR 7: VELOCIDAD DE TESTING ====================
    
    def calcular_velocidad_testing(self, metricas: MetricasDia) -> float:
        """
        Velocidad = Casos Ejecutados / Día
        
        Número de casos de prueba ejecutados por día
        """
        return float(metricas.casos_ejecutados)
    
    # ==================== INDICADOR 8: ÍNDICE DE CALIDAD ====================
    
    def calcular_indice_calidad(self, metricas: MetricasDia) -> float:
        """
        Índice de Calidad = (Tasa Éxito × 0.4) + ((100 - Densidad) × 0.3) + (Cobertura × 0.3)
        
        Indicador compuesto que combina varios factores de calidad
        Meta: ≥ 80
        """
        # Normalizar densidad (invertir para que menor sea mejor)
        densidad_normalizada = max(0, 100 - metricas.densidad_defectos)
        
        indice = (metricas.tasa_exito * 0.4 + 
                 densidad_normalizada * 0.3 + 
                 metricas.cobertura * 0.3)
        
        return round(indice, 2)
    
    # ==================== ANÁLISIS DE TENDENCIAS ====================
    
    def detectar_tendencia(self, metrica: str, ventana: int = 3) -> str:
        """
        Detectar tendencia de una métrica en los últimos N días
        
        Args:
            metrica: Nombre del atributo de MetricasDia
            ventana: Número de días para análisis (default: 3)
            
        Returns:
            'ascendente', 'descendente' o 'estable'
        """
        if len(self.historico) < 2:
            return 'insuficiente_datos'
        
        # Obtener últimos N valores
        valores = [getattr(m, metrica) for m in self.historico[-ventana:]]
        
        if len(valores) < 2:
            return 'insuficiente_datos'
        
        # Calcular diferencias consecutivas
        diferencias = [valores[i+1] - valores[i] for i in range(len(valores)-1)]
        
        # Determinar tendencia
        if all(d > 0 for d in diferencias):
            return 'ascendente'
        elif all(d < 0 for d in diferencias):
            return 'descendente'
        else:
            # Calcular promedio de diferencias
            promedio_diff = sum(diferencias) / len(diferencias)
            if abs(promedio_diff) < 0.5:  # Umbral de estabilidad
                return 'estable'
            elif promedio_diff > 0:
                return 'ascendente'
            else:
                return 'descendente'
    
    def analizar_todas_tendencias(self) -> Dict[str, str]:
        """Analizar tendencias de todas las métricas clave"""
        metricas_clave = [
            'cobertura', 'tasa_exito', 'densidad_defectos',
            'defectos_abiertos', 'tasa_resolucion', 'indice_calidad'
        ]
        
        tendencias = {}
        for metrica in metricas_clave:
            tendencias[metrica] = self.detectar_tendencia(metrica)
        
        return tendencias
    
    # ==================== CRITERIOS DE SALIDA ====================
    
    def criterios_salida(self) -> Tuple[bool, List[str]]:
        """
        Evaluar si se cumplen los criterios de salida del testing
        
        Returns:
            Tupla (cumple, razones)
            - cumple: True si se pueden detener las pruebas
            - razones: Lista de razones por las que no se cumple
        """
        if not self.historico:
            return False, ["No hay datos históricos"]
        
        ultimo_dia = self.historico[-1]
        razones_incumplimiento = []
        
        # Criterio 1: Cobertura mínima
        if ultimo_dia.cobertura < self.criterios_salida_config['cobertura_minima']:
            razones_incumplimiento.append(
                f"Cobertura insuficiente: {ultimo_dia.cobertura}% (min: {self.criterios_salida_config['cobertura_minima']}%)"
            )
        
        # Criterio 2: Tasa de éxito mínima
        if ultimo_dia.tasa_exito < self.criterios_salida_config['tasa_exito_minima']:
            razones_incumplimiento.append(
                f"Tasa de éxito baja: {ultimo_dia.tasa_exito}% (min: {self.criterios_salida_config['tasa_exito_minima']}%)"
            )
        
        # Criterio 3: No defectos críticos
        if ultimo_dia.defectos_criticos > self.criterios_salida_config['defectos_criticos_max']:
            razones_incumplimiento.append(
                f"Defectos críticos abiertos: {ultimo_dia.defectos_criticos}"
            )
        
        # Criterio 4: Defectos altos controlados
        if ultimo_dia.defectos_altos > self.criterios_salida_config['defectos_altos_max']:
            razones_incumplimiento.append(
                f"Demasiados defectos altos: {ultimo_dia.defectos_altos} (max: {self.criterios_salida_config['defectos_altos_max']})"
            )
        
        # Criterio 5: Densidad de defectos
        if ultimo_dia.densidad_defectos > self.criterios_salida_config['densidad_defectos_max']:
            razones_incumplimiento.append(
                f"Densidad de defectos alta: {ultimo_dia.densidad_defectos} (max: {self.criterios_salida_config['densidad_defectos_max']})"
            )
        
        # Criterio 6: Tendencia de defectos
        if len(self.historico) >= 3:
            tendencia_defectos = self.detectar_tendencia('defectos_abiertos')
            if tendencia_defectos == 'ascendente':
                razones_incumplimiento.append(
                    "Tendencia de defectos ascendente (debe ser descendente o estable)"
                )
        
        # Criterio 7: Estabilidad (días consecutivos sin defectos críticos)
        dias_requeridos = self.criterios_salida_config['dias_consecutivos_estables']
        if len(self.historico) >= dias_requeridos:
            ultimos_dias = self.historico[-dias_requeridos:]
            if not all(d.defectos_criticos == 0 for d in ultimos_dias):
                razones_incumplimiento.append(
                    f"No hay {dias_requeridos} días consecutivos sin defectos críticos"
                )
        else:
            razones_incumplimiento.append(
                f"Necesita al menos {dias_requeridos} días de pruebas"
            )
        
        cumple = len(razones_incumplimiento) == 0
        
        return cumple, razones_incumplimiento
    
    # ==================== REPORTES ====================
    
    def generar_reporte_dia(self, dia: int = None) -> str:
        """Generar reporte detallado de un día específico"""
        if not self.historico:
            return "No hay datos disponibles"
        
        if dia is None:
            metricas = self.historico[-1]
        else:
            if dia < 1 or dia > len(self.historico):
                return f"Día {dia} no encontrado"
            metricas = self.historico[dia - 1]
        
        reporte = f"""
╔═══════════════════════════════════════════════════════════════╗
║           REPORTE DE MÉTRICAS - DÍA {metricas.dia}                        
║           Fecha: {metricas.fecha}                             
╚═══════════════════════════════════════════════════════════════╝

📊 MÉTRICAS DE EJECUCIÓN
├─ Casos Planificados:  {metricas.casos_planificados}
├─ Casos Ejecutados:    {metricas.casos_ejecutados}
├─ Casos Pasados:       {metricas.casos_pasados}
├─ Casos Fallados:      {metricas.casos_fallados}
└─ Casos Bloqueados:    {metricas.casos_bloqueados}

🐛 MÉTRICAS DE DEFECTOS
├─ Defectos Nuevos:     {metricas.defectos_nuevos}
├─ Defectos Abiertos:   {metricas.defectos_abiertos}
├─ Defectos Resueltos:  {metricas.defectos_resueltos}
├─ Críticos:            {metricas.defectos_criticos}
├─ Altos:               {metricas.defectos_altos}
├─ Medios:              {metricas.defectos_medios}
└─ Bajos:               {metricas.defectos_bajos}

📈 INDICADORES CALCULADOS
├─ 1. Cobertura:              {metricas.cobertura}%
├─ 2. Tasa de Éxito:          {metricas.tasa_exito}%
├─ 3. Densidad Defectos:      {metricas.densidad_defectos}
├─ 4. Efectividad Testing:    {metricas.efectividad_testing}%
├─ 5. Tasa Resolución:        {metricas.tasa_resolucion}%
├─ 6. Backlog Defectos:       {metricas.backlog_defectos}
├─ 7. Velocidad Testing:      {metricas.velocidad_testing} casos/día
└─ 8. Índice de Calidad:      {metricas.indice_calidad}
"""
        return reporte
    
    def obtener_dataframe(self) -> pd.DataFrame:
        """Convertir histórico a DataFrame de pandas"""
        if not self.historico:
            return pd.DataFrame()
        
        datos = [asdict(m) for m in self.historico]
        return pd.DataFrame(datos)


# ==================== FUNCIONES DE UTILIDAD ====================

def crear_metricas_ejemplo():
    """Crear datos de ejemplo para pruebas"""
    sistema = MetricasTesting("metricas_test.json")
    
    # Simular 5 días de testing
    dias_ejemplo = [
        {
            'casos_planificados': 100, 'casos_ejecutados': 60,
            'casos_pasados': 45, 'casos_fallados': 12, 'casos_bloqueados': 3,
            'defectos_nuevos': 15, 'defectos_abiertos': 15, 'defectos_resueltos': 0,
            'defectos_criticos': 2, 'defectos_altos': 5, 'defectos_medios': 6, 'defectos_bajos': 2
        },
        {
            'casos_planificados': 100, 'casos_ejecutados': 85,
            'casos_pasados': 70, 'casos_fallados': 10, 'casos_bloqueados': 5,
            'defectos_nuevos': 12, 'defectos_abiertos': 20, 'defectos_resueltos': 7,
            'defectos_criticos': 1, 'defectos_altos': 4, 'defectos_medios': 10, 'defectos_bajos': 5
        },
        {
            'casos_planificados': 100, 'casos_ejecutados': 95,
            'casos_pasados': 85, 'casos_fallados': 8, 'casos_bloqueados': 2,
            'defectos_nuevos': 8, 'defectos_abiertos': 15, 'defectos_resueltos': 13,
            'defectos_criticos': 0, 'defectos_altos': 3, 'defectos_medios': 8, 'defectos_bajos': 4
        },
        {
            'casos_planificados': 100, 'casos_ejecutados': 98,
            'casos_pasados': 92, 'casos_fallados': 5, 'casos_bloqueados': 1,
            'defectos_nuevos': 5, 'defectos_abiertos': 10, 'defectos_resueltos': 10,
            'defectos_criticos': 0, 'defectos_altos': 2, 'defectos_medios': 5, 'defectos_bajos': 3
        },
        {
            'casos_planificados': 100, 'casos_ejecutados': 100,
            'casos_pasados': 95, 'casos_fallados': 3, 'casos_bloqueados': 2,
            'defectos_nuevos': 3, 'defectos_abiertos': 5, 'defectos_resueltos': 8,
            'defectos_criticos': 0, 'defectos_altos': 1, 'defectos_medios': 3, 'defectos_bajos': 1
        }
    ]
    
    for metricas_dia in dias_ejemplo:
        sistema.registrar_dia(metricas_dia)
        print(f"✅ Día {len(sistema.historico)} registrado")
    
    return sistema


if __name__ == "__main__":
    print("🧪 Iniciando Sistema de Métricas de Testing\n")
    
    # Crear datos de ejemplo
    sistema = crear_metricas_ejemplo()
    
    # Mostrar reporte del último día
    print(sistema.generar_reporte_dia())
    
    # Analizar tendencias
    print("\n📈 ANÁLISIS DE TENDENCIAS")
    tendencias = sistema.analizar_todas_tendencias()
    for metrica, tendencia in tendencias.items():
        print(f"├─ {metrica}: {tendencia}")
    
    # Evaluar criterios de salida
    print("\n✅ CRITERIOS DE SALIDA")
    cumple, razones = sistema.criterios_salida()
    if cumple:
        print("✅ Se cumplen todos los criterios de salida")
    else:
        print("❌ No se cumplen los criterios de salida:")
        for razon in razones:
            print(f"   • {razon}")
    
    # Mostrar DataFrame
    print("\n📊 DATOS HISTÓRICOS")
    df = sistema.obtener_dataframe()
    print(df[['dia', 'cobertura', 'tasa_exito', 'defectos_criticos', 'indice_calidad']])