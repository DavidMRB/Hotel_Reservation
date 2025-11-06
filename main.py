import sys
import os
from datetime import datetime

sys.path.append(os.path.dirname(os.path.abspath(__file__)))

def mostrar_menu():
    """Mostrar menú principal"""
    print("\n" + "="*70)
    print("  🏨 PROYECTO: SISTEMA DE RESERVAS DE HOTEL")
    print("     Testing de Software - Sistema Completo")
    print("="*70)
    print("\nFASE 1: Sistema de Reservas")
    print("  1. Iniciar servidor del sistema de reservas")
    print("  2. Ejecutar cliente de prueba")
    print("\nFASE 2: Sistema de Métricas")
    print("  3. Ejecutar simulación completa de 5 días")
    print("  4. Ver métricas existentes")
    print("  5. Generar dashboard visual")
    print("  6. Generar reporte HTML")
    print("\nOtras opciones")
    print("  7. Ver documentación")
    print("  8. Verificar instalación")
    print("  0. Salir")
    print("\n" + "="*70)

def verificar_dependencias():
    """Verificar que todas las dependencias estén instaladas"""
    print("\n🔍 Verificando dependencias...")
    
    dependencias = {
        'fastapi': 'FastAPI',
        'uvicorn': 'Uvicorn',
        'pydantic': 'Pydantic',
        'pandas': 'Pandas',
        'matplotlib': 'Matplotlib',
        'numpy': 'NumPy',
        'requests': 'Requests'
    }
    
    faltantes = []
    
    for modulo, nombre in dependencias.items():
        try:
            __import__(modulo)
            print(f"  ✅ {nombre}")
        except ImportError:
            print(f"  ❌ {nombre} - NO INSTALADO")
            faltantes.append(nombre)
    
    if faltantes:
        print(f"\n⚠️ Faltan dependencias: {', '.join(faltantes)}")
        print("\nPara instalar todas las dependencias, ejecuta:")
        print("  pip install -r requirements.txt")
        return False
    else:
        print("\n✅ Todas las dependencias están instaladas correctamente")
        return True

def iniciar_servidor():
    """Iniciar servidor de FastAPI"""
    print("\n🚀 Iniciando servidor del sistema de reservas...")
    print("📍 El servidor se iniciará en: http://localhost:8000")
    print("📚 Documentación: http://localhost:8000/docs")
    print("\n⚠️ Presiona CTRL+C para detener el servidor\n")
    
    try:
        import uvicorn
        from hotel_booking_system import app
        uvicorn.run(app, host="0.0.0.0", port=8000)
    except ImportError:
        print("❌ Error: No se puede importar el módulo del servidor")
        print("   Asegúrate de que hotel_booking_system.py esté en el mismo directorio")
    except KeyboardInterrupt:
        print("\n\n✅ Servidor detenido correctamente")

def ejecutar_cliente_prueba():
    """Ejecutar cliente de prueba"""
    print("\n🧪 Ejecutando cliente de prueba...")
    print("⚠️ Asegúrate de que el servidor esté corriendo en otra terminal\n")
    
    try:
        import test_client
        print("\n✅ Prueba completada")
    except ImportError:
        print("❌ Error: No se puede importar test_client.py")
    except Exception as e:
        print(f"❌ Error durante la ejecución: {e}")

def ejecutar_simulacion():
    """Ejecutar simulación de 5 días"""
    print("\n🎬 Iniciando simulación de 5 días de testing...\n")
    
    try:
        from simulador_5_dias import SimuladorTesting
        simulador = SimuladorTesting()
        simulador.ejecutar_simulacion()
        print("\n✅ Simulación completada exitosamente")
    except ImportError as e:
        print(f"❌ Error al importar módulos: {e}")
        print("   Asegúrate de que todos los archivos estén en el directorio")
    except Exception as e:
        print(f"❌ Error durante la simulación: {e}")

def ver_metricas():
    """Ver métricas existentes"""
    print("\n📊 Cargando métricas existentes...\n")
    
    try:
        from metricas_testing import MetricasTesting
        
        sistema = MetricasTesting("simulacion_5_dias.json")
        
        if not sistema.historico:
            print("⚠️ No hay datos históricos disponibles")
            print("   Ejecuta primero la opción 3 para generar datos")
            return
        
        # Mostrar último día
        print(sistema.generar_reporte_dia())
        
        # Mostrar tendencias
        print("\n📈 ANÁLISIS DE TENDENCIAS")
        tendencias = sistema.analizar_todas_tendencias()
        for metrica, tendencia in tendencias.items():
            simbolo = {'ascendente': '↑', 'descendente': '↓', 'estable': '→'}.get(tendencia, '?')
            print(f"├─ {metrica.replace('_', ' ').title()}: {simbolo} {tendencia.title()}")
        
        # Criterios de salida
        print("\n✅ EVALUACIÓN DE CRITERIOS")
        cumple, razones = sistema.criterios_salida()
        if cumple:
            print("✅ Se cumplen todos los criterios de salida")
        else:
            print("❌ No se cumplen los criterios de salida:")
            for razon in razones:
                print(f"   • {razon}")
        
    except FileNotFoundError:
        print("⚠️ No se encontró el archivo de métricas")
        print("   Ejecuta primero la opción 3 para generar datos")
    except ImportError:
        print("❌ Error al importar módulo de métricas")
    except Exception as e:
        print(f"❌ Error: {e}")

