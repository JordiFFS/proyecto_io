# 🚀 Guía Rápida - Sistema de Optimización Empresarial

## ¡Comienza en 5 minutos!

### 1️⃣ Instalación Rápida
```bash
# Clonar repositorio
cd jordiffs-proyecto_io

# Crear ambiente virtual
python -m venv venv

# Activar ambiente
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
```

### 2️⃣ Configuración Mínima

Crear archivo `.env`:
```env
GEMINI_API_KEY=tu_api_key (opcional)
```

### 3️⃣ Ejecutar Aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá en `http://localhost:8501`

---

## 📊 Casos de Uso Rápidos

### Caso 1: Resolver Problema de Programación Lineal

1. Ve a **📈 Programación Lineal**
2. Selecciona **"Ejecutar Ejemplo Coca-Cola"**
3. Elige método: **Simplex**
4. ¡Listo! Verás la solución paso a paso

### Caso 2: Optimizar Distribución de Bebidas

1. Ve a **🚚 Problemas de Transporte**
2. Selecciona **"Método Esquina Noroeste"**
3. Usa datos de ejemplo **"Coca-Cola"**
4. Visualiza la matriz de asignación óptima

### Caso 3: Encontrar Ruta Más Eficiente

1. Ve a **🌐 Problemas de Redes**
2. Selecciona **"Ruta Más Corta (Dijkstra)"**
3. Ingresa distancias entre plantas y centros
4. ¡Obtén la ruta óptima!

### Caso 4: Analizar Empresa Coca-Cola Completa

1. Ve a **🏭 Caso Empresarial Coca-Cola**
2. Revisa información de plantas, centros y productos
3. Observa KPIs del negocio
4. Explora problemas de optimización sugeridos

---

## 🤖 Usar Análisis con IA

Todos los métodos incluyen análisis automático con:
- 🤖 **Gemini** (Google)
- 🧠 **Hugging Face** (Open Source)
- 💻 **Ollama** (Local)

Los análisis aparecen automáticamente al final de cada sección en **pestañas comparativas**.

---

## 📁 Estructura Mínima del Proyecto
```
jordiffs-proyecto_io/
├── app.py
├── requirements.txt
├── .env
├── models/
│   ├── programacion_lineal/
│   ├── transporte/
│   ├── redes/
│   └── inventarios/
├── views/
├── ia/
├── empresa/
│   ├── caso_empresarial.py
│   └── datos_empresa.py
└── venv/
```

---

## ⚡ Comandos Útiles

| Comando | Descripción |
|---------|-------------|
| `streamlit run app.py` | Iniciar aplicación |
| `streamlit run app.py --logger.level=debug` | Modo debug |
| `pip install -r requirements.txt` | Instalar dependencias |
| `python -m venv venv` | Crear ambiente virtual |
| `ollama serve` | Iniciar Ollama (para análisis local) |

---

## 🔧 Solución Rápida de Problemas

### ❌ "Port 8501 already in use"
```bash
streamlit run app.py --server.port=8502
```

### ❌ "ModuleNotFoundError: streamlit"
```bash
pip install streamlit==1.28.1
```

### ❌ "GEMINI_API_KEY not found"
1. Obtén key en https://makersuite.google.com
2. Cópialo en archivo `.env`
3. Reinicia la aplicación

### ❌ "Ollama connection error"
```bash
# En otra terminal:
ollama serve
```

---

## 📚 Documentación Completa

Para información detallada, consulta:
- **README.md** - Documentación completa del proyecto
- **CASO_EMPRESA.md** - Información detallada de Coca-Cola

---

## 🎯 Próximos Pasos

1. ✅ Instala y ejecuta la aplicación
2. ✅ Prueba con ejemplos de Coca-Cola
3. ✅ Explora diferentes métodos de optimización
4. ✅ Analiza resultados con IA
5. ✅ Revisa documentación completa para casos avanzados

---

**¡Listo! Ya puedes usar el sistema de optimización. 🚀**