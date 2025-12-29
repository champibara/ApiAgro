# Proyecto: Sistema de Apoyo a la Decisión Agropecuaria 🌾🚜

## 👥 Integrantes
* **Escobar Champi, Claudia Maria** (GitHub: champibara)
* **Condori Cieza, Esther Elizabeth** (GitHub: Esther0907)

## 📋 Descripción del Proyecto
Este proyecto surge ante la dificultad de acceder a información climática y ambiental dispersa. Proponemos un buscador temático orientado a la ganadería y agricultura que utiliza técnicas de extracción de datos para facilitar la toma de decisiones estratégicas.

## 🎯 Objetivos
* **Extraer** datos relativos al clima y ambiente de múltiples fuentes digitales.
* **Procesar y organizar** los datos recolectados de manera eficiente mediante lógica de programación.
* **Visualizar** la información mediante un mapa interactivo para identificar zonas de aptitud agropecuaria.

## ✨ Característica Principal: Mapa Inteligente
El sistema cuenta con un "Mapa Inteligente" que ofrece:
* **Distribución Territorial:** Muestra la aptitud agropecuaria por regiones usando indicadores como temperatura, humedad y precipitación.
* **Análisis por Zona:** Al seleccionar un área, indica los tipos de ganado recomendados y sus condiciones de crianza.

## 📊 Estructuración de Datos
La estructuración organiza los datos de entrada para que sean compatibles entre sí:
* **Conversión de Formatos:** Transformación de respuestas API (JSON) y tablas locales (CSV) en DataFrames de Pandas.
* **Homogeneización:** Asegura que todas las fuentes utilicen las mismas unidades de medida y nombres de regiones para permitir el cruce de información.

## ⚙️ Procesamiento de Datos
El procesamiento es el núcleo lógico del sistema donde ocurre la toma de decisiones:
* **Lógica de Comparación:** El sistema ejecuta algoritmos que contrastan la temperatura actual obtenida de la API contra los umbrales de supervivencia y confort registrados en los CSV.
* **Generación de Indicadores:** Se calcula automáticamente un "Índice de Aptitud". Si los valores climáticos coinciden con los rangos óptimos, el sistema marca la zona como favorable.
* **Automatización de Resultados:** El resultado se traduce en colores y etiquetas (Apto/No Apto) que alimentan la interfaz visual.

## 🛠️ Tecnologías Clave
* **Python + Pandas:** Manipulación de datos y lógica de negocio.
* **Streamlit:** Interfaz gráfica e interactividad.
* **Geopy & OpenWeather:** Motores de datos geográficos y climáticos.

## 📂 Estructura del Proyecto
```text
ApiAgro/
├── .devcontainer/
│   └── devcontainer.json    # Configuración de entorno estandarizado
├── data/referencias         # Bases de datos técnicas
│   ├── aves.csv
│   ├── bovinos.csv
│   ├── cultivos.csv
│   └── porcinos.csv
├── src/                     # Módulos de lógica y API
│   ├── __init__.py          # Inicializador de paquete Python
│   ├── agro_logic.py        # Procesamiento y lógica de aptitud
│   ├── api_client.py        # Conexión con OpenWeather y Geopy
│   └── map_utils.py         # Funciones para el Mapa Inteligente
├── app.py                   # Orquestador principal de Streamlit
├── requirements.txt         # Librerías (Pandas, Streamlit, etc.)
├── .gitignore               # Archivos excluidos del repositorio
└── README.md                # Documentación técnica
```

## 🚀 Guía de Instalación
### Opción A: Uso de DevContainer (Recomendado) 🐳
Este proyecto está configurado para ejecutarse en un entorno estandarizado. Si utilizas **Visual Studio Code**:
1. Abre la carpeta del proyecto.
2. Haz clic en el aviso **"Reopen in Container"** que aparecerá automáticamente.
3. El entorno se configurará solo, instalando Python y todas las dependencias necesarias.

### Opción B: Instalación Local Tradicional 💻
Si prefieres una instalación manual, sigue estos pasos:

1. **Clonar el repositorio** o descargar los archivos en tu computadora.
2. **Instalar las dependencias** necesarias ejecutando:
   ```bash
   pip install -r requirements.txt
   ```
3. **Ejecutar la aplicación con el siguiente comando:**
   ```bash
   streamlit run app.py
   ```
💡 Nota: La aplicación se abrirá automáticamente en una nueva pestaña de tu navegador predeterminado.
