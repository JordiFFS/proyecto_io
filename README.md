# 🎯 Sistema de Optimización Empresarial - Investigación Operativa

**Proyecto Integral de Análisis y Optimización de Procesos Empresariales**
**Caso Real: Coca-Cola Embotelladora Nacional**

## 📋 Descripción General

Sistema completo desarrollado desde cero que resuelve problemas complejos de Investigación Operativa (IO) aplicados a contextos empresariales reales. Integra múltiples métodos matemáticos clásicos con análisis de sensibilidad mediante IA (Gemini, Hugging Face, Ollama).

### ✨ Características Principales

#### 📐 Programación Lineal Completa
- **Simplex**: Método simplex completo con visualización paso a paso
- **Gran M**: Para problemas con restricciones de igualdad y desigualdad
- **Dos Fases**: Método de dos fases para problemas complejos
- **Método Dual**: Análisis de dualidad y precios sombra
- Visualización de 5 fases por iteración
- Análisis de costos reducidos y razones mínimas
- Detección de soluciones no acotadas e infactibles

#### 🚚 Problemas de Transporte
- **Esquina Noroeste**: Método de solución inicial
- **Costo Mínimo**: Minimización de costos de transporte
- **Vogel (VAM)**: Método con análisis de penalizaciones
- **MODI + Stepping Stone**: Optimización iterativa
- Visualización gráfica de rutas
- Verificación de restricciones

#### 🌐 Problemas de Redes
- **Dijkstra**: Ruta más corta
- **Kruskal**: Árbol de expansión mínima
- **Ford-Fulkerson**: Flujo máximo
- **Costo Mínimo**: Flujo de costo mínimo
- Visualización interactiva de grafos

#### 📦 Gestión de Inventarios
- **Modelo EOQ**: Economic Order Quantity
- Análisis de punto de reorden
- Consideración de productos perecederos
- Gráficos de evolución de inventario

#### 🤖 Análisis de Sensibilidad con IA Múltiple
- 🤖 **Gemini**: Análisis profundo y contextualizado
- 🧠 **Hugging Face**: Análisis con modelos open-source
- 💻 **Ollama**: Análisis completamente local
- Comparación automática de resultados
- Pestañas interactivas

#### 🏭 Caso Empresarial Integral Coca-Cola
- Análisis de producción multi-planta
- Optimización de distribución multi-nivel
- Gestión de inventarios de materias primas perecederas
- Análisis de sensibilidad estratégico
- KPIs del negocio

#### 🌐 Interfaz Web Interactiva
- Streamlit completa y responsiva
- Visualizaciones dinámicas
- Tablas interactivas

#### 🔄 Acceso Remoto
- ngrok para compartir y colaborar
- URL pública automática

---

## 🏭 Caso Empresarial: Coca-Cola Embotelladora Nacional

### 📊 Información General

| Parámetro | Valor |
|-----------|-------|
| **Empresa** | Coca-Cola Embotelladora Nacional |
| **Tipo** | Industria de Bebidas |
| **Ubicación** | Quito, Ecuador |
| **Fundación** | 2010 |
| **Empleados** | 450 |

### 🏭 Plantas de Producción

| Planta | Ubicación | Capacidad Mensual | Costo Unitario |
|--------|-----------|-------------------|----------------|
| **Quito** | Quito - Pichincha | 1,500,000 | $0.85 |
| **Guayaquil** | Guayaquil - Guayas | 1,350,000 | $0.80 |
| **Cuenca** | Cuenca - Azuay | 900,000 | $0.88 |

**Capacidad Total:** 3,750,000 botellas/mes

### 📦 Centros de Distribución

| Centro | Capacidad | Costo Almacenamiento |
|--------|-----------|----------------------|
| **Quito** | 500,000 | $0.02/botella/día |
| **Guayaquil** | 450,000 | $0.025/botella/día |
| **Cuenca** | 250,000 | $0.03/botella/día |

**Capacidad Total:** 1,200,000 botellas

### 🥤 Cartera de Productos

| Producto | Precio | Costo | Margen |
|----------|--------|-------|--------|
| **Coca-Cola** | $1.50 | $0.85 | 65% |
| **Sprite** | $1.40 | $0.80 | 60% |
| **Fanta** | $1.35 | $0.75 | 64% |

