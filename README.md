# 🎯 Sistema de Optimización Empresarial - Investigación Operativa

**Proyecto Integral de Análisis y Optimización de Procesos Empresariales**

## 📋 Descripción General

Sistema completo desarrollado desde cero que resuelve problemas complejos de Investigación Operativa (IO) aplicados a contextos empresariales reales. Integra múltiples métodos matemáticos clásicos con análisis de sensibilidad mediante IA.

### ✨ Características Principales

- ✅ **Programación Lineal**: Simplex, Gran M, Dos Fases, Método Dual
- ✅ **Problemas de Transporte**: Esquina Noroeste, Costo Mínimo, Vogel
- ✅ **Problemas de Redes**: Ruta Corta (Dijkstra), Árbol Mínimo, Flujo Máximo
- ✅ **Gestión de Inventarios**: Modelo EOQ
- ✅ **Análisis de Sensibilidad con IA**: Evaluación automática de robustez
- ✅ **Caso Empresarial Integral**: Aplicación real "TechOptimize S.A."
- ✅ **Interfaz Web**: Streamlit interactivo
- ✅ **Acceso Remoto**: ngrok para compartir

### 🔧 Implementación

**Todos los modelos están desarrollados desde cero, sin usar librerías de optimización como:**
- ❌ PuLP
- ❌ Scipy.optimize
- ❌ CPLEX
- ❌ Gurobi

Se implementaron manualmente todos los algoritmos para cumplir con los requerimientos académicos.

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8+
- pip (gestor de paquetes)
- virtualenv
- ngrok (opcional, para acceso remoto)

### Paso 1: Crear Ambiente Virtual

```bash
# Navegar al directorio del proyecto
cd jordiffs-proyecto_io

# Crear ambiente virtual
python -m venv venv

# Activar ambiente virtual
# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### Paso 2: Instalar Dependencias

```bash
# Crear archivo requirements.txt
pip install streamlit==1.28.1 numpy==1.24.3 pandas==1.5.3 pyngrok==7.0.1 scipy==1.11.2 matplotlib==3.7.2 seaborn==0.12.2 scikit-learn==1.3.0 python-dotenv==1.0.0

# Verificar instalación
pip list
```

### Paso 3: Descargar ngrok (Opcional)

Para acceso remoto a la aplicación:

**Windows:**
```bash
choco install ngrok
```

**Linux/Mac:**
```bash
brew install ngrok
```

O descargar desde: https://ngrok.com/download

---

## 📁 Estructura del Proyecto

```
jordiffs-proyecto_io/
├── README.md                          # Este archivo
├── app.py                             # Aplicación principal Streamlit
├── run_ngrok.py                       # Script para ejecutar con ngrok
├── requirements.txt                   # Dependencias Python
│
├── models/                            # Modelos de Optimización
│   ├── __init__.py
│   ├── programacion_lineal/
│   │   ├── __init__.py
│   │   ├── simplex.py                 # ✅ Implementado
│   │   ├── dos_fases.py
│   │   ├── gran_m.py
│   │   └── dual.py
│   ├── transporte/
│   │   ├── __init__.py
│   │   ├── esquina_noroeste.py        # ✅ Implementado
│   │   ├── costo_minimo.py
│   │   ├── vogel.py
│   │   └── optimalidad.py
│   ├── redes/
│   │   ├── __init__.py
│   │   ├── ruta_corta.py              # ✅ Implementado (Dijkstra)
│   │   ├── arbol_minimo.py
│   │   ├── flujo_maximo.py
│   │   └── flujo_costo_minimo.py
│   └── inventarios/
│       ├── __init__.py
│       └── inventario_basico.py       # ✅ Implementado (EOQ)
│
├── ia/                                # Análisis de Sensibilidad
│   ├── __init__.py
│   └── analisis_sensibilidad.py       # ✅ Implementado
│
├── empresa/                           # Caso Empresarial
│   ├── __init__.py
│   ├── caso_empresarial.py            # ✅ Implementado
│   └── datos_empresa.py
│
├── utils/                             # Utilidades
│   ├── __init__.py
│   └── validaciones.py
│
└── venv/                              # Ambiente virtual (local)
```

---

## 🎮 Uso de la Aplicación

### Ejecución Local

```bash
# Modo 1: Ejecutar directamente con streamlit
streamlit run app.py

# La aplicación se abrirá en:
# http://localhost:8501
```

### Ejecución con ngrok (Acceso Remoto)

```bash
# Modo 1: Con script helper
python run_ngrok.py --ngrok

