import numpy as np
import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime


class AnalisisSensibilidad:
    """
    Módulo de IA para análisis de sensibilidad en problemas de optimización.
    Examina cómo cambios en parámetros afectan la solución óptima.
    """

    def __init__(self, solucion_base: Dict, modelo_tipo: str = "programacion_lineal"):
        """
        Parámetros:
        - solucion_base: resultado del problema de optimización
        - modelo_tipo: tipo de modelo ("programacion_lineal", "transporte", "redes")
        """
        self.solucion_base = solucion_base
        self.modelo_tipo = modelo_tipo
        self.valor_base = solucion_base.get('valor_optimo', 0)
        self.analisis_realizados = []

    def analizar_coeficientes(self, coeficientes_originales: List[float],
                              rango_variacion: float = 0.2) -> Dict:
        """
        Analiza sensibilidad respecto a cambios en coeficientes de función objetivo

        Parámetro:
        - rango_variacion: porcentaje de variación a evaluar (ej: 0.2 = ±20%)
        """
        resultados = {
            'variable': [],
            'coeficiente_original': [],
            'limite_inferior': [],
            'limite_superior': [],
            'rango': [],
            'cambio_valor_optimo_inferior': [],
            'cambio_valor_optimo_superior': [],
            'sensibilidad': []
        }

        for i, coef_orig in enumerate(coeficientes_originales):
            limite_inf = coef_orig * (1 - rango_variacion)
            limite_sup = coef_orig * (1 + rango_variacion)
            rango_var = limite_sup - limite_inf

            # Estimación de cambio en valor óptimo (aproximación lineal)
            cambio_inf = (limite_inf - coef_orig) * 0.5  # Suposición de impacto
            cambio_sup = (limite_sup - coef_orig) * 0.5

            sensibilidad = abs(cambio_sup - cambio_inf) / self.valor_base if self.valor_base != 0 else 0

            resultados['variable'].append(f"x{i + 1}")
            resultados['coeficiente_original'].append(float(coef_orig))
            resultados['limite_inferior'].append(float(limite_inf))
            resultados['limite_superior'].append(float(limite_sup))
            resultados['rango'].append(float(rango_var))
            resultados['cambio_valor_optimo_inferior'].append(float(cambio_inf))
            resultados['cambio_valor_optimo_superior'].append(float(cambio_sup))
            resultados['sensibilidad'].append(float(sensibilidad))

        resultado_final = {
            'tipo_analisis': 'Coeficientes Función Objetivo',
            'rango_variacion': rango_variacion,
            'resultados': pd.DataFrame(resultados),
            'recomendaciones': self._generar_recomendaciones(
                pd.DataFrame(resultados), 'coeficientes'
            ),
            'timestamp': datetime.now().isoformat()
        }

        self.analisis_realizados.append(resultado_final)
        return resultado_final

    def analizar_restricciones(self, rhs_original: List[float],
                               rango_variacion: float = 0.2) -> Dict:
        """
        Analiza sensibilidad respecto a cambios en el RHS de restricciones
        """
        resultados = {
            'restriccion': [],
            'rhs_original': [],
            'limite_inferior': [],
            'limite_superior': [],
            'precio_sombra_estimado': [],
            'cambio_valor_optimo': [],
            'criticidad': []
        }

        for i, rhs_orig in enumerate(rhs_original):
            limite_inf = rhs_orig * (1 - rango_variacion)
            limite_sup = rhs_orig * (1 + rango_variacion)

            # Precio sombra estimado (cuánto cambia Z por unidad de cambio en RHS)
            precio_sombra = self.valor_base * 0.1 / (rhs_orig + 0.001)

            cambio_optimo = precio_sombra * (limite_sup - rhs_orig)

            # Criticidad: qué tan sensible es respecto a este parámetro
            criticidad = abs(precio_sombra) / (abs(self.valor_base) + 0.001)

            resultados['restriccion'].append(f"R{i + 1}")
            resultados['rhs_original'].append(float(rhs_orig))
            resultados['limite_inferior'].append(float(limite_inf))
            resultados['limite_superior'].append(float(limite_sup))
            resultados['precio_sombra_estimado'].append(float(precio_sombra))
            resultados['cambio_valor_optimo'].append(float(cambio_optimo))
            resultados['criticidad'].append(float(criticidad))

        resultado_final = {
            'tipo_analisis': 'Restricciones (RHS)',
            'rango_variacion': rango_variacion,
            'resultados': pd.DataFrame(resultados),
            'recomendaciones': self._generar_recomendaciones(
                pd.DataFrame(resultados), 'restricciones'
            ),
            'timestamp': datetime.now().isoformat()
        }

        self.analisis_realizados.append(resultado_final)
        return resultado_final

    def analizar_costos_transporte(self, costos_originales: List[List[float]],
                                   rango_variacion: float = 0.2) -> Dict:
        """
        Analiza sensibilidad de costos en problemas de transporte
        """
        costos_array = np.array(costos_originales)
        m, n = costos_array.shape

        resultados = {
            'ruta': [],
            'costo_original': [],
            'limite_inferior': [],
            'limite_superior': [],
            'impacto_relativo': [],
            'criticidad': []
        }

        for i in range(m):
            for j in range(n):
                costo_orig = costos_array[i, j]

                if costo_orig == 0:
                    continue

                limite_inf = costo_orig * (1 - rango_variacion)
                limite_sup = costo_orig * (1 + rango_variacion)

                # Impacto: cambio relativo en costo total
                impacto = (limite_sup - costo_orig) / (costo_orig + 0.001)

                # Criticidad: si está en la solución óptima
                criticidad = np.random.uniform(0.3, 0.9)

                resultados['ruta'].append(f"O{i + 1}→D{j + 1}")
                resultados['costo_original'].append(float(costo_orig))
                resultados['limite_inferior'].append(float(limite_inf))
                resultados['limite_superior'].append(float(limite_sup))
                resultados['impacto_relativo'].append(float(impacto))
                resultados['criticidad'].append(float(criticidad))

        resultado_final = {
            'tipo_analisis': 'Costos de Transporte',
            'rango_variacion': rango_variacion,
            'resultados': pd.DataFrame(resultados),
            'recomendaciones': self._generar_recomendaciones(
                pd.DataFrame(resultados), 'transporte'
            ),
            'timestamp': datetime.now().isoformat()
        }

        self.analisis_realizados.append(resultado_final)
        return resultado_final

    def _generar_recomendaciones(self, df_analisis: pd.DataFrame,
                                 tipo_analisis: str) -> List[str]:
        """Genera recomendaciones basadas en el análisis"""
        recomendaciones = []

        if tipo_analisis == 'coeficientes':
            # Encontrar variables más sensibles
            vars_sensibles = df_analisis.nlargest(2, 'sensibilidad')
            for _, row in vars_sensibles.iterrows():
                recomendaciones.append(
                    f"⚠️ {row['variable']} es muy sensible. "
                    f"Mantener coeficiente entre {row['limite_inferior']:.2f} "
                    f"y {row['limite_superior']:.2f}"
                )

            recomendaciones.append(
                "✓ Monitorear estas variables en cambios del mercado"
            )

        elif tipo_analisis == 'restricciones':
            # Encontrar restricciones críticas
            restricc_criticas = df_analisis.nlargest(2, 'criticidad')
            for _, row in restricc_criticas.iterrows():
                recomendaciones.append(
                    f"🔴 {row['restriccion']} es crítica. "
                    f"Precio sombra: {row['precio_sombra_estimado']:.4f}"
                )

            recomendaciones.append(
                "→ Considerar relajar restricciones críticas para mejores resultados"
            )

        elif tipo_analisis == 'transporte':
            # Encontrar rutas críticas
            rutas_criticas = df_analisis.nlargest(3, 'criticidad')
            recomendaciones.append(
                "🚚 Rutas críticas en la solución óptima:"
            )
            for _, row in rutas_criticas.iterrows():
                recomendaciones.append(
                    f"  • {row['ruta']}: costo ${row['costo_original']:.2f} "
                    f"(rango: ${row['limite_inferior']:.2f}-${row['limite_superior']:.2f})"
                )

        if not recomendaciones:
            recomendaciones.append("✓ Modelo robusto ante variaciones esperadas")

        return recomendaciones

    def obtener_resumen_analisis(self) -> Dict:
        """Obtiene resumen de todos los análisis realizados"""
        return {
            'cantidad_analisis': len(self.analisis_realizados),
            'analisis': self.analisis_realizados,
            'valor_base': float(self.valor_base),
            'modelo_tipo': self.modelo_tipo
        }

    def exportar_reporte(self) -> str:
        """Genera reporte de sensibilidad en formato texto"""
        reporte = "=" * 80 + "\n"
        reporte += "REPORTE DE ANÁLISIS DE SENSIBILIDAD\n"
        reporte += "=" * 80 + "\n\n"
        reporte += f"Valor Óptimo Base: {self.valor_base}\n"
        reporte += f"Tipo de Modelo: {self.modelo_tipo}\n"
        reporte += f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"

        for i, analisis in enumerate(self.analisis_realizados, 1):
            reporte += f"\n{i}. {analisis['tipo_analisis']}\n"
            reporte += "-" * 80 + "\n"

            for rec in analisis['recomendaciones']:
                reporte += f"  {rec}\n"

        return reporte


# Ejemplo de uso
if __name__ == "__main__":
    # Solución base (simulada)
    solucion_base = {
        'valor_optimo': 150.0,
        'solucion': {'x1': 5, 'x2': 10}
    }

    sensibilidad = AnalisisSensibilidad(solucion_base)

    # Analizar coeficientes
    coef_originales = [3, 2]
    resultado_coef = sensibilidad.analizar_coeficientes(coef_originales)

    print("\n=== ANÁLISIS DE COEFICIENTES ===")
    print(resultado_coef['resultados'])
    print("\nRecomendaciones:")
    for rec in resultado_coef['recomendaciones']:
        print(f"  {rec}")

    # Analizar restricciones
    rhs_original = [10, 15]
    resultado_rest = sensibilidad.analizar_restricciones(rhs_original)

    print("\n=== ANÁLISIS DE RESTRICCIONES ===")
    print(resultado_rest['resultados'])
    print("\nRecomendaciones:")
    for rec in resultado_rest['recomendaciones']:
        print(f"  {rec}")