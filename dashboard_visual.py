import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import Rectangle
import pandas as pd
import numpy as np
from datetime import datetime
import os
from metricas_testing import MetricasTesting

class DashboardVisual:
    """Dashboard visual con matplotlib para métricas de testing"""
    
    def __init__(self, sistema_metricas: MetricasTesting):
        self.sistema = sistema_metricas
        self.colores = {
            'exito': '#2ecc71',
            'warning': '#f39c12',
            'critico': '#e74c3c',
            'info': '#3498db',
            'neutro': '#95a5a6'
        }
        
        # Configurar estilo de matplotlib
        plt.style.use('seaborn-v0_8-darkgrid')
        plt.rcParams['figure.facecolor'] = 'white'
        plt.rcParams['axes.facecolor'] = '#f8f9fa'
    
    def crear_semaforo(self, valor: float, umbral_verde: float, umbral_amarillo: float, 
                       invertido: bool = False) -> str:
        """
        Determinar color del semáforo basado en umbrales
        
        Args:
            valor: Valor a evaluar
            umbral_verde: Umbral para color verde
            umbral_amarillo: Umbral para color amarillo
            invertido: Si True, valores altos son malos
        """
        if invertido:
            if valor <= umbral_verde:
                return self.colores['exito']
            elif valor <= umbral_amarillo:
                return self.colores['warning']
            else:
                return self.colores['critico']
        else:
            if valor >= umbral_verde:
                return self.colores['exito']
            elif valor >= umbral_amarillo:
                return self.colores['warning']
            else:
                return self.colores['critico']
    
    def generar_dashboard_completo(self, archivo_salida: str = "dashboard_metricas.png"):
        """Generar dashboard completo con todos los gráficos"""
        if not self.sistema.historico:
            print("❌ No hay datos históricos para generar dashboard")
            return
        
        # Crear figura con subplots
        fig = plt.figure(figsize=(20, 12))
        gs = fig.add_gridspec(4, 3, hspace=0.3, wspace=0.3)
        
        # 1. Gráfico de Cobertura y Tasa de Éxito
        ax1 = fig.add_subplot(gs[0, 0])
        self._grafico_cobertura_exito(ax1)
        
        # 2. Gráfico de Defectos por Severidad
        ax2 = fig.add_subplot(gs[0, 1])
        self._grafico_defectos_severidad(ax2)
        
        # 3. Semáforo de Estado
        ax3 = fig.add_subplot(gs[0, 2])
        self._grafico_semaforo_estado(ax3)
        
        # 4. Tendencia de Densidad de Defectos
        ax4 = fig.add_subplot(gs[1, 0])
        self._grafico_densidad_defectos(ax4)
        
        # 5. Backlog de Defectos
        ax5 = fig.add_subplot(gs[1, 1])
        self._grafico_backlog_defectos(ax5)
        
        # 6. Velocidad de Testing
        ax6 = fig.add_subplot(gs[1, 2])
        self._grafico_velocidad_testing(ax6)
        
        # 7. Índice de Calidad
        ax7 = fig.add_subplot(gs[2, 0])
        self._grafico_indice_calidad(ax7)
        
        # 8. Distribución de Casos
        ax8 = fig.add_subplot(gs[2, 1])
        self._grafico_distribucion_casos(ax8)
        
        # 9. Tasa de Resolución
        ax9 = fig.add_subplot(gs[2, 2])
        self._grafico_tasa_resolucion(ax9)
        
        # 10. Resumen de Métricas Clave
        ax10 = fig.add_subplot(gs[3, :])
        self._tabla_resumen_metricas(ax10)
        
        # Título general
        fig.suptitle('🏨 DASHBOARD DE MÉTRICAS - SISTEMA DE RESERVAS DE HOTEL', 
                     fontsize=20, fontweight='bold', y=0.98)
        
        # Agregar fecha de generación
        fecha_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        fig.text(0.99, 0.01, f'Generado: {fecha_str}', 
                ha='right', va='bottom', fontsize=10, style='italic')
        
        # Guardar
        plt.savefig(archivo_salida, dpi=150, bbox_inches='tight')
        print(f"✅ Dashboard guardado en: {archivo_salida}")
        
        # Mostrar
        plt.show()
    
    def _grafico_cobertura_exito(self, ax):
        """Gráfico de líneas: Cobertura y Tasa de Éxito"""
        df = self.sistema.obtener_dataframe()
        
        ax.plot(df['dia'], df['cobertura'], marker='o', linewidth=2, 
               label='Cobertura', color=self.colores['info'])
        ax.plot(df['dia'], df['tasa_exito'], marker='s', linewidth=2,
               label='Tasa Éxito', color=self.colores['exito'])
        
        # Líneas de meta
        ax.axhline(y=85, color='red', linestyle='--', alpha=0.5, label='Meta Cobertura (85%)')
        ax.axhline(y=90, color='green', linestyle='--', alpha=0.5, label='Meta Éxito (90%)')
        
        ax.set_xlabel('Día', fontweight='bold')
        ax.set_ylabel('Porcentaje (%)', fontweight='bold')
        ax.set_title('Cobertura y Tasa de Éxito', fontweight='bold', pad=10)
        ax.legend(loc='lower right')
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 105)
    
    def _grafico_defectos_severidad(self, ax):
        """Gráfico de barras apiladas: Defectos por Severidad"""
        df = self.sistema.obtener_dataframe()
        
        width = 0.6
        x = df['dia']
        
        ax.bar(x, df['defectos_criticos'], width, label='Críticos',
              color=self.colores['critico'])
        ax.bar(x, df['defectos_altos'], width, bottom=df['defectos_criticos'],
              label='Altos', color=self.colores['warning'])
        ax.bar(x, df['defectos_medios'], width,
              bottom=df['defectos_criticos'] + df['defectos_altos'],
              label='Medios', color='#3498db')
        ax.bar(x, df['defectos_bajos'], width,
              bottom=df['defectos_criticos'] + df['defectos_altos'] + df['defectos_medios'],
              label='Bajos', color=self.colores['neutro'])
        
        ax.set_xlabel('Día', fontweight='bold')
        ax.set_ylabel('Cantidad', fontweight='bold')
        ax.set_title('Defectos por Severidad', fontweight='bold', pad=10)
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
    
    def _grafico_semaforo_estado(self, ax):
        """Semáforo visual del estado actual"""
        ultimo_dia = self.sistema.historico[-1]
        cumple, razones = self.sistema.criterios_salida()
        
        # Preparar datos
        metricas_eval = [
            ('Cobertura', ultimo_dia.cobertura, 85, 75, False),
            ('Tasa Éxito', ultimo_dia.tasa_exito, 90, 80, False),
            ('Densidad Def.', ultimo_dia.densidad_defectos, 10, 15, True),
            ('Def. Críticos', ultimo_dia.defectos_criticos, 0, 1, True),
            ('Índice Calidad', ultimo_dia.indice_calidad, 80, 70, False)
        ]
        
        y_pos = np.arange(len(metricas_eval))
        
        for i, (nombre, valor, umbral_v, umbral_a, invertido) in enumerate(metricas_eval):
            color = self.crear_semaforo(valor, umbral_v, umbral_a, invertido)
            
            # Dibujar círculo de semáforo
            circle = plt.Circle((0.2, i), 0.15, color=color, ec='black', linewidth=2)
            ax.add_patch(circle)
            
            # Texto
            ax.text(0.5, i, f'{nombre}: {valor:.1f}', 
                   va='center', fontsize=10, fontweight='bold')
        
        ax.set_xlim(0, 1)
        ax.set_ylim(-0.5, len(metricas_eval) - 0.5)
        ax.set_title('Semáforo de Estado Actual', fontweight='bold', pad=10)
        ax.axis('off')
        
        # Estado general
        estado_texto = "✅ LISTO PARA RELEASE" if cumple else "⚠️ REQUIERE ATENCIÓN"
        color_estado = self.colores['exito'] if cumple else self.colores['warning']
        ax.text(0.5, -0.8, estado_texto, ha='center', fontsize=12,
               fontweight='bold', bbox=dict(boxstyle='round', facecolor=color_estado, alpha=0.5))
    
    def _grafico_densidad_defectos(self, ax):
        """Tendencia de Densidad de Defectos"""
        df = self.sistema.obtener_dataframe()
        
        ax.plot(df['dia'], df['densidad_defectos'], marker='o', linewidth=2.5,
               color=self.colores['critico'], markersize=8)
        
        # Línea de tendencia
        z = np.polyfit(df['dia'], df['densidad_defectos'], 1)
        p = np.poly1d(z)
        ax.plot(df['dia'], p(df['dia']), "--", alpha=0.5, color='gray',
               label='Tendencia')
        
        # Meta
        ax.axhline(y=15, color='red', linestyle='--', alpha=0.5,
                  label='Meta (≤15)')
        
        ax.set_xlabel('Día', fontweight='bold')
        ax.set_ylabel('Densidad', fontweight='bold')
        ax.set_title('Densidad de Defectos (por 100 casos)', fontweight='bold', pad=10)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _grafico_backlog_defectos(self, ax):
        """Backlog de Defectos"""
        df = self.sistema.obtener_dataframe()
        
        colores_bars = [self.crear_semaforo(v, 5, 10, True) for v in df['backlog_defectos']]
        
        ax.bar(df['dia'], df['backlog_defectos'], color=colores_bars, 
              edgecolor='black', linewidth=1.5)
        
        ax.set_xlabel('Día', fontweight='bold')
        ax.set_ylabel('Defectos Pendientes', fontweight='bold')
        ax.set_title('Backlog de Defectos', fontweight='bold', pad=10)
        ax.grid(True, alpha=0.3, axis='y')
    
    def _grafico_velocidad_testing(self, ax):
        """Velocidad de Testing (casos por día)"""
        df = self.sistema.obtener_dataframe()
        
        ax.plot(df['dia'], df['velocidad_testing'], marker='D', linewidth=2,
               color='#9b59b6', markersize=8)
        
        # Promedio
        promedio = df['velocidad_testing'].mean()
        ax.axhline(y=promedio, color='green', linestyle='--', alpha=0.5,
                  label=f'Promedio ({promedio:.1f})')
        
        ax.set_xlabel('Día', fontweight='bold')
        ax.set_ylabel('Casos Ejecutados', fontweight='bold')
        ax.set_title('Velocidad de Testing', fontweight='bold', pad=10)
        ax.legend()
        ax.grid(True, alpha=0.3)
    
    def _grafico_indice_calidad(self, ax):
        """Índice de Calidad General"""
        df = self.sistema.obtener_dataframe()
        
        # Gráfico de área
        ax.fill_between(df['dia'], df['indice_calidad'], alpha=0.3,
                       color=self.colores['exito'])
        ax.plot(df['dia'], df['indice_calidad'], marker='o', linewidth=2,
               color=self.colores['exito'], markersize=8)
        
        # Meta
        ax.axhline(y=80, color='red', linestyle='--', alpha=0.5,
                  label='Meta (≥80)')
        
        ax.set_xlabel('Día', fontweight='bold')
        ax.set_ylabel('Índice', fontweight='bold')
        ax.set_title('Índice de Calidad General', fontweight='bold', pad=10)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 110)
    
    def _grafico_distribucion_casos(self, ax):
        """Distribución de Casos del Último Día"""
        ultimo_dia = self.sistema.historico[-1]
        
        categorias = ['Pasados', 'Fallados', 'Bloqueados', 'Pendientes']
        valores = [
            ultimo_dia.casos_pasados,
            ultimo_dia.casos_fallados,
            ultimo_dia.casos_bloqueados,
            ultimo_dia.casos_planificados - ultimo_dia.casos_ejecutados
        ]
        colores = [self.colores['exito'], self.colores['critico'],
                  self.colores['warning'], self.colores['neutro']]
        
        wedges, texts, autotexts = ax.pie(valores, labels=categorias, colors=colores,
                                          autopct='%1.1f%%', startangle=90)
        
        # Mejorar textos
        for autotext in autotexts:
            autotext.set_color('white')
            autotext.set_fontweight('bold')
            autotext.set_fontsize(10)
        
        ax.set_title(f'Distribución de Casos - Día {ultimo_dia.dia}',
                    fontweight='bold', pad=10)
    
    def _grafico_tasa_resolucion(self, ax):
        """Tasa de Resolución de Defectos"""
        df = self.sistema.obtener_dataframe()
        
        ax.plot(df['dia'], df['tasa_resolucion'], marker='o', linewidth=2,
               color='#e67e22', markersize=8)
        
        # Meta
        ax.axhline(y=70, color='green', linestyle='--', alpha=0.5,
                  label='Meta (≥70%)')
        
        ax.set_xlabel('Día', fontweight='bold')
        ax.set_ylabel('Porcentaje (%)', fontweight='bold')
        ax.set_title('Tasa de Resolución de Defectos', fontweight='bold', pad=10)
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_ylim(0, 110)
    
    def _tabla_resumen_metricas(self, ax):
        """Tabla resumen de todas las métricas"""
        df = self.sistema.obtener_dataframe()
        
        # Preparar datos para la tabla
        metricas_mostrar = [
            'cobertura', 'tasa_exito', 'densidad_defectos',
            'defectos_criticos', 'defectos_altos', 'backlog_defectos',
            'velocidad_testing', 'indice_calidad'
        ]
        
        tabla_data = []
        for metrica in metricas_mostrar:
            valores = df[metrica].tolist()
            # Agregar fila con: Métrica, Día1, Día2, ..., DíaN, Tendencia
            tendencia = self.sistema.detectar_tendencia(metrica)
            
            # Símbolos de tendencia
            simbolo = {
                'ascendente': '↑',
                'descendente': '↓',
                'estable': '→',
                'insuficiente_datos': '-'
            }.get(tendencia, '?')
            
            fila = [metrica.replace('_', ' ').title()] + [f'{v:.1f}' for v in valores] + [simbolo]
            tabla_data.append(fila)
        
        # Crear tabla
        col_labels = ['Métrica'] + [f'D{i+1}' for i in range(len(df))] + ['Tend.']
        
        table = ax.table(cellText=tabla_data, colLabels=col_labels,
                        cellLoc='center', loc='center',
                        colWidths=[0.15] + [0.08] * len(df) + [0.08])
        
        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 2)
        
        # Estilizar
        for (i, j), cell in table.get_celld().items():
            if i == 0:  # Header
                cell.set_facecolor('#3498db')
                cell.set_text_props(weight='bold', color='white')
            else:
                cell.set_facecolor('#ecf0f1' if i % 2 == 0 else 'white')
        
        ax.set_title('Resumen Histórico de Métricas', fontweight='bold', 
                    fontsize=14, pad=20)
        ax.axis('off')
    
    def generar_reporte_html(self, archivo_salida: str = "reporte_metricas.html"):
        """Generar reporte HTML completo"""
        ultimo_dia = self.sistema.historico[-1]
        cumple, razones = self.sistema.criterios_salida()
        tendencias = self.sistema.analizar_todas_tendencias()
        
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Métricas - Testing</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        }}
        .container {{
            max-width: 1400px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2c3e50;
            text-align: center;
            border-bottom: 3px solid #3498db;
            padding-bottom: 15px;
        }}
        .resumen {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin: 30px 0;
        }}
        .metrica-card {{
            background: #f8f9fa;
            padding: 20px;
            border-radius: 10px;
            border-left: 5px solid #3498db;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }}
        .metrica-card h3 {{
            margin: 0 0 10px 0;
            color: #34495e;
            font-size: 14px;
        }}
        .metrica-valor {{
            font-size: 32px;
            font-weight: bold;
            color: #2c3e50;
        }}
        .semaforo {{
            display: inline-block;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            margin-right: 10px;
        }}
        .verde {{ background: #2ecc71; }}
        .amarillo {{ background: #f39c12; }}
        .rojo {{ background: #e74c3c; }}
        .criterios {{
            margin: 30px 0;
            padding: 20px;
            background: {'#d4edda' if cumple else '#f8d7da'};
            border-radius: 10px;
            border-left: 5px solid {'#28a745' if cumple else '#dc3545'};
        }}
        .tendencias {{
            margin: 30px 0;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 20px 0;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background: #3498db;
            color: white;
            font-weight: bold;
        }}
        tr:hover {{
            background: #f5f5f5;
        }}
        .footer {{
            text-align: center;
            margin-top: 30px;
            color: #7f8c8d;
            font-size: 12px;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>🏨 REPORTE DE MÉTRICAS - SISTEMA DE RESERVAS DE HOTEL</h1>
        <p style="text-align: center; color: #7f8c8d;">
            Día {ultimo_dia.dia} | {ultimo_dia.fecha}
        </p>
        
        <div class="resumen">
            <div class="metrica-card">
                <h3>📊 Cobertura de Pruebas</h3>
                <div class="metrica-valor">{ultimo_dia.cobertura}%</div>
                <span class="semaforo {'verde' if ultimo_dia.cobertura >= 85 else 'amarillo' if ultimo_dia.cobertura >= 75 else 'rojo'}"></span>
                <small>Meta: ≥85%</small>
            </div>
            
            <div class="metrica-card">
                <h3>✅ Tasa de Éxito</h3>
                <div class="metrica-valor">{ultimo_dia.tasa_exito}%</div>
                <span class="semaforo {'verde' if ultimo_dia.tasa_exito >= 90 else 'amarillo' if ultimo_dia.tasa_exito >= 80 else 'rojo'}"></span>
                <small>Meta: ≥90%</small>
            </div>
            
            <div class="metrica-card">
                <h3>🐛 Defectos Críticos</h3>
                <div class="metrica-valor">{ultimo_dia.defectos_criticos}</div>
                <span class="semaforo {'verde' if ultimo_dia.defectos_criticos == 0 else 'rojo'}"></span>
                <small>Meta: 0</small>
            </div>
            
            <div class="metrica-card">
                <h3>📈 Índice de Calidad</h3>
                <div class="metrica-valor">{ultimo_dia.indice_calidad}</div>
                <span class="semaforo {'verde' if ultimo_dia.indice_calidad >= 80 else 'amarillo' if ultimo_dia.indice_calidad >= 70 else 'rojo'}"></span>
                <small>Meta: ≥80</small>
            </div>
        </div>
        
        <div class="criterios">
            <h2>{'✅ Criterios de Salida CUMPLIDOS' if cumple else '⚠️ Criterios de Salida NO CUMPLIDOS'}</h2>
            {'<p><strong>El sistema está listo para pasar a producción.</strong></p>' if cumple else '<ul>'}
            {''.join([f'<li>{razon}</li>' for razon in razones]) if not cumple else ''}
            {'</ul>' if not cumple else ''}
        </div>
        
        <div class="tendencias">
            <h2>📈 Análisis de Tendencias</h2>
            <table>
                <thead>
                    <tr>
                        <th>Métrica</th>
                        <th>Tendencia</th>
                        <th>Interpretación</th>
                    </tr>
                </thead>
                <tbody>
"""
        
        interpretaciones = {
            'cobertura': ('ascendente', 'positivo', 'Se están ejecutando más casos'),
            'tasa_exito': ('ascendente', 'positivo', 'Mejora la calidad del software'),
            'densidad_defectos': ('descendente', 'positivo', 'Menos defectos por caso'),
            'defectos_abiertos': ('descendente', 'positivo', 'Se están resolviendo defectos'),
            'tasa_resolucion': ('ascendente', 'positivo', 'Mayor velocidad de corrección'),
            'indice_calidad': ('ascendente', 'positivo', 'Mejora general de calidad')
        }
        
        for metrica, tendencia in tendencias.items():
            esperada, tipo, interp = interpretaciones.get(metrica, ('', '', ''))
            es_buena = (tendencia == esperada)
            color = 'verde' if es_buena else 'amarillo' if tendencia == 'estable' else 'rojo'
            simbolo = {'ascendente': '↑', 'descendente': '↓', 'estable': '→'}.get(tendencia, '?')
            
            html += f"""
                    <tr>
                        <td><strong>{metrica.replace('_', ' ').title()}</strong></td>
                        <td><span class="semaforo {color}"></span> {simbolo} {tendencia.title()}</td>
                        <td>{interp}</td>
                    </tr>
"""
        
        html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Generado el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}</p>
            <p>Sistema de Métricas de Testing v1.0</p>
        </div>
    </div>
</body>
</html>
"""
        
        with open(archivo_salida, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"✅ Reporte HTML guardado en: {archivo_salida}")
        return archivo_salida


if __name__ == "__main__":
    from metricas_testing import MetricasTesting, crear_metricas_ejemplo
    
    print("📊 Generando Dashboard Visual\n")
    
    # Cargar o crear datos
    sistema = crear_metricas_ejemplo()
    
    # Crear dashboard
    dashboard = DashboardVisual(sistema)
    
    # Generar gráficos
    dashboard.generar_dashboard_completo("dashboard_metricas.png")
    
    # Generar reporte HTML
    dashboard.generar_reporte_html("reporte_metricas.html")
    
    print("\n✅ Archivos generados exitosamente")
    print("   • dashboard_metricas.png")
    print("   • reporte_metricas.html")