# ⚡ GUÍA RÁPIDA - Primeros Pasos

## 5 Pasos para Empezar

### 1️⃣ Configurar Ambiente Virtual

```bash
# Navegar al proyecto
cd jordiffs-proyecto_io

# Crear ambiente
python -m venv venv

# Activar (elegir según tu SO)
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Deberías ver: (venv) C:\...>
```

### 2️⃣ Instalar Dependencias

```bash
# Opción A: Una línea
pip install streamlit numpy pandas pyngrok scipy matplotlib seaborn scikit-learn python-dotenv

# Opción B: Desde archivo
pip install -r requirements.txt

# Verificar
pip list
```

### 3️⃣ Ejecutar Aplicación

```bash
# Modo local (más simple)
streamlit run app.py

# Se abrirá automáticamente en: http://localhost:8501
```

### 4️⃣ (Opcional) Ejecutar con ngrok

```bash
# Primero instalar ngrok
# Windows: choco install ngrok
# Mac: brew install ngrok

# Ejecutar con acceso remoto
python run_ngrok.py --ngrok

# Ver URL pública en console o http://localhost:4040
```

### 5️⃣ ¡Listo! Explorar la App

- Abre el navegador en `http://localhost:8501`
- Selecciona una opción del menú lateral
- Experimenta con cada módulo

---

## 🧪 Pruebas Rápidas

### Probar Simplex (desde Python)

```python
# Crear archivo: test_simplex.py

from models.programacion_lineal.simplex import Simplex

# max: 3x + 2y s.a x+y <= 10, 2x+y <= 15
c = [3, 2]
A = [[1, 1], [2, 1]]
b = [10, 15]

simplex = Simplex(c, A, b, tipo="max")
resultado = simplex.resolver()

print(f"Valor Óptimo: {resultado['valor_optimo']}")  # Debería ser 25
print(f"x1={resultado['solucion']['x1']}, x2={resultado['solucion']['x2']}")
```

**Ejecutar:**
```bash
python test_simplex.py
```

### Probar Transporte (desde Python)

```python
# Crear archivo: test_transporte.py

from models.transporte.esquina_noroeste import EsquinaNoreste

costos = [[2, 3, 1], [6, 5, 3], [1, 2, 5]]
oferta = [50, 60, 40]
demanda = [40, 70, 40]

transporte = EsquinaNoreste(costos, oferta, demanda)
resultado = transporte.resolver()

print(f"Costo Total: ${resultado['costo_total']:.2f}")
print("\nAsignaciones:")
for asig in resultado['asignaciones_detalladas']:
    print(f"  {asig['origen']} → {asig['destino']}: {asig['cantidad']} unid @ ${asig['costo_unitario']}")
```

**Ejecutar:**
```bash
python test_transporte.py
```

### Probar Caso Empresarial (desde Python)

```python
# Crear archivo: test_caso.py

from empresa.caso_empresarial import CasoEmpresarial

caso = CasoEmpresarial()
resultados = caso.ejecutar_analisis_completo()

print(caso.exportar_reporte_texto())
```

**Ejecutar:**
```bash
python test_caso.py
```

---

## 📋 Checklist de Implementación

- [ ] **Ambiente Virtual** ✅
  - [ ] Creado con `python -m venv venv`
  - [ ] Activado (prompt muestra `(venv)`)

- [ ] **Dependencias** ✅
  - [ ] streamlit instalado
  - [ ] numpy, pandas instalados
  - [ ] Verificado con `pip list`

- [ ] **Módulos Principales** ✅
  - [ ] `Simplex` implementado y funcional
  - [ ] `EsquinaNoreste` implementado y funcional
  - [ ] `RutaMasCorta` (Dijkstra) implementado
  - [ ] `CasoEmpresarial` implementado

- [ ] **Aplicación Streamlit** ✅
  - [ ] `app.py` creado
  - [ ] Interfaz con todas las secciones
  - [ ] Formularios para entrada de datos
  - [ ] Visualización de resultados

- [ ] **Análisis de Sensibilidad IA** ✅
  - [ ] Módulo `AnalisisSensibilidad` creado
  - [ ] Generación de recomendaciones
  - [ ] Integrado en la app

- [ ] **Documentación** ✅
  - [ ] README.md completo
  - [ ] Docstrings en módulos
  - [ ] Ejemplos de uso
  - [ ] Guía de troubleshooting

---

## 🚀 Próximos Pasos (Completar Implementación)

### Funcionalidades Adicionales Recomendadas

