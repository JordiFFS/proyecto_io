# empresa/datos_empresa.py

"""
Datos de la empresa Coca-Cola para el análisis de optimización
Incluye parámetros reales y simulados para los diferentes modelos
"""

# ============================================================================
# 1. INFORMACIÓN GENERAL DE LA EMPRESA
# ============================================================================

EMPRESA_INFO = {
    "nombre": "Coca-Cola Embotelladora Nacional",
    "tipo": "Industria de Bebidas",
    "ubicacion": "Quito, Ecuador",
    "fundacion": 2010,
    "empleados": 450,
    "descripcion": "Empresa dedicada a la producción, embotellamiento y distribución de bebidas Coca-Cola"
}

# ============================================================================
# 2. PLANTAS DE PRODUCCIÓN
# ============================================================================

PLANTAS = {
    "Planta_Quito": {
        "nombre": "Planta Quito",
        "ubicacion": "Quito - Pichincha",
        "capacidad_diaria": 50000,  # botellas/día
        "capacidad_mensual": 1500000,  # botellas/mes
        "productos": ["Coca-Cola", "Sprite", "Fanta"],
        "costo_produccion_unitario": 0.85,  # USD por botella
        "eficiencia": 0.95,  # 95%
    },
    "Planta_Guayaquil": {
        "nombre": "Planta Guayaquil",
        "ubicacion": "Guayaquil - Guayas",
        "capacidad_diaria": 45000,  # botellas/día
        "capacidad_mensual": 1350000,  # botellas/mes
        "productos": ["Coca-Cola", "Fanta"],
        "costo_produccion_unitario": 0.80,  # USD por botella
        "eficiencia": 0.93,
    },
    "Planta_Cuenca": {
        "nombre": "Planta Cuenca",
        "ubicacion": "Cuenca - Azuay",
        "capacidad_diaria": 30000,  # botellas/día
        "capacidad_mensual": 900000,  # botellas/mes
        "productos": ["Sprite", "Fanta"],
        "costo_produccion_unitario": 0.88,  # USD por botella
        "eficiencia": 0.90,
    }
}

# ============================================================================
# 3. CENTROS DE DISTRIBUCIÓN
# ============================================================================

CENTROS_DISTRIBUCION = {
    "Centro_Quito": {
        "nombre": "Centro de Distribución Quito",
        "ubicacion": "Quito",
        "capacidad_almacenamiento": 500000,  # botellas
        "costo_almacenamiento_diario": 0.02,  # USD por botella
        "punto_reorden": 100000,  # botellas
    },
    "Centro_Guayaquil": {
        "nombre": "Centro de Distribución Guayaquil",
        "ubicacion": "Guayaquil",
        "capacidad_almacenamiento": 450000,  # botellas
        "costo_almacenamiento_diario": 0.025,  # USD por botella
        "punto_reorden": 90000,
    },
    "Centro_Cuenca": {
        "nombre": "Centro de Distribución Cuenca",
        "ubicacion": "Cuenca",
        "capacidad_almacenamiento": 250000,  # botellas
        "costo_almacenamiento_diario": 0.03,  # USD por botella
        "punto_reorden": 50000,
    }
}

# ============================================================================
# 4. PUNTOS DE VENTA Y DEMANDA
# ============================================================================

PUNTOS_VENTA = {
    "SupermercadoA": {
        "nombre": "Supermercado A",
        "ubicacion": "Quito",
        "demanda_diaria": 5000,  # botellas/día
        "margen": 0.30,  # 30%
        "tipo": "Supermercado"
    },
    "SupermercadoB": {
        "nombre": "Supermercado B",
        "ubicacion": "Guayaquil",
        "demanda_diaria": 4500,  # botellas/día
        "margen": 0.30,
        "tipo": "Supermercado"
    },
    "TiendaDistribuidor1": {
        "nombre": "Distribuidor mayorista 1",
        "ubicacion": "Quito",
        "demanda_diaria": 8000,  # botellas/día
        "margen": 0.25,  # 25%
        "tipo": "Mayorista"
    },
    "TiendaDistribuidor2": {
        "nombre": "Distribuidor mayorista 2",
        "ubicacion": "Guayaquil",
        "demanda_diaria": 7500,  # botellas/día
        "margen": 0.25,
        "tipo": "Mayorista"
    },
    "TiendaMinorista1": {
        "nombre": "Tienda minorista 1",
        "ubicacion": "Cuenca",
        "demanda_diaria": 3000,  # botellas/día
        "margen": 0.35,  # 35%
        "tipo": "Minorista"
    },
    "TiendaMinorista2": {
        "nombre": "Tienda minorista 2",
        "ubicacion": "Quito",
        "demanda_diaria": 2500,  # botellas/día
        "margen": 0.35,
        "tipo": "Minorista"
    }
}