### 📊 KPIs Clave

- **Capacidad Total/Mes:** 3,750,000 botellas
- **Demanda Total/Mes:** 1,110,000 botellas
- **Utilidad de Capacidad:** 29.6%
- **Ingresos Potenciales/Mes:** $1,580,250
- **Margen Potencial/Mes:** $636,750

---

## 🚀 Instalación y Configuración

### Requisitos Previos

- Python 3.8+
- pip
- virtualenv
- ngrok (opcional)

### Paso 1: Crear Ambiente Virtual
```bash
# Navegar al directorio
cd jordiffs-proyecto_io

# Crear ambiente virtual
python -m venv venv

# Activar
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate
```

### Paso 2: Instalar Dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Configurar Variables de Entorno

Crear archivo `.env`:
```env
GEMINI_API_KEY=tu_api_key_aqui
HUGGING_FACE_API_KEY=tu_token_aqui
OLLAMA_BASE_URL=http://localhost:11434
OLLAMA_MODEL=mistral
NGROK_AUTH_TOKEN=tu_token_ngrok_aqui
```

### Paso 4: Instalar Ollama (Opcional)
```bash
# Windows
choco install ollama
ollama pull mistral
ollama serve

# Linux/Mac
brew install ollama
ollama pull mistral
ollama serve
```

---

## 🎮 Uso de la Aplicación

### Ejecución Local
```bash
streamlit run app.py
# http://localhost:8501
```

### Ejecución con ngrok
```bash
python run_ngrok.py --ngrok
```

---

## 📁 Estructura del Proyecto
```
jordiffs-proyecto_io/
├── README.md
├── GUIA_RAPIDA.md
├── CASO_EMPRESA.md
├── app.py
├── run_ngrok.py
├── requirements.txt
├── .env
│
├── models/
│   ├── programacion_lineal/
│   │   ├── simplex.py
│   │   ├── dos_fases.py
│   │   ├── gran_m.py
│   │   └── dual.py
│   ├── transporte/
│   │   ├── esquina_noroeste.py
│   │   ├── costo_minimo.py
│   │   ├── vogel.py
│   │   └── optimalidad.py
│   ├── redes/
│   │   ├── ruta_corta.py
│   │   ├── arbol_minimo.py
│   │   ├── flujo_maximo.py
│   │   └── flujo_costo_minimo.py
│   └── inventarios/
│       └── inventario_basico.py
│
├── views/
│   ├── resolucion_simplex.py
│   ├── resolucion_gran_m.py
│   ├── resolucion_dos_fases.py
│   ├── resolucion_dual.py
│   ├── resolucion_esquina_noroeste.py
│   ├── resolucion_costo_minimo_transporte.py
│   ├── resolucion_vogel.py
│   ├── resolucion_optimalidad.py
│   ├── resolucion_ruta_mas_corta.py
│   ├── resolucion_arbol_expansion_minima.py
│   ├── resolucion_flujo_maximo.py
│   ├── resolucion_costo_minimo.py
│   └── resolucion_inventario.py
│
├── ia/
│   ├── gemini.py
│   ├── huggingface_analisis_pl.py
│   ├── ollama_analisis_pl.py
│   └── analisis_sensibilidad.py
│
├── empresa/
│   ├── caso_empresarial.py
│   └── datos_empresa.py
│
├── utils/
│   └── validaciones.py
│
└── venv/
```

---

## 📊 Módulos Implementados

### 1. Programación Lineal - Simplex
```python
from models.programacion_lineal.simplex import Simplex

c = [0.65, 0.60, 0.60]
A = [[1, 1, 1], [1, 1, 1], [1, 1, 1], [1, 0, 0], [0, 1, 0], [0, 0, 1]]
b = [1500000, 1350000, 900000, 450000, 300000, 360000]

simplex = Simplex(c, A, b, tipo="max", nombres_vars=["Coca-Cola", "Sprite", "Fanta"])
resultado = simplex.resolver()

print(f"Valor Óptimo: ${resultado['valor_optimo']:.2f}")
```