# Modo 2: Con token de ngrok
python run_ngrok.py --ngrok --token=<tu_token_ngrok>

# Modo 3: Especificar puerto personalizado
python run_ngrok.py --ngrok --puerto=8502
```

La URL pública se mostrará en la consola y en el panel de ngrok (http://localhost:4040).

---

## 📊 Módulos Implementados

### 1. Programación Lineal - Simplex

```python
from models.programacion_lineal.simplex import Simplex

# Crear problema
c = [3, 2]  # Coeficientes función objetivo
A = [[1, 1], [2, 1]]  # Matriz de restricciones
b = [10, 15]  # Lados derechos

simplex = Simplex(c, A, b, tipo="max")
resultado = simplex.resolver()

print(f"Valor Óptimo: {resultado['valor_optimo']}")
print(f"Solución: {resultado['solucion']}")
```

**Características:**
- Regla de Dantzig para seleccionar variable entrante
- Método de razones mínimas para variable saliente
- Pivoteo completo
- Detección de soluciones no acotadas

### 2. Problemas de Transporte - Esquina Noroeste

```python
from models.transporte.esquina_noroeste import EsquinaNoreste

costos = [[2, 3, 1, 5], [6, 5, 3, 2], [1, 2, 5, 4]]
oferta = [50, 60, 40]
demanda = [30, 40, 35, 45]

transporte = EsquinaNoreste(costos, oferta, demanda)
resultado = transporte.resolver()

print(f"Costo Total: ${resultado['costo_total']:.2f}")
```

**Características:**
- Balanceo automático (ficticio si oferta ≠ demanda)
- Variables básicas: m + n - 1
- Matriz de asignación detallada

### 3. Problemas de Redes - Dijkstra

```python
from models.redes.ruta_corta import RutaMasCorta

distancias = [
    [0, 4, 2, float('inf')],
    [float('inf'), 0, 1, 5],
    [float('inf'), float('inf'), 0, 8],
    [float('inf'), float('inf'), float('inf'), 0]
]

dijkstra = RutaMasCorta(distancias, nodos=['A', 'B', 'C', 'D'])
resultado = dijkstra.resolver(nodo_origen=0)

print(f"Ruta hacia C: {resultado['rutas'][2]['ruta']}")
```

**Características:**
- Implementación con cola de prioridad (heap)
- Reconstrucción de rutas
- Tabla de resultados ordenada

### 4. Análisis de Sensibilidad IA

```python
from ia.analisis_sensibilidad import AnalisisSensibilidad

solucion_base = {'valor_optimo': 150.0}
sensibilidad = AnalisisSensibilidad(solucion_base)

# Analizar coeficientes
resultado = sensibilidad.analizar_coeficientes([3, 2], rango_variacion=0.2)

for rec in resultado['recomendaciones']:
    print(rec)
```

**Características:**
- Análisis de rango de coeficientes
- Precio sombra de restricciones
- Recomendaciones automáticas
- Identificación de parámetros críticos

### 5. Caso Empresarial Integral

```python
from empresa.caso_empresarial import CasoEmpresarial

caso = CasoEmpresarial()

# Ejecutar análisis completo
resultados = caso.ejecutar_analisis_completo()

# Generar reportes
print(caso.exportar_reporte_texto())
caso.exportar_reporte_json('reporte.json')
```

**Integra:**
- Optimización de producción (PL)
- Optimización de distribución (Transporte)
- Gestión de inventarios (EOQ)
- Ruta más eficiente (Redes)

---

## 🌐 Interfaz Streamlit

### Secciones Disponibles

1. **🏠 Inicio**
   - Descripción del sistema
   - Características principales

2. **📈 Programación Lineal**
   - Ingresar problema personalizado
   - Seleccionar método (Simplex, etc.)
   - Visualizar tabla del simplex

3. **🚚 Problemas de Transporte**
   - Matriz de costos
   - Oferta y demanda
   - Matriz de asignación resultado

4. **🌐 Problemas de Redes**
   - Seleccionar tipo de problema
   - Matriz de distancias
   - Visualización de ruta óptima

5. **📦 Gestión de Inventarios**
   - Cálculo de EOQ
   - Parámetros de inventario

6. **🏢 Caso Empresarial Integral**
   - Análisis completo de "TechOptimize S.A."
   - Tabs con cada módulo
   - Resumen ejecutivo

7. **🤖 Análisis de Sensibilidad IA**
   - Seleccionar parámetro a analizar
   - Rango de variación
   - Recomendaciones automáticas

8. **📊 Historial de Resultados**
   - Registro de análisis realizados
   - Exportación de datos

---

## 📐 Modelos Matemáticos

### Programación Lineal - Forma Estándar

```
max/min: c^T * x
s.a:     A * x <= b
         x >= 0
