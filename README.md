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
* **Comparativa Regional:** Facilita la identificación de zonas óptimas para la actividad agrícola y ganadera.

## 🛠️ Diseño y Planeamiento de la Extracción
Para cumplir con los requisitos de la evaluación, el sistema integra tres fuentes de información:
1. **API de OpenWeather:** Datos climáticos en tiempo real (temperatura y humedad).
2. **API de Geopy:** Localización geográfica y conversión de nombres a coordenadas.
3. **Archivos Estructurados (.CSV):** Bases de datos con parámetros técnicos de crianza para diferentes especies.

## 📊 Estructuración y Combinación de Datos
El sistema cruza la información climática obtenida por las APIs con los límites técnicos definidos en los archivos CSV locales. Mediante lógica en Python, se determina si una zona es apta y se envía esa información al mapa para su visualización interactiva.