# ============================================================================
# 5. PRODUCTOS Y PRECIOS
# ============================================================================

PRODUCTOS = {
    "Coca_Cola": {
        "nombre": "Coca-Cola 500ml",
        "precio_venta": 1.50,  # USD
        "costo_produccion": 0.85,  # USD
        "demanda_promedio_diaria": 15000,  # botellas
        "margen_bruto": 0.65,  # 65%
    },
    "Sprite": {
        "nombre": "Sprite 500ml",
        "precio_venta": 1.40,  # USD
        "costo_produccion": 0.80,  # USD
        "demanda_promedio_diaria": 10000,  # botellas
        "margen_bruto": 0.60,
    },
    "Fanta": {
        "nombre": "Fanta 500ml",
        "precio_venta": 1.35,  # USD
        "costo_produccion": 0.75,  # USD
        "demanda_promedio_diaria": 12000,  # botellas
        "margen_bruto": 0.64,
    }
}

# ============================================================================
# 6. MATERIAS PRIMAS
# ============================================================================

MATERIAS_PRIMAS = {
    "Agua": {
        "nombre": "Agua purificada",
        "unidad": "litros",
        "costo_unitario": 0.05,  # USD/litro
        "consumo_por_botella": 0.5,  # litros
        "stock_actual": 100000,  # litros
        "stock_minimo": 20000,  # litros
        "stock_maximo": 200000,  # litros
        "perecedera": False,
    },
    "Jarabe": {
        "nombre": "Jarabe concentrado",
        "unidad": "litros",
        "costo_unitario": 2.50,  # USD/litro
        "consumo_por_botella": 0.1,  # litros
        "stock_actual": 15000,  # litros
        "stock_minimo": 3000,  # litros
        "stock_maximo": 25000,  # litros
        "perecedera": True,
        "vida_util_dias": 180,
    },
    "Botellas": {
        "nombre": "Botellas de plástico 500ml",
        "unidad": "unidades",
        "costo_unitario": 0.15,  # USD/botella
        "consumo_por_botella": 1,  # botellas
        "stock_actual": 200000,  # unidades
        "stock_minimo": 50000,  # unidades
        "stock_maximo": 300000,  # unidades
        "perecedera": False,
    },
    "Etiquetas": {
        "nombre": "Etiquetas impresas",
        "unidad": "unidades",
        "costo_unitario": 0.05,  # USD/etiqueta
        "consumo_por_botella": 1,  # etiquetas
        "stock_actual": 250000,  # unidades
        "stock_minimo": 50000,  # unidades
        "stock_maximo": 400000,  # unidades
        "perecedera": False,
    },
    "Tapas": {
        "nombre": "Tapas de botellas",
        "unidad": "unidades",
        "costo_unitario": 0.08,  # USD/tapa
        "consumo_por_botella": 1,  # tapas
        "stock_actual": 220000,  # unidades
        "stock_minimo": 40000,  # unidades
        "stock_maximo": 350000,  # unidades
        "perecedera": False,
    }
}

# ============================================================================
# 7. COSTOS DE TRANSPORTE (Matriz de distancias entre plantas y distribuidores)
# ============================================================================

