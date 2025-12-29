# Sistema de Apoyo a la Decisión Agropecuaria 🌾🚜

## 📋 Descripción del Proyecto
Este proyecto es un buscador temático diseñado para centralizar información climática y ambiental. Su objetivo es facilitar la toma de decisiones para productores mediante el análisis de datos en tiempo real y registros históricos.

## 👥 Integrantes
* **Escobar Champi, Claudia Maria** (GitHub: champibara)
* **Condori Cieza, Esther Elizabeth** (GitHub: Esther0907)

## 🎯 Objetivos
1. **Extraer** datos climáticos y agropecuarios de múltiples fuentes digitales.
2. **Procesar y organizar** la información para identificar zonas óptimas de crianza y cultivo.
3. **Visualizar** los resultados en un **Mapa Inteligente** interactivo.

## 🛠️ Diseño y Planeamiento de la Extracción
Para cumplir con los requisitos de la evaluación, el sistema integra tres fuentes:
1. **API de OpenWeather:** Datos climáticos en tiempo real.
2. **API de Geopy:** Localización geográfica y coordenadas.
3. **Archivos Estructurados (.CSV):** Parámetros técnicos de crianza (bovinos, porcinos, aves).

## 📊 Estructuración y Combinación de Datos
El sistema cruza la temperatura obtenida por la API con los límites definidos en los archivos CSV. Si la zona es apta según los parámetros técnicos, el Mapa Inteligente la resalta como zona óptima.