1. **Métodos de Transporte:**
   - [ ] Implementar `CostoMinimo`
   - [ ] Implementar `Vogel`
   - [ ] Implementar `PruebaOptimalidad`

2. **Métodos de Programación Lineal:**
   - [ ] Implementar `DosFases`
   - [ ] Implementar `GranM`
   - [ ] Implementar `Dual`

3. **Problemas de Redes:**
   - [ ] Implementar `ArbolExpansionMinima` (Kruskal, Prim)
   - [ ] Implementar `FlujoMaximo` (Ford-Fulkerson)
   - [ ] Implementar `FlujoCostoMinimo`

4. **Mejoras a la Interfaz:**
   - [ ] Gráficos interactivos de redes
   - [ ] Visualización de tablas simplex dinámicas
   - [ ] Exportación a PDF/Excel
   - [ ] Historial persistente

5. **Validaciones:**
   - [ ] Entrada de datos robusta
   - [ ] Mensajes de error claros
   - [ ] Validación de dimensiones matriciales

---

## 🎓 Recursos de Aprendizaje

### Algoritmos Implementados

| Algoritmo | Archivo | Complejidad | Referencia |
|-----------|---------|-------------|-----------|
| Simplex | `simplex.py` | O(nm) | Taha (Cap 3) |
| Esquina Noroeste | `esquina_noroeste.py` | O(m+n) | Taha (Cap 5) |
| Dijkstra | `ruta_corta.py` | O(V log V) | CLRS |
| EOQ | `inventario_basico.py` | O(1) | Winston (Cap 17) |

### Documentación Online

- [Streamlit Docs](https://docs.streamlit.io)
- [NumPy Guide](https://numpy.org/doc/)
- [Pandas Tutorial](https://pandas.pydata.org/docs/)
- [ngrok Docs](https://ngrok.com/docs)

---

## 💾 Estructura de Datos Clave

### Resultado de Simplex

```python
{
    'exito': bool,
    'valor_optimo': float,
    'solucion': {
        'x1': float,
        'x2': float,
        ...
    },
    'iteraciones': int,
    'tabla_final': list,
    'base_final': list,
    'tipo_optimizacion': 'max' | 'min'
}
```

### Resultado de Transporte

```python
{
    'metodo': str,
    'costo_total': float,
    'asignacion_matriz': list,
    'asignaciones_detalladas': [
        {
            'origen': str,
            'destino': str,
            'cantidad': float,
            'costo_unitario': float,
            'costo_total': float
        }
    ],
    'variables_basicas': int,
    'es_viable': bool
}
```

### Resultado de Ruta Más Corta

```python
{
    'algoritmo': 'Dijkstra',
    'nodo_origen': str,
    'rutas': [
        {
            'destino': str,
            'distancia': float,
            'ruta': str,
            'ruta_indices': list
        }
    ],
    'distancias': dict,
    'predecesores': dict
}
```

---

## 🐛 Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| `ModuleNotFoundError: streamlit` | No instalado | `pip install streamlit` |
| `FileNotFoundError: app.py` | Ruta incorrecta | `cd jordiffs-proyecto_io` |
| `Permission denied: venv` | Ambiente no activado | Activar: `source venv/bin/activate` |
| `Port 8501 in use` | Puerto ocupado | `streamlit run app.py --server.port=8502` |
| `ngrok not found` | ngrok no instalado | Descargar desde ngrok.com |

---

## 📊 Ejemplo de Entrada/Salida

### Input: Problema de PL

```
Función Objetivo: max 3x₁ + 2x₂
Restricción 1: x₁ + x₂ ≤ 10
Restricción 2: 2x₁ + x₂ ≤ 15
No negatividad: x₁, x₂ ≥ 0
```

### Output: Solución

```
✅ SOLUCIÓN ÓPTIMA ENCONTRADA

Valor Óptimo: Z = 25.00

Variables de Decisión:
  x₁ = 5.00
  x₂ = 5.00

Iteraciones: 2

Restricciones:
  R₁: 10.00 / 10.00 (100% utilizada)
  R₂: 15.00 / 15.00 (100% utilizada)
```

---

## 🎯 Meta Final

Cuando todo esté funcionando, deberías ser capaz de:

✅ Ejecutar `streamlit run app.py` y ver la interfaz
✅ Seleccionar cualquier módulo (PL, Transporte, Redes, etc.)
✅ Ingresar datos y obtener resultados
✅ Ver análisis de sensibilidad automático
✅ Ejecutar caso empresarial completo
✅ Acceder remotamente con ngrok

---

**¡Buena suerte con tu proyecto! 🚀**