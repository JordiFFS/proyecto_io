# models/inventarios/inventario_basico.py

"""
Módulo de Gestión de Inventarios
Implementa los modelos clásicos de gestión de inventarios:
- EOQ (Economic Order Quantity)
- Punto de Reorden
- Control de inventarios con demanda estocástica
"""

import math


class ModeloEOQ:
    """
    Modelo de Cantidad Económica de Orden (EOQ)
    Minimiza el costo total de inventario
    """

    def __init__(self, demanda_anual, costo_orden, costo_mantener):
        """
        Args:
            demanda_anual: Demanda anual en unidades
            costo_orden: Costo por orden colocada (USD)
            costo_mantener: Costo mantener una unidad por año (USD)
        """
        self.demanda_anual = demanda_anual
        self.costo_orden = costo_orden
        self.costo_mantener = costo_mantener
        self.pasos = []

    def resolver(self):
        """
        Calcula la cantidad económica de orden

        Returns:
            dict: Contiene EOQ, número de órdenes, costo total, etc.
        """
        # Fórmula EOQ: Q* = sqrt(2*D*S/H)
        Q_estrella = math.sqrt(2 * self.demanda_anual * self.costo_orden / self.costo_mantener)

        # Número de órdenes por año
        num_ordenes = self.demanda_anual / Q_estrella

        # Tiempo entre órdenes (días)
        dias_entre_ordenes = 365 / num_ordenes

        # Inventario promedio
        inventario_promedio = Q_estrella / 2

        # Costo total anual
        costo_ordenes_anual = self.demanda_anual / Q_estrella * self.costo_orden
        costo_almacen_anual = inventario_promedio * self.costo_mantener
        costo_total = costo_ordenes_anual + costo_almacen_anual

        # Guardar pasos
        self.pasos = [
            {
                'paso': 1,
                'descripcion': 'Identificar parámetros',
                'contenido': f'D={self.demanda_anual}, S={self.costo_orden}, H={self.costo_mantener}'
            },
            {
                'paso': 2,
                'descripcion': 'Aplicar fórmula EOQ',
                'contenido': f'Q* = √(2*{self.demanda_anual}*{self.costo_orden}/{self.costo_mantener}) = {Q_estrella:.0f} unidades'
            },
            {
                'paso': 3,
                'descripcion': 'Calcular número de órdenes',
                'contenido': f'N = {self.demanda_anual}/{Q_estrella:.0f} = {num_ordenes:.2f} órdenes/año'
            }
        ]

        return {
            'Q_estrella': Q_estrella,
            'num_ordenes': num_ordenes,
            'dias_entre_ordenes': dias_entre_ordenes,
            'inventario_promedio': inventario_promedio,
            'costo_ordenes_anual': costo_ordenes_anual,
            'costo_almacen_anual': costo_almacen_anual,
            'costo_total': costo_total,
            'pasos': self.pasos
        }


class PuntoReorden:
    """
    Calcula el punto de reorden para un artículo
    con demanda constante y lead time variable
    """

    def __init__(self, demanda_diaria, lead_time_dias, desv_std_demanda=None, nivel_servicio=0.95):
        """
        Args:
            demanda_diaria: Demanda promedio diaria
            lead_time_dias: Días de entrega del proveedor
            desv_std_demanda: Desviación estándar de la demanda (opcional)
            nivel_servicio: Nivel de servicio deseado (0-1)
        """
        self.demanda_diaria = demanda_diaria
        self.lead_time_dias = lead_time_dias
        self.desv_std_demanda = desv_std_demanda
        self.nivel_servicio = nivel_servicio

    def resolver(self):
        """
        Calcula punto de reorden simple y con stock de seguridad

        Returns:
            dict: ROP simple, ROP con seguridad, stock de seguridad
        """
        # ROP simple: R = d*L
        rop_simple = self.demanda_diaria * self.lead_time_dias

        # Stock de seguridad (si se conoce desviación)
        stock_seguridad = 0
        rop_con_seguridad = rop_simple

        if self.desv_std_demanda:
            # Z score para nivel de servicio
            z_scores = {
                0.85: 1.04,
                0.90: 1.28,
                0.95: 1.645,
                0.99: 2.33,
            }
            z = z_scores.get(self.nivel_servicio, 1.645)

            # Stock de seguridad: SS = z * σ * sqrt(L)
            stock_seguridad = z * self.desv_std_demanda * math.sqrt(self.lead_time_dias)
            rop_con_seguridad = rop_simple + stock_seguridad

        return {
            'rop_simple': rop_simple,
            'rop_con_seguridad': rop_con_seguridad,
            'stock_seguridad': stock_seguridad,
            'demanda_durante_lead_time': rop_simple
        }


