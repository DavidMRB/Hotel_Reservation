import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
from metricas_testing import MetricasTesting
from dashboard_visual import DashboardVisual
import os

class SimuladorTesting:
    """Simulador de proceso de testing durante 5 días"""
    
    def __init__(self):
        self.sistema_metricas = MetricasTesting("simulacion_5_dias.json")
        self.total_casos = 100
        self.defectos_acumulados = []
        self.decisiones = []
        
    def generar_dataset_defectos(self, archivo: str = "dataset_defectos.csv"):
        """Generar dataset de 500 defectos simulados"""
        
        print("📋 Generando dataset de defectos...")
        
        np.random.seed(42)
        random.seed(42)
        
        severidades = ['critico', 'alto', 'medio', 'bajo']
        estados = ['abierto', 'en_progreso', 'resuelto', 'cerrado']
        modulos = ['busqueda', 'reservas', 'pagos', 'usuarios', 'sesiones']
        tipos = ['funcional', 'ui', 'rendimiento', 'seguridad', 'usabilidad']
        
        # Distribución realista de severidades (más bajos que críticos)
        prob_severidad = [0.05, 0.15, 0.40, 0.40]
        
        defectos = []
        
        for i in range(500):
            severidad = np.random.choice(severidades, p=prob_severidad)
            modulo = random.choice(modulos)
            tipo = random.choice(tipos)
            
            # Probabilidad de estar resuelto según severidad
            prob_resuelto = {
                'critico': 0.9,
                'alto': 0.7,
                'medio': 0.5,
                'bajo': 0.3
            }[severidad]
            
            estado = 'resuelto' if random.random() < prob_resuelto else random.choice(estados[:2])
            
            # Tiempo de detección (día 1-5)
            dia_detectado = random.randint(1, 5)
            
            # Tiempo de resolución (si está resuelto)
            if estado == 'resuelto':
                dia_resuelto = dia_detectado + random.randint(1, 3)
                if dia_resuelto > 5:
                    dia_resuelto = 5
            else:
                dia_resuelto = None
            
            defecto = {
                'id': f"DEF-{i+1:04d}",
                'severidad': severidad,
                'modulo': modulo,
                'tipo': tipo,
                'estado': estado,
                'dia_detectado': dia_detectado,
                'dia_resuelto': dia_resuelto,
                'descripcion': f"Defecto en {modulo} - {tipo}",
                'prioridad': {'critico': 5, 'alto': 4, 'medio': 3, 'bajo': 2}[severidad]
            }
            
            defectos.append(defecto)
        
        # Crear DataFrame y guardar
        df = pd.DataFrame(defectos)
        df.to_csv(archivo, index=False)
        
        print(f"✅ Dataset generado: {archivo} ({len(df)} defectos)")
        print(f"   • Críticos: {len(df[df['severidad']=='critico'])}")
        print(f"   • Altos: {len(df[df['severidad']=='alto'])}")
        print(f"   • Medios: {len(df[df['severidad']=='medio'])}")
        print(f"   • Bajos: {len(df[df['severidad']=='bajo'])}")
        
        return df
    
    def simular_dia(self, dia: int, df_defectos: pd.DataFrame):
        """Simular un día de testing"""
        
        print(f"\n{'='*70}")
        print(f"  📅 DÍA {dia} - {(datetime.now() + timedelta(days=dia-1)).strftime('%Y-%m-%d')}")
        print(f"{'='*70}")
        
        # Calcular progreso basado en el día
        progreso_base = min(60 + (dia - 1) * 10, 100)
        casos_ejecutados = int(self.total_casos * progreso_base / 100)
        
        # Agregar variabilidad
        casos_ejecutados = min(casos_ejecutados + random.randint(-3, 3), self.total_casos)
        
        # Simular tasa de éxito (mejora con el tiempo)
        tasa_exito_base = 75 + (dia - 1) * 5
        tasa_exito = min(tasa_exito_base + random.uniform(-3, 3), 100)
        
        casos_pasados = int(casos_ejecutados * tasa_exito / 100)
        casos_fallados = int(casos_ejecutados * (100 - tasa_exito) / 100)
        casos_bloqueados = casos_ejecutados - casos_pasados - casos_fallados
        
        # Obtener defectos del día
        defectos_dia = df_defectos[df_defectos['dia_detectado'] == dia]
        
        defectos_nuevos = len(defectos_dia)
        defectos_criticos = len(defectos_dia[defectos_dia['severidad'] == 'critico'])
        defectos_altos = len(defectos_dia[defectos_dia['severidad'] == 'alto'])
        defectos_medios = len(defectos_dia[defectos_dia['severidad'] == 'medio'])
        defectos_bajos = len(defectos_dia[defectos_dia['severidad'] == 'bajo'])
        
        # Calcular defectos resueltos y abiertos
        defectos_resueltos_dia = len(df_defectos[
            (df_defectos['dia_resuelto'] == dia) & 
            (df_defectos['dia_detectado'] < dia)
        ])
        
        defectos_abiertos_total = len(df_defectos[
            (df_defectos['dia_detectado'] <= dia) & 
            ((df_defectos['dia_resuelto'].isna()) | (df_defectos['dia_resuelto'] > dia))
        ])
        
        # Registrar métricas
        metricas_dia = {
            'casos_planificados': self.total_casos,
            'casos_ejecutados': casos_ejecutados,
            'casos_pasados': casos_pasados,
            'casos_fallados': casos_fallados,
            'casos_bloqueados': casos_bloqueados,
            'defectos_nuevos': defectos_nuevos,
            'defectos_abiertos': defectos_abiertos_total,
            'defectos_resueltos': defectos_resueltos_dia,
            'defectos_criticos': defectos_criticos,
            'defectos_altos': defectos_altos,
            'defectos_medios': defectos_medios,
            'defectos_bajos': defectos_bajos
        }
        
        # Registrar en el sistema
        metricas = self.sistema_metricas.registrar_dia(metricas_dia)
        
        # Mostrar resumen del día
        print(f"\n📊 RESUMEN DEL DÍA {dia}")
        print(f"├─ Casos ejecutados: {casos_ejecutados}/{self.total_casos} ({metricas.cobertura}%)")
        print(f"├─ Casos pasados: {casos_pasados} ({metricas.tasa_exito}%)")
        print(f"├─ Casos fallados: {casos_fallados}")
        print(f"├─ Nuevos defectos: {defectos_nuevos}")
        print(f"│  ├─ Críticos: {defectos_criticos}")
        print(f"│  ├─ Altos: {defectos_altos}")
        print(f"│  ├─ Medios: {defectos_medios}")
        print(f"│  └─ Bajos: {defectos_bajos}")
        print(f"├─ Defectos abiertos: {defectos_abiertos_total}")
        print(f"├─ Defectos resueltos: {defectos_resueltos_dia}")
        print(f"└─ Índice de calidad: {metricas.indice_calidad}")
        
        # Tomar decisión
        decision = self.tomar_decision(dia, metricas, defectos_dia)
        self.decisiones.append(decision)
        
        print(f"\n🎯 DECISIÓN DEL DÍA")
        print(f"├─ Acción: {decision['accion']}")
        print(f"├─ Justificación: {decision['justificacion']}")
        print(f"└─ Recomendaciones:")
        for rec in decision['recomendaciones']:
            print(f"   • {rec}")
        
        # Evaluar criterios de salida
        cumple, razones = self.sistema_metricas.criterios_salida()
        print(f"\n{'✅' if cumple else '⚠️'} CRITERIOS DE SALIDA: {'CUMPLIDOS' if cumple else 'NO CUMPLIDOS'}")
        if not cumple:
            print("Razones de incumplimiento:")
            for razon in razones:
                print(f"   • {razon}")
        
        return metricas
    
    def tomar_decision(self, dia: int, metricas, defectos_dia: pd.DataFrame) -> dict:
        """Tomar decisiones basadas en métricas del día"""
        
        accion = ""
        justificacion = ""
        recomendaciones = []
        
        # Analizar situación
        tiene_criticos = metricas.defectos_criticos > 0
        cobertura_baja = metricas.cobertura < 85
        tasa_exito_baja = metricas.tasa_exito < 90
        densidad_alta = metricas.densidad_defectos > 15
        
        # Decisión principal
        if dia == 1:
            accion = "CONTINUAR CON TESTING INTENSIVO"
            justificacion = "Primer día de ejecución, fase de descubrimiento de defectos"
            recomendaciones = [
                "Priorizar pruebas de funcionalidad crítica",
                "Documentar todos los defectos encontrados",
                "Establecer reunión diaria con desarrollo"
            ]
        
        elif dia == 2:
            if tiene_criticos:
                accion = "PAUSAR NUEVAS PRUEBAS - RESOLVER CRÍTICOS"
                justificacion = f"Se encontraron {metricas.defectos_criticos} defectos críticos que bloquean el testing"
                recomendaciones = [
                    "Equipo de desarrollo debe enfocarse en defectos críticos",
                    "QA debe validar correcciones inmediatamente",
                    "Preparar casos de regresión para mañana"
                ]
            else:
                accion = "CONTINUAR TESTING - AMPLIAR COBERTURA"
                justificacion = "No hay defectos críticos, se puede avanzar con más casos"
                recomendaciones = [
                    "Ejecutar casos de regresión",
                    "Iniciar pruebas de integración",
                    "Monitorear resolución de defectos altos"
                ]
        
        elif dia == 3:
            if cobertura_baja:
                accion = "ACELERAR EJECUCIÓN DE CASOS"
                justificacion = f"Cobertura en {metricas.cobertura}%, necesita alcanzar 85%"
                recomendaciones = [
                    "Priorizar casos de alto impacto",
                    "Automatizar casos repetitivos si es posible",
                    "Asignar más recursos al testing"
                ]
            elif tiene_criticos:
                accion = "BLOQUEAR RELEASE - RESOLVER CRÍTICOS"
                justificacion = "Aún hay defectos críticos sin resolver"
                recomendaciones = [
                    "Reunión urgente con stakeholders",
                    "Replantear timeline del release",
                    "Priorizar corrección de críticos"
                ]
            else:
                accion = "CONTINUAR TESTING ENFOCADO"
                justificacion = "Buen progreso, enfocar en casos pendientes"
                recomendaciones = [
                    "Ejecutar casos de borde y negativos",
                    "Validar correcciones de defectos",
                    "Preparar reporte de progreso"
                ]
        
        elif dia == 4:
            cumple, razones = self.sistema_metricas.criterios_salida()
            
            if cumple:
                accion = "PREPARAR PARA RELEASE"
                justificacion = "Todos los criterios de salida cumplidos"
                recomendaciones = [
                    "Ejecutar suite de regresión completa",
                    "Preparar documentación de release",
                    "Coordinar despliegue a producción"
                ]
            elif tiene_criticos or len(razones) > 3:
                accion = "EXTENDER FASE DE TESTING"
                justificacion = f"No se cumplen {len(razones)} criterios de salida"
                recomendaciones = [
                    "Replantear fecha de release",
                    "Reforzar equipo de desarrollo",
                    "Análisis de causa raíz de defectos"
                ]
            else:
                accion = "TESTING FINAL - VALIDACIÓN"
                justificacion = "Quedan pocos criterios por cumplir"
                recomendaciones = [
                    "Completar casos faltantes",
                    "Validar últimas correcciones",
                    "Preparar para release condicional"
                ]
        
        else:  # día == 5
            cumple, razones = self.sistema_metricas.criterios_salida()
            
            if cumple:
                accion = "APROBAR RELEASE A PRODUCCIÓN"
                justificacion = "Sistema cumple todos los criterios de calidad"
                recomendaciones = [
                    "Ejecutar despliegue a producción",
                    "Activar monitoreo post-release",
                    "Preparar plan de rollback por precaución"
                ]
            elif tiene_criticos:
                accion = "RECHAZAR RELEASE - CRÍTICOS ABIERTOS"
                justificacion = f"No se puede liberar con {metricas.defectos_criticos} defectos críticos"
                recomendaciones = [
                    "Planificar sprint de corrección",
                    "Nueva fecha de release",
                    "Análisis retrospectivo del proceso"
                ]
            elif tasa_exito_baja or cobertura_baja:
                accion = "RELEASE CONDICIONAL"
                justificacion = "Criterios principales cumplidos pero con observaciones"
                recomendaciones = [
                    "Release con plan de mitigación",
                    "Monitoreo intensivo en producción",
                    "Hotfix team en alerta"
                ]
            else:
                accion = "APROBAR RELEASE CON RESERVAS"
                justificacion = "Cumple criterios mínimos, con plan de mejora post-release"
                recomendaciones = [
                    "Liberar a producción con cautela",
                    "Plan de correcciones en próximo sprint",
                    "Revisión de proceso de testing"
                ]
        
        return {
            'dia': dia,
            'accion': accion,
            'justificacion': justificacion,
            'recomendaciones': recomendaciones,
            'metricas_clave': {
                'cobertura': metricas.cobertura,
                'tasa_exito': metricas.tasa_exito,
                'criticos': metricas.defectos_criticos,
                'indice_calidad': metricas.indice_calidad
            }
        }
    
    def ejecutar_simulacion(self):
        """Ejecutar simulación completa de 5 días"""
        
        print("\n" + "="*70)
        print("  🏨 SIMULACIÓN DE 5 DÍAS DE TESTING")
        print("     Sistema de Reservas de Hotel")
        print("="*70)
        
        # Generar dataset
        df_defectos = self.generar_dataset_defectos()
        
        # Simular cada día
        for dia in range(1, 6):
            self.simular_dia(dia, df_defectos)
            
            # Generar snapshot del día
            dashboard = DashboardVisual(self.sistema_metricas)
            dashboard.generar_dashboard_completo(f"dashboard_dia_{dia}.png")
            dashboard.generar_reporte_html(f"reporte_dia_{dia}.html")
            
            print(f"\n💾 Snapshot del día {dia} guardado")
        
        # Resumen final
        self.generar_resumen_final()
    
    def generar_resumen_final(self):
        """Generar resumen ejecutivo de los 5 días"""
        
        print(f"\n{'='*70}")
        print("  📊 RESUMEN EJECUTIVO - 5 DÍAS DE TESTING")
        print(f"{'='*70}")
        
        # Obtener datos históricos
        df = self.sistema_metricas.obtener_dataframe()
        
        # Métricas finales
        ultimo_dia = self.sistema_metricas.historico[-1]
        primer_dia = self.sistema_metricas.historico[0]
        
        print(f"\n📈 EVOLUCIÓN DE MÉTRICAS")
        print(f"├─ Cobertura: {primer_dia.cobertura}% → {ultimo_dia.cobertura}% ({ultimo_dia.cobertura - primer_dia.cobertura:+.1f}%)")
        print(f"├─ Tasa de Éxito: {primer_dia.tasa_exito}% → {ultimo_dia.tasa_exito}% ({ultimo_dia.tasa_exito - primer_dia.tasa_exito:+.1f}%)")
        print(f"├─ Defectos Críticos: {primer_dia.defectos_criticos} → {ultimo_dia.defectos_criticos} ({ultimo_dia.defectos_criticos - primer_dia.defectos_criticos:+d})")
        print(f"├─ Índice de Calidad: {primer_dia.indice_calidad} → {ultimo_dia.indice_calidad} ({ultimo_dia.indice_calidad - primer_dia.indice_calidad:+.1f})")
        print(f"└─ Densidad Defectos: {primer_dia.densidad_defectos} → {ultimo_dia.densidad_defectos} ({ultimo_dia.densidad_defectos - primer_dia.densidad_defectos:+.1f})")
        
        # Totales
        total_defectos = df['defectos_nuevos'].sum()
        total_resueltos = df['defectos_resueltos'].sum()
        
        print(f"\n📊 TOTALES")
        print(f"├─ Total casos ejecutados: {ultimo_dia.casos_ejecutados}/{self.total_casos}")
        print(f"├─ Total defectos encontrados: {total_defectos}")
        print(f"├─ Total defectos resueltos: {total_resueltos}")
        print(f"├─ Tasa de resolución global: {(total_resueltos/total_defectos*100):.1f}%")
        print(f"└─ Defectos pendientes: {ultimo_dia.defectos_abiertos}")
        
        # Decisiones tomadas
        print(f"\n🎯 DECISIONES TOMADAS")
        for decision in self.decisiones:
            print(f"Día {decision['dia']}: {decision['accion']}")
        
        # Criterios de salida
        cumple, razones = self.sistema_metricas.criterios_salida()
        print(f"\n{'✅' if cumple else '❌'} CRITERIOS DE SALIDA: {'CUMPLIDOS' if cumple else 'NO CUMPLIDOS'}")
        
        if cumple:
            print("\n🎉 RECOMENDACIÓN FINAL: APROBAR RELEASE A PRODUCCIÓN")
            print("   El sistema cumple todos los criterios de calidad establecidos.")
        else:
            print("\n⚠️ RECOMENDACIÓN FINAL: NO APROBAR RELEASE")
            print("   Razones:")
            for razon in razones:
                print(f"   • {razon}")
        
        # Generar dashboard final
        print(f"\n📊 Generando documentación final...")
        dashboard = DashboardVisual(self.sistema_metricas)
        dashboard.generar_dashboard_completo("dashboard_final.png")
        dashboard.generar_reporte_html("reporte_final.html")
        
        print(f"\n✅ SIMULACIÓN COMPLETADA")
        print(f"\n📁 Archivos generados:")
        print(f"   • dataset_defectos.csv")
        print(f"   • simulacion_5_dias.json")
        for dia in range(1, 6):
            print(f"   • dashboard_dia_{dia}.png")
            print(f"   • reporte_dia_{dia}.html")
        print(f"   • dashboard_final.png")
        print(f"   • reporte_final.html")


if __name__ == "__main__":
    simulador = SimuladorTesting()
    simulador.ejecutar_simulacion()