### 2. Problemas de Transporte - Esquina Noroeste
```python
from models.transporte.esquina_noroeste import EsquinaNoreste

costos = [[0.05, 0.15, 0.08], [0.15, 0.05, 0.12], [0.08, 0.12, 0.04]]
oferta = [1500000, 1350000, 900000]
demanda = [500000, 450000, 250000]

esquina = EsquinaNoreste(costos, oferta, demanda)
resultado = esquina.resolver()

print(f"Costo Total: ${resultado['costo_total']:.2f}")
```

### 3. Problemas de Redes - Dijkstra
```python
from models.redes.ruta_corta import RutaMasCorta

distancias = [[0, 0.05, 0.15, 0.08], [0.05, 0, 0.15, 0.12], [0.15, 0.15, 0, 0.12], [0.08, 0.12, 0.12, 0]]

dijkstra = RutaMasCorta(distancias, nodos=['Planta_Quito', 'Centro_Quito', 'Centro_Guayaquil', 'Centro_Cuenca'])
resultado = dijkstra.resolver(nodo_origen=0)

for ruta in resultado['rutas']:
    print(f"{ruta['destino']}: {ruta['distancia']} km")
```

### 4. Gestión de Inventarios - EOQ
```python
from models.inventarios.inventario_basico import ModeloEOQ

demanda_anual = 3650000
costo_orden = 50
costo_mantener = 0.02

eoq = ModeloEOQ(demanda_anual, costo_orden, costo_mantener)
resultado = eoq.calcular()

print(f"EOQ: {resultado['eoq']:.0f} botellas")
```

### 5. Análisis de Sensibilidad IA
```python
from ia.gemini import generar_analisis_gemini
from ia.huggingface_analisis_pl import generar_analisis_huggingface
from ia.ollama_analisis_pl import generar_analisis_ollama

# Análisis con Gemini
analisis_gemini = generar_analisis_gemini(
    origen="Simplex",
    rutas=[{"destino": "Coca-Cola", "distancia": 450000, "ruta": "Coca-Cola"}],
    iteraciones=3,
    total_nodos=9
)

# Análisis con Hugging Face
analisis_hf = generar_analisis_huggingface(...)

# Análisis con Ollama
analisis_ollama = generar_analisis_ollama(...)
```

### 6. Caso Empresarial Integral
```python
from empresa.caso_empresarial import CasoEmpresarial

caso = CasoEmpresarial()
kpis = caso.calcular_indicadores_clave()

print(f"Capacidad: {kpis['capacidad_total_plantas']:,.0f}")
print(f"Demanda: {kpis['demanda_total_mensual']:,.0f}")
```

---

## 🌐 Interfaz Streamlit

### Secciones

1. **🏠 Inicio** - Descripción y características
2. **📈 Programación Lineal** - Simplex, Gran M, Dos Fases, Dual
3. **🚚 Transporte** - Esquina Noroeste, Costo Mínimo, Vogel, MODI
4. **🌐 Redes** - Dijkstra, Kruskal, Ford-Fulkerson, Costo Mínimo
5. **📦 Inventarios** - EOQ y gestión de stock
6. **🏭 Caso Coca-Cola** - Análisis empresarial completo
7. **🤖 Análisis IA** - Sensibilidad con múltiples IAs
8. **📊 Reportes** - Histórico y exportación

---

## 📐 Modelos Matemáticos

### Programación Lineal
```
max/min: c^T * x
s.a:     A * x <= b
         x >= 0
```

### Problema de Transporte
```
min: Σ Σ c_ij * x_ij
s.a: Σ_j x_ij = o_i
     Σ_i x_ij = d_j
     x_ij >= 0
```

### EOQ
```
EOQ = √(2*D*K / h)
Costo Total = (D/EOQ)*K + (EOQ/2)*h
```

---

## 🛠️ Troubleshooting

### Puerto en uso
```bash
streamlit run app.py --server.port=8502
```

### Falta módulo
```bash
pip install streamlit==1.28.1
```

### Gemini API
1. Obtén key en https://makersuite.google.com
2. Copia en `.env`

### Ollama no conecta
```bash
ollama serve
```

