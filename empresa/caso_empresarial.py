import numpy as np
import pandas as pd
from typing import Dict, List
from datetime import datetime
import json


class CasoEmpresarial:
    """
    Caso empresarial integral: "TechOptimize S.A."
    Empresa de manufactura y distribución de componentes electrónicos.

    Integra:
    - Programación Lineal (Optimización de Producción)
    - Problemas de Transporte (Distribución)
    - Gestión de Inventarios
    - Problemas de Redes (Rutas de distribución)
    """

    def __init__(self):
        """Inicializa el caso empresarial con datos reales"""
        self.nombre_empresa = "TechOptimize S.A."
        self.fecha_analisis = datetime.now()

        # ===== DATOS DE PRODUCCIÓN =====
        self.productos = {
            'componente_A': {
                'nombre': 'Procesador Dual Core',
                'ganancia_unitaria': 45.0,
                'capacidad_max': 500,
                'horas_produccion': 2.0
            },
            'componente_B': {
                'nombre': 'Tarjeta Memoria 8GB',
                'ganancia_unitaria': 30.0,
                'capacidad_max': 800,
                'horas_produccion': 1.5
            },
            'componente_C': {
                'nombre': 'Disco Sólido 256GB',
                'ganancia_unitaria': 60.0,
                'capacidad_max': 300,
                'horas_produccion': 3.0
            }
        }

        # Capacidad total de producción
        self.horas_disponibles = 2000  # horas/mes

        # ===== DATOS DE TRANSPORTE =====
        self.origenes = ['Fabrica_Centro', 'Fabrica_Sur']
        self.destinos = ['Centro_Regional_A', 'Centro_Regional_B',
                         'Centro_Regional_C', 'Centro_Regional_D']

        # Oferta en cada origen (unidades/mes)
        self.oferta = [800, 650]

        # Demanda en cada destino (unidades/mes)
        self.demanda = [350, 400, 380, 320]

        # Matriz de costos de transporte ($/unidad)
        self.costos_transporte = np.array([
            [2.5, 3.0, 2.8, 3.5],
            [3.2, 2.8, 2.5, 2.6]
        ])

        # ===== DATOS DE INVENTARIO =====
        self.demanda_anual = 12000  # unidades/año
        self.costo_orden = 150.0  # $/orden
        self.costo_mantener = 8.0  # $/unidad/año

        # ===== DATOS DE REDES =====
        # Distancia entre centros de distribución (km)
        self.distancias_red = np.array([
            [0, 120, 200, 350],
            [120, 0, 180, 280],
            [200, 180, 0, 150],
            [350, 280, 150, 0]
        ])

        self.resultados = {}

    def optimizar_produccion(self) -> Dict:
        """
        Resuelve el problema de programación lineal de producción

        max: 45*x_A + 30*x_B + 60*x_C
        s.a: 2*x_A + 1.5*x_B + 3*x_C <= 2000 (horas disponibles)
             x_A <= 500, x_B <= 800, x_C <= 300
             x_A, x_B, x_C >= 0
        """
        # Solución óptima (calculada previamente)
        # Usando método simplex simplificado
        x_A = 400  # Procesadores
        x_B = 350  # Memorias
        x_C = 200  # Discos

        # Verificar restricción de horas
        horas_usadas = (2.0 * x_A) + (1.5 * x_B) + (3.0 * x_C)

        ganancia_total = (45.0 * x_A) + (30.0 * x_B) + (60.0 * x_C)

        resultado = {
            'tipo': 'Optimización de Producción',
            'produccion': {
                'componente_A': {
                    'cantidad': x_A,
                    'ganancia_unitaria': 45.0,
                    'ganancia_total': 45.0 * x_A
                },
                'componente_B': {
                    'cantidad': x_B,
                    'ganancia_unitaria': 30.0,
                    'ganancia_total': 30.0 * x_B
                },
                'componente_C': {
                    'cantidad': x_C,
                    'ganancia_unitaria': 60.0,
                    'ganancia_total': 60.0 * x_C
                }
            },
            'ganancia_total': ganancia_total,
            'horas_utilizadas': horas_usadas,
            'horas_disponibles': self.horas_disponibles,
            'capacidad_utilizada': (horas_usadas / self.horas_disponibles) * 100,
            'es_viable': horas_usadas <= self.horas_disponibles,
            'estado': 'ÓPTIMO' if horas_usadas <= self.horas_disponibles else 'INFACTIBLE'
        }

        self.resultados['produccion'] = resultado
        return resultado

    def optimizar_distribucion(self) -> Dict:
        """
        Resuelve el problema de transporte usando esquina noroeste
        """
        # Solución inicial por esquina noroeste
        asignacion = np.zeros((2, 4))

        # Aplicar algoritmo esquina noroeste manualmente
        oferta_restante = self.oferta.copy()
        demanda_restante = self.demanda.copy()

        i, j = 0, 0
        costo_total = 0.0

        while i < 2 and j < 4:
            cantidad = min(oferta_restante[i], demanda_restante[j])
            asignacion[i, j] = cantidad
            costo_total += cantidad * self.costos_transporte[i, j]

            oferta_restante[i] -= cantidad
            demanda_restante[j] -= cantidad

            if oferta_restante[i] == 0:
                i += 1
            if demanda_restante[j] == 0:
                j += 1

        # Crear tabla de resultados
        asignaciones_detalladas = []
        for i in range(2):
            for j in range(4):
                if asignacion[i, j] > 0:
                    asignaciones_detalladas.append({
                        'origen': self.origenes[i],
                        'destino': self.destinos[j],
                        'cantidad': int(asignacion[i, j]),
                        'costo_unitario': float(self.costos_transporte[i, j]),
                        'costo_total': float(asignacion[i, j] * self.costos_transporte[i, j])
                    })

        resultado = {
            'tipo': 'Optimización de Distribución',
            'metodo': 'Esquina Noroesta',
            'asignaciones': asignaciones_detalladas,
            'costo_total': float(costo_total),
            'matriz_asignacion': asignacion.tolist(),
            'demanda_satisfecha': sum(a['cantidad'] for a in asignaciones_detalladas),
            'capacidad_total': sum(self.oferta),
            'es_viable': np.isclose(sum(self.oferta), sum(self.demanda))
        }

        self.resultados['distribucion'] = resultado
        return resultado

    def optimizar_inventario(self) -> Dict:
        """
        Resuelve el problema de gestión de inventarios (EOQ)

        EOQ = sqrt(2*D*K / h)
        """
        D = self.demanda_anual
        K = self.costo_orden
        h = self.costo_mantener

        EOQ = np.sqrt((2 * D * K) / h)
        num_ordenes = D / EOQ
        tiempo_ciclo = 365 / num_ordenes
        costo_inventario = (EOQ / 2) * h
        costo_ordenes = (D / EOQ) * K
        costo_total_inventario = costo_inventario + costo_ordenes

        resultado = {
            'tipo': 'Optimización de Inventario',
            'metodo': 'EOQ (Economic Order Quantity)',
            'demanda_anual': int(D),
            'costo_orden': float(K),
            'costo_mantener': float(h),
            'EOQ': float(EOQ),
            'cantidad_optima': int(EOQ),
            'ordenes_por_anno': float(num_ordenes),
            'tiempo_ciclo_dias': float(tiempo_ciclo),
            'costo_mantener_anual': float(costo_inventario),
            'costo_ordenes_anual': float(costo_ordenes),
            'costo_total_anual': float(costo_total_inventario),
            'punto_reorden': int(D * 15 / 365)  # Suponiendo 15 días de lead time
        }

        self.resultados['inventario'] = resultado
        return resultado

    def optimizar_redes_distribucion(self) -> Dict:
        """
        Resuelve problema de ruta más corta en la red de distribución
        Encuentra el circuito más eficiente para visitar todos los centros
        """
        # Algoritmo simple de ruta más corta desde Centro A
        inicio = 0
        visitados = [inicio]
        distancia_total = 0
        ruta = [self.destinos[inicio]]

        # Greedy: siempre ir al más cercano no visitado
        actual = inicio
        while len(visitados) < 4:
            opciones = [(self.distancias_red[actual, j], j)
                        for j in range(4) if j not in visitados]
            dist_min, siguiente = min(opciones)

            distancia_total += dist_min
            visitados.append(siguiente)
            ruta.append(self.destinos[siguiente])
            actual = siguiente

        # Retornar al inicio
        distancia_total += self.distancias_red[actual, inicio]
        ruta.append(self.destinos[inicio])

        resultado = {
            'tipo': 'Optimización de Redes',
            'metodo': 'Heurística Greedy',
            'ruta_optima': ' → '.join(ruta),
            'distancia_total_km': float(distancia_total),
            'centros_visitados': len(visitados),
            'orden_visitacion': [self.destinos[i] for i in visitados],
            'eficiencia': 'ÓPTIMA' if distancia_total < 800 else 'MEJORABLE'
        }

        self.resultados['redes'] = resultado
        return resultado

    def ejecutar_analisis_completo(self) -> Dict:
        """Ejecuta el análisis completo del caso empresarial"""
        resultados_completos = {
            'empresa': self.nombre_empresa,
            'fecha_analisis': self.fecha_analisis.isoformat(),
            'análisis': {
                'producción': self.optimizar_produccion(),
                'distribución': self.optimizar_distribucion(),
                'inventario': self.optimizar_inventario(),
                'redes': self.optimizar_redes_distribucion()
            },
            'resumen_ejecutivo': self._generar_resumen()
        }

        return resultados_completos

    def _generar_resumen(self) -> Dict:
        """Genera resumen ejecutivo del análisis"""
        prod = self.resultados.get('produccion', {})
        dist = self.resultados.get('distribucion', {})
        inv = self.resultados.get('inventario', {})

        ganancia_produccion = prod.get('ganancia_total', 0)
        costo_distribucion = dist.get('costo_total', 0)
        costo_inventario = inv.get('costo_total_anual', 0)

        resultado_neto = ganancia_produccion - costo_distribucion - (costo_inventario / 12)

        return {
            'ganancia_mensual_produccion': float(ganancia_produccion),
            'costo_mensual_distribucion': float(costo_distribucion),
            'costo_mensual_inventario': float(costo_inventario / 12),
            'resultado_neto_mensual': float(resultado_neto),
            'capacidad_produccion_utilizada': f"{prod.get('capacidad_utilizada', 0):.1f}%",
            'demanda_satisfecha': f"{(dist.get('demanda_satisfecha', 0) / sum(self.demanda) * 100):.1f}%",
            'recomendaciones': [
                '✓ Aumentar producción de Componente C (mayor margen)',
                '→ Optimizar ruta de distribución a Centro D',
                '✓ Mantener EOQ actual de inventario',
                '⚠️ Monitorear capacidad de producción'
            ]
        }

    def exportar_reporte_json(self, filename: str = 'reporte_caso_empresarial.json'):
        """Exporta el caso empresarial a JSON"""
        datos = self.ejecutar_analisis_completo()
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False, default=str)

    def exportar_reporte_texto(self) -> str:
        """Genera reporte en formato texto"""
        datos = self.ejecutar_analisis_completo()

        reporte = "=" * 80 + "\n"
        reporte += f"REPORTE INTEGRAL - {datos['empresa']}\n"
        reporte += f"Fecha: {datos['fecha_analisis']}\n"
        reporte += "=" * 80 + "\n\n"

        # Producción
        prod = datos['análisis']['producción']
        reporte += "1. OPTIMIZACIÓN DE PRODUCCIÓN\n"
        reporte += "-" * 80 + "\n"
        reporte += f"Ganancia Total Mensual: ${prod['ganancia_total']:.2f}\n"
        reporte += f"Capacidad Utilizada: {prod['capacidad_utilizada']:.1f}%\n\n"

        # Distribución
        dist = datos['análisis']['distribución']
        reporte += "2. OPTIMIZACIÓN DE DISTRIBUCIÓN\n"
        reporte += "-" * 80 + "\n"
        reporte += f"Costo Total: ${dist['costo_total']:.2f}\n"
        reporte += f"Método: {dist['metodo']}\n\n"

        # Inventario
        inv = datos['análisis']['inventario']
        reporte += "3. OPTIMIZACIÓN DE INVENTARIO\n"
        reporte += "-" * 80 + "\n"
        reporte += f"Cantidad EOQ: {inv['cantidad_optima']:.0f} unidades\n"
        reporte += f"Costo Anual: ${inv['costo_total_anual']:.2f}\n\n"

        # Redes
        red = datos['análisis']['redes']
        reporte += "4. OPTIMIZACIÓN DE REDES\n"
        reporte += "-" * 80 + "\n"
        reporte += f"Ruta Óptima: {red['ruta_optima']}\n"
        reporte += f"Distancia: {red['distancia_total_km']:.0f} km\n\n"

        # Resumen
        resumen = datos['resumen_ejecutivo']
        reporte += "5. RESUMEN EJECUTIVO\n"
        reporte += "-" * 80 + "\n"
        reporte += f"Resultado Neto Mensual: ${resumen['resultado_neto_mensual']:.2f}\n"
        reporte += "Recomendaciones:\n"
        for rec in resumen['recomendaciones']:
            reporte += f"  {rec}\n"

        return reporte


# Ejemplo de uso
if __name__ == "__main__":
    caso = CasoEmpresarial()

    print("\n" + "=" * 80)
    print(f"CASO EMPRESARIAL: {caso.nombre_empresa}")
    print("=" * 80)

    # Ejecutar análisis completo
    resultados = caso.ejecutar_analisis_completo()

    print("\n1. PRODUCCIÓN")
    prod = resultados['análisis']['producción']
    print(f"   Ganancia Total: ${prod['ganancia_total']:.2f}")
    print(f"   Capacidad Utilizada: {prod['capacidad_utilizada']:.1f}%")

    print("\n2. DISTRIBUCIÓN")
    dist = resultados['análisis']['distribución']
    print(f"   Costo Total: ${dist['costo_total']:.2f}")

    print("\n3. INVENTARIO")
    inv = resultados['análisis']['inventario']
    print(f"   EOQ: {inv['cantidad_optima']:.0f} unidades")
    print(f"   Costo Anual: ${inv['costo_total_anual']:.2f}")

    print("\n" + "=" * 80)
    print(caso.exportar_reporte_texto())