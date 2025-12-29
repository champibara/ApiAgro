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

## 🏗️ Arquitectura del Sistema
El flujo lógico de los datos sigue un proceso estructurado para garantizar la integridad de la información desde la fuente hasta el usuario final:

\`\`\`mermaid
graph LR
    A[Fuentes Externas: API/CSV] --> B[Módulo de Extracción]
    B --> C[Transformación y Normalización - Pandas]
    C --> D[Cruce de Variables y Lógica de Aptitud]
    D --> E[Visualización: Mapa Inteligente]
\`\`\`
*Figura 1: Arquitectura lógica del flujo de datos (Pipeline).*

## 🛠️ Diseño y Planeamiento de la Extracción
El sistema integra tres fuentes de información:
1. **API de OpenWeather:** Datos climáticos en tiempo real.
2. **API de Geopy:** Localización y coordenadas geográficas.
3. **Archivos Estructurados (.CSV):** Parámetros técnicos de crianza y cultivo.

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
* \`src/\`: Lógica principal y módulos de extracción.
* \`data/referencias/\`: Archivos CSV con parámetros técnicos.
* \`.devcontainer/\`: Configuración para entorno de desarrollo estandarizado.

## 🚀 Guía de Instalación

### Opción A: Uso de DevContainer (Recomendado)
Si usas VS Code, el proyecto detectará automáticamente la carpeta **.devcontainer**. Haz clic en "Reopen in Container" para tener todo el entorno listo sin instalar nada manualmente.

### Opción B: Instalación Local
1. Instalar dependencias: \`pip install -r requirements.txt\`
2. Ejecutar: \`streamlit run app.py\`
