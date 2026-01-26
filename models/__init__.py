"""
Módulo de Modelos de Investigación Operativa
Contiene implementaciones desde cero de:
- Programación Lineal
- Problemas de Transporte
- Problemas de Redes
- Gestión de Inventarios
"""

from .programacion_lineal.simplex import Simplex
from .transporte.esquina_noroeste import EsquinaNoreste
from .redes.ruta_corta import RutaMasCorta

__all__ = [
    'Simplex',
    'EsquinaNoreste',
    'RutaMasCorta'
]