def generar_dashboard():
    """Generar dashboard visual"""
    print("\n📊 Generando dashboard visual...\n")
    
    try:
        from metricas_testing import MetricasTesting
        from dashboard_visual import DashboardVisual
        
        sistema = MetricasTesting("simulacion_5_dias.json")
        
        if not sistema.historico:
            print("⚠️ No hay datos históricos disponibles")
            print("   Ejecuta primero la opción 3 para generar datos")
            return
        
        dashboard = DashboardVisual(sistema)
        
        # Generar dashboard
        archivo = f"dashboard_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
        dashboard.generar_dashboard_completo(archivo)
        
        print(f"\n✅ Dashboard generado: {archivo}")
        
    except FileNotFoundError:
        print("⚠️ No se encontró el archivo de métricas")
        print("   Ejecuta primero la opción 3 para generar datos")
    except ImportError:
        print("❌ Error al importar módulos")
    except Exception as e:
        print(f"❌ Error: {e}")

def generar_reporte_html():
    """Generar reporte HTML"""
    print("\n📄 Generando reporte HTML...\n")
    
    try:
        from metricas_testing import MetricasTesting
        from dashboard_visual import DashboardVisual
        
        sistema = MetricasTesting("simulacion_5_dias.json")
        
        if not sistema.historico:
            print("⚠️ No hay datos históricos disponibles")
            print("   Ejecuta primero la opción 3 para generar datos")
            return
        
        dashboard = DashboardVisual(sistema)
        
        # Generar reporte
        archivo = f"reporte_{datetime.now().strftime('%Y%m%d_%H%M%S')}.html"
        dashboard.generar_reporte_html(archivo)
        
        print(f"\n✅ Reporte HTML generado: {archivo}")
        print(f"   Ábrelo en tu navegador para ver el reporte completo")
        
    except FileNotFoundError:
        print("⚠️ No se encontró el archivo de métricas")
        print("   Ejecuta primero la opción 3 para generar datos")
    except ImportError:
        print("❌ Error al importar módulos")
    except Exception as e:
        print(f"❌ Error: {e}")

def mostrar_documentacion():
    """Mostrar información de documentación"""
    print("\n" + "="*70)
    print("  📚 DOCUMENTACIÓN DEL PROYECTO")
    print("="*70)
    print("\nArchivos de documentación:")
    print("  • README.md - Instrucciones de la FASE 1")
    print("  • README_FASE2.md - Instrucciones de la FASE 2")
    print("\nEstructura del proyecto:")
    print("  FASE 1: Sistema de Reservas de Hotel")
    print("    • hotel_booking_system.py - Backend con FastAPI")
    print("    • test_client.py - Cliente de prueba")
    print("\n  FASE 2: Sistema de Métricas")
    print("    • metricas_testing.py - 8 indicadores + análisis")
    print("    • dashboard_visual.py - Visualización con matplotlib")
    print("    • simulador_5_dias.py - Simulación completa")
    print("\nDocumentación online:")
    print("  • FastAPI: https://fastapi.tiangolo.com/")
    print("  • Pandas: https://pandas.pydata.org/")
    print("  • Matplotlib: https://matplotlib.org/")
    print("\nPara más detalles, consulta los archivos README.md")

def main():
    """Función principal"""
    while True:
        mostrar_menu()
        
        try:
            opcion = input("\nSelecciona una opción (0-8): ").strip()
            
            if opcion == "0":
                print("\n👋 ¡Hasta luego!")
                break
            
            elif opcion == "1":
                iniciar_servidor()
            
            elif opcion == "2":
                ejecutar_cliente_prueba()
            
            elif opcion == "3":
                ejecutar_simulacion()
            
            elif opcion == "4":
                ver_metricas()
            
            elif opcion == "5":
                generar_dashboard()
            
            elif opcion == "6":
                generar_reporte_html()
            
            elif opcion == "7":
                mostrar_documentacion()
            
            elif opcion == "8":
                verificar_dependencias()
            
            else:
                print("\n❌ Opción inválida. Por favor, selecciona un número del 0 al 8.")
            
            input("\n\nPresiona ENTER para continuar...")
            
        except KeyboardInterrupt:
            print("\n\n👋 ¡Hasta luego!")
            break
        except Exception as e:
            print(f"\n❌ Error inesperado: {e}")
            input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    print("\n🏨 Sistema de Reservas de Hotel - Proyecto Completo")
    print("   Testing de Software\n")
    
    # Verificar dependencias al inicio
    if not verificar_dependencias():
        print("\n⚠️ Por favor instala las dependencias faltantes antes de continuar")
        sys.exit(1)
    
    main()