# Costo de transporte por botella (USD) desde plantas a centros de distribución
COSTOS_TRANSPORTE_DISTRIBUCION = {
    "Planta_Quito": {
        "Centro_Quito": 0.05,
        "Centro_Guayaquil": 0.15,
        "Centro_Cuenca": 0.08,
    },
    "Planta_Guayaquil": {
        "Centro_Quito": 0.15,
        "Centro_Guayaquil": 0.05,
        "Centro_Cuenca": 0.12,
    },
    "Planta_Cuenca": {
        "Centro_Quito": 0.08,
        "Centro_Guayaquil": 0.12,
        "Centro_Cuenca": 0.04,
    }
}

# Costo de transporte por botella (USD) desde centros de distribución a puntos de venta
COSTOS_TRANSPORTE_VENTA = {
    "Centro_Quito": {
        "SupermercadoA": 0.03,
        "TiendaDistribuidor1": 0.02,
        "TiendaMinorista2": 0.03,
        "SupermercadoB": 0.15,
        "TiendaDistribuidor2": 0.15,
        "TiendaMinorista1": 0.12,
    },
    "Centro_Guayaquil": {
        "SupermercadoB": 0.03,
        "TiendaDistribuidor2": 0.02,
        "SupermercadoA": 0.15,
        "TiendaDistribuidor1": 0.15,
        "TiendaMinorista1": 0.12,
        "TiendaMinorista2": 0.15,
    },
    "Centro_Cuenca": {
        "TiendaMinorista1": 0.03,
        "SupermercadoB": 0.12,
        "TiendaDistribuidor2": 0.12,
        "SupermercadoA": 0.15,
        "TiendaDistribuidor1": 0.15,
        "TiendaMinorista2": 0.15,
    }
}

# ============================================================================
# 8. PARÁMETROS DE PROGRAMACIÓN LINEAL
# ============================================================================

# Demanda mensual por producto (en botellas)
DEMANDA_MENSUAL = {
    "Coca_Cola": 450000,  # botellas/mes
    "Sprite": 300000,  # botellas/mes
    "Fanta": 360000,  # botellas/mes
}

# Capacidad de producción mensual por planta y producto
CAPACIDAD_PRODUCCION = {
    "Planta_Quito": {
        "Coca_Cola": 600000,
        "Sprite": 500000,
        "Fanta": 400000,
    },
    "Planta_Guayaquil": {
        "Coca_Cola": 550000,
        "Sprite": 450000,
        "Fanta": 350000,
    },
    "Planta_Cuenca": {
        "Coca_Cola": 400000,
        "Sprite": 300000,
        "Fanta": 200000,
    }
}

# Costo de producción unitario por planta
COSTO_PRODUCCION_PLANTA = {
    "Planta_Quito": 0.85,
    "Planta_Guayaquil": 0.80,
    "Planta_Cuenca": 0.88,
}

# ============================================================================
# 9. PARÁMETROS DE INVENTARIO
# ============================================================================

PARAMETROS_INVENTARIO = {
    "costo_mantener_unitario": 0.02,  # USD por botella por día
    "costo_ordenes": 50,  # USD por orden
    "tasa_demanda_anual": 3650000,  # botellas/año (promedio)
    "dias_lead_time": 3,  # días de entrega
    "nivel_servicio": 0.95,  # 95% de disponibilidad
}

# ============================================================================
# 10. PARÁMETROS DE REDES (Nodos para problemas de redes)
# ============================================================================

NODOS_RED = {
    "plantas": list(PLANTAS.keys()),
    "centros_distribucion": list(CENTROS_DISTRIBUCION.keys()),
    "puntos_venta": list(PUNTOS_VENTA.keys()),
}

# ============================================================================
# 11. INFORMACIÓN ADICIONAL
# ============================================================================

HORAS_OPERACION_DIARIA = 24
DIAS_OPERACION_MES = 30
DIAS_OPERACION_ANIO = 365

# Horarios de distribución
HORARIOS_DISTRIBUCION = {
    "Quito": {"inicio": "06:00", "fin": "18:00"},
    "Guayaquil": {"inicio": "06:00", "fin": "18:00"},
    "Cuenca": {"inicio": "07:00", "fin": "19:00"},
}

# Porcentaje de demanda por región
DISTRIBUCION_DEMANDA_REGIONAL = {
    "Quito": 0.40,  # 40%
    "Guayaquil": 0.35,  # 35%
    "Cuenca": 0.25,  # 25%
}