class ControlInventario:
    """
    Control de inventario con capacidad limitada
    Considera custos de mantener vs. costo de escasez
    """

    def __init__(self, stock_actual, stock_minimo, stock_maximo,
                 demanda_diaria, costo_mantener, costo_escasez):
        """
        Args:
            stock_actual: Stock actual en unidades
            stock_minimo: Stock mínimo permitido
            stock_maximo: Capacidad máxima de almacén
            demanda_diaria: Demanda diaria promedio
            costo_mantener: Costo diario de mantener una unidad
            costo_escasez: Costo de no tener una unidad disponible
        """
        self.stock_actual = stock_actual
        self.stock_minimo = stock_minimo
        self.stock_maximo = stock_maximo
        self.demanda_diaria = demanda_diaria
        self.costo_mantener = costo_mantener
        self.costo_escasez = costo_escasez

    def evaluar_estado(self):
        """
        Evalúa el estado actual del inventario

        Returns:
            dict: Estado actual, recomendación de acción
        """
        estado = "NORMAL"
        accion = "Continuar monitoreando"
        urgencia = 0

        if self.stock_actual <= self.stock_minimo:
            estado = "CRÍTICO"
            accion = "ORDENAR INMEDIATAMENTE"
            urgencia = 3
        elif self.stock_actual <= self.stock_minimo * 1.5:
            estado = "BAJO"
            accion = "Preparar orden de compra"
            urgencia = 2
        elif self.stock_actual >= self.stock_maximo * 0.9:
            estado = "ALTO"
            accion = "Revisar pronóstico de demanda"
            urgencia = 1

        dias_con_stock = self.stock_actual / self.demanda_diaria if self.demanda_diaria > 0 else 0

        return {
            'estado': estado,
            'accion': accion,
            'urgencia': urgencia,
            'stock_actual': self.stock_actual,
            'stock_minimo': self.stock_minimo,
            'stock_maximo': self.stock_maximo,
            'dias_con_stock': dias_con_stock,
            'capacidad_utilizada': (self.stock_actual / self.stock_maximo) * 100
        }

    def calcular_cantidad_ordenar(self, dias_para_reorden=14):
        """
        Calcula la cantidad a ordenar basado en EOQ y restricciones

        Args:
            dias_para_reorden: Días disponibles para la próxima orden

        Returns:
            dict: Cantidad a ordenar, costo estimado
        """
        # Demanda esperada
        demanda_esperada = self.demanda_diaria * dias_para_reorden

        # Cantidad a ordenar para llegar a stock máximo
        cantidad_ideal = self.stock_maximo - self.stock_actual

        # Ajustar por demanda esperada
        cantidad_ordenar = max(demanda_esperada, cantidad_ideal)

        # No exceder capacidad
        cantidad_ordenar = min(cantidad_ordenar, self.stock_maximo - self.stock_actual)

        return {
            'cantidad_a_ordenar': max(0, cantidad_ordenar),
            'stock_esperado_post_orden': self.stock_actual + cantidad_ordenar,
            'demanda_esperada_periodo': demanda_esperada
        }