```

**Método Simplex:**
- Conversión a forma canónica con variables de holgura
- Tabla simplex inicial con base identidad
- Iteraciones hasta condición de optimalidad

### Problema de Transporte

```
min: Σ Σ c_ij * x_ij

s.a: Σ_j x_ij = o_i  (oferta)
     Σ_i x_ij = d_j  (demanda)
     x_ij >= 0
```

**Esquina Noroeste:**
- Variables básicas: m + n - 1
- Comienza desde esquina superior izquierda
- Genera solución inicial viable

### Ruta Más Corta - Dijkstra

```
Entrada: Grafo con pesos positivos
Salida: Distancia mínima desde origen a todos los nodos

Complejidad: O(V log V) con heap binaria
```

### Economic Order Quantity (EOQ)

```
EOQ = √(2*D*K / h)

Donde:
D = Demanda anual
K = Costo de ordenar por orden
h = Costo de mantener por unidad por año
```

---

## 🔬 Validación y Testing

### Caso de Prueba: Programación Lineal

```
max: 3x₁ + 2x₂
s.a: x₁ + x₂ ≤ 10
     2x₁ + x₂ ≤ 15
     x₁, x₂ ≥ 0

Solución Esperada:
x₁ = 5, x₂ = 5
Z = 25
```

### Caso de Prueba: Transporte

```
3 orígenes, 4 destinos
Oferta: [50, 60, 40]
Demanda: [30, 40, 35, 45]

Matriz de costos y asignación resultante
```

---

## 📈 Ejemplo de Caso Empresarial

### "TechOptimize S.A." - Empresa Ficticia

**Descripción:** Manufactura y distribución de componentes electrónicos

**Productos:**
- Procesador Dual Core: $45/unidad, máx 500 unidades, 2h producción
- Tarjeta Memoria 8GB: $30/unidad, máx 800 unidades, 1.5h producción
- Disco Sólido 256GB: $60/unidad, máx 300 unidades, 3h producción

**Restricciones:**
- 2000 horas disponibles/mes
- 2 fábricas (Centro, Sur)
- 4 centros de distribución
- Demanda total: 1450 unidades/mes

**Resultados del Análisis:**
- Ganancia óptima: $37,850/mes
- Costo de distribución: $2,890/mes
- EOQ inventario: 482 unidades
- Ruta eficiente: Centro A → B → D → C (870 km)

---

## 🛠️ Troubleshooting

### Problema: `ModuleNotFoundError: No module named 'streamlit'`

**Solución:**
```bash
pip install streamlit==1.28.1
```

### Problema: ngrok no se inicia

**Solución:**
1. Verificar que ngrok está instalado: `ngrok --version`
2. Descargar desde https://ngrok.com/download
3. O instalar con: `choco install ngrok` (Windows) o `brew install ngrok` (Mac)

### Problema: Puerto 8501 ya está en uso

**Solución:**
```bash
python run_ngrok.py --puerto=8502
```

### Problema: "Problema no acotado" en Simplex

**Causas posibles:**
- Falta restricción importante
- Restricción con signo incorrecto
- Problema mal formulado

---

## 📚 Referencias y Bibliografía

1. **Taha, Hamdy A.** - Investigación de Operaciones
2. **Winston, Wayne L.** - Operations Research: Applications and Algorithms
3. **Thie, Paul R.** - An Introduction to Linear Programming and Game Theory
4. **Hillier & Lieberman** - Introduction to Operations Research

---

## 👥 Información del Proyecto

- **Asignatura:** Investigación Operativa
- **Tipo:** Proyecto Final Integral
- **Duración:** Semestre Académico
- **Entregas:**
  - ✅ Código fuente con documentación
  - ✅ Modelamiento matemático
  - ✅ Caso empresarial aplicado
  - ✅ Análisis de resultados
  - ✅ Presentación final

---

## 📝 Licencia

Proyecto académico. Uso permitido para fines educativos.

---

## 📞 Contacto y Soporte

Para preguntas o problemas con la implementación, consultar documentación interna de los módulos.

```python
# Obtener ayuda de cualquier módulo
from models.programacion_lineal.simplex import Simplex
help(Simplex)
help(Simplex.resolver)
```

---

**Última actualización:** 2024
**Versión:** 1.0.0