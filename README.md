# Proyecto: Sistema de Apoyo a la Decisión Agropecuaria 🌾🚜

## 👥 Integrantes
* **Escobar Champi, Claudia Maria** (GitHub: champibara)
* **Condori Cieza, Esther Elizabeth** (GitHub: Esther0907)

## 📋 Descripción del Proyecto
Este proyecto surge ante la dificultad de acceder a información climática y ambiental, la cual se encuentra dispersa en diversas fuentes. Proponemos un buscador temático orientado a la ganadería y agricultura que utiliza técnicas de extracción de datos para facilitar la toma de decisiones.

## 🎯 Objetivos
* **Extraer** datos relativos al clima y ambiente de múltiples fuentes.
* **Procesar y organizar** los datos recolectados de manera eficiente.
* **Visualizar** la información mediante un mapa interactivo para identificar zonas óptimas.

## ✨ Característica Principal: Mapa Inteligente
El sistema cuenta con un "Mapa Inteligente" que ofrece:
* **Distribución Territorial:** Muestra la aptitud agropecuaria por regiones usando indicadores como temperatura, humedad y precipitación.
* **Análisis por Zona:** Al seleccionar un área, indica los tipos de ganado recomendados y sus condiciones de crianza.

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
* **Automatización de Resultados:** El resultado del procesamiento se traduce en colores y etiquetas (Apto/No Apto) que alimentan directamente la interfaz visual del mapa.