class InventarioMateriaPrima:
    """
    Control especializado para materias primas perecederas
    Considera fecha de vencimiento y rotación FIFO
    """

    def __init__(self, nombre, stock_actual, stock_minimo, stock_maximo,
                 dias_vida_util, costo_unitario, costo_almacen_diario,
                 demanda_diaria, es_perecedera=False):
        """
        Args:
            nombre: Nombre del producto
            stock_actual: Stock actual
            stock_minimo: Stock mínimo
            stock_maximo: Stock máximo
            dias_vida_util: Días de vida útil del producto
            costo_unitario: Costo por unidad
            costo_almacen_diario: Costo diario de almacén
            demanda_diaria: Demanda diaria
            es_perecedera: ¿Es perecedera?
        """
        self.nombre = nombre
        self.stock_actual = stock_actual
        self.stock_minimo = stock_minimo
        self.stock_maximo = stock_maximo
        self.dias_vida_util = dias_vida_util
        self.costo_unitario = costo_unitario
        self.costo_almacen_diario = costo_almacen_diario
        self.demanda_diaria = demanda_diaria
        self.es_perecedera = es_perecedera

    def calcular_riesgo_vencimiento(self, dias_almacenados=None):
        """
        Calcula el riesgo de vencimiento del inventario

        Args:
            dias_almacenados: Días que lleva almacenado (opcional)

        Returns:
            dict: Porcentaje de riesgo, cantidad en riesgo
        """
        if not self.es_perecedera:
            return {
                'en_riesgo': False,
                'porcentaje_riesgo': 0,
                'cantidad_en_riesgo': 0
            }

        dias_almacenados = dias_almacenados or (self.dias_vida_util / 2)
        dias_restantes = self.dias_vida_util - dias_almacenados

        # Riesgo aumenta cuando quedan < 30% de vida útil
        if dias_restantes <= self.dias_vida_util * 0.3:
            porcentaje_riesgo = 100 * (1 - dias_restantes / self.dias_vida_util)
            cantidad_en_riesgo = self.stock_actual * (porcentaje_riesgo / 100)
        else:
            porcentaje_riesgo = 0
            cantidad_en_riesgo = 0

        return {
            'en_riesgo': porcentaje_riesgo > 0,
            'porcentaje_riesgo': porcentaje_riesgo,
            'cantidad_en_riesgo': cantidad_en_riesgo,
            'dias_restantes': dias_restantes,
            'vida_util_dias': self.dias_vida_util
        }

    def recomendar_acciones(self):
        """
        Proporciona recomendaciones de acción basadas en análisis

        Returns:
            list: Lista de recomendaciones
        """
        recomendaciones = []

        # Análisis de nivel de stock
        if self.stock_actual <= self.stock_minimo:
            recomendaciones.append("URGENTE: Stock crítico - Ordenar inmediatamente")
        elif self.stock_actual <= self.stock_minimo * 1.5:
            recomendaciones.append("Preparar orden de compra - Stock bajo")

        # Análisis para perecederos
        if self.es_perecedera:
            riesgo = self.calcular_riesgo_vencimiento()
            if riesgo['en_riesgo']:
                cantidad = riesgo['cantidad_en_riesgo']
                recomendaciones.append(
                    f"Riesgo de vencimiento: {riesgo['porcentaje_riesgo']:.1f}% "
                    f"({cantidad:.0f} unidades en riesgo)"
                )
                recomendaciones.append("Aplicar política FIFO - Priorizar venta de stock antiguo")

        # Análisis de capacidad
        if self.stock_actual >= self.stock_maximo * 0.9:
            recomendaciones.append("Stock alto - Revisar demanda y estrategia de ventas")

        # Análisis de rotación
        dias_con_stock = self.stock_actual / self.demanda_diaria if self.demanda_diaria > 0 else 0
        if dias_con_stock > 30:
            recomendaciones.append(f"Stock para {dias_con_stock:.0f} días - Alto período de rotación")

        return recomendaciones if recomendaciones else ["Situación normal - Continuar monitoreando"]