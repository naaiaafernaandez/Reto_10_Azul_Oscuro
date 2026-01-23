# Reto 10 Azul Oscuro: Lookiero Dashboard & Recommendation System

## Descripción del Proyecto

Este proyecto es una solución integral que combina análisis de datos y desarrollo web para sistemas de recomendación de moda.

**Parte de Análisis y Modelado:**
Se centra en el análisis de datos para "looks" y "likes" de prendas. Utiliza técnicas de procesamiento de datos, análisis de experiencia de usuario (UX), construcción de grafos y modelos de redes neuronales gráficas (GNN) como GCN, SAGE y GAT para predecir preferencias y generar recomendaciones de productos nuevos.

**Parte de Aplicación Web (Big Data):**
Incluye una aplicación web full-stack ubicada en la carpeta `Web/` que utiliza **Inteligencia Artificial** para generar recomendaciones personalizadas en tiempo real. Combina un backend basado en eventos con **Apache Kafka** y un frontend interactivo de visualización de datos.

---

## Estructura del Proyecto

### Notebooks (Análisis y Modelado)

- **1_Procesamiento.ipynb**: Archivo input: (product_2.csv, product_variant.csv, color.csv, size.csv, brand.csv, product_feature_value.csv, feature_value.csv, feature_value_family.csv, feature.csv)
  - Notebook para el procesamiento y limpieza inicial de los datos. Incluye la unificación de datasets, manejo de valores faltantes y preparación de datos para análisis posteriores.

- **2.Analisis_UX.ipynb**: Archivo input: (Datos/Originales/Datos UX/page_views_2.csv)
  - Análisis de la experiencia de usuario basado en vistas de página y datos de interacción. Explora patrones de comportamiento de los usuarios.

- **3.Grafo.ipynb**: Archivo input: ("Datos\Transformados\df_unificado_colores.csv")
  - Construcción del grafo de prendas. Crea representaciones gráficas de las relaciones entre productos, colores y características.

- **4.Analisis_grafos.ipynb**: Archivo input: ("grafo_prendas.gexf")
  - Realización del análisis de los grafos mediante algoritmos.

- **5.generación_looks.ipynb**: Archivo input: ("grafo_prendas.gexf")
  - Se realiza la generación de los looks.

- **6.GCN_SAGE_GAT.ipynb**: Archivo input: (Si se ejecuta la celda se obtiene el grafo "grafo_prendas.gexf")
  - Implementación y entrenamiento de modelos de GNN (GCN, SAGE, GAT) para predicción de preferencias y recomendaciones.

- **7.GCN_SAGE_GAT_Variables_usadas.ipynb**: Archivo input: (Si se ejecuta la celda se obtiene el grafo "grafo_prendas.gexf")
  - Análisis de las variables utilizadas en los modelos GNN, incluyendo importancia de características y evaluación de rendimiento.

- **8.Producto_nuevo.ipynb**: Archivo input: (Si se ejecuta la celda se obtiene el grafo "grafo_prendas.gexf")
  - Desarrollo de recomendaciones para productos nuevos basados en los modelos entrenados y datos históricos.

- **9.Look&Like.ipynb**: Archivo input: ("Datos/Originales/Datos look&like/customers_data_2.csv", "Datos/Originales/Datos look&like/items_data.csv", "Datos/Originales/Datos look&like/look_and_like_data_2.csv")
  - Análisis específico de "look and like" data, incluyendo similitudes entre prendas y preferencias de usuarios.

### Scripts de Python (Raíz)

- **funciones.py**: Funciones auxiliares reutilizables para procesamiento de datos, cálculos de similitud y utilidades generales.
- **reglas.py**: Definición de reglas de negocio para la lógica de recomendaciones y validaciones.

### Datos y Modelos (Raíz)

- **looks.csv**: Dataset principal de looks, incluyendo información de prendas y preferencias.
- **grafo_prendas.gexf**: Archivo de grafo en formato GEXF para visualización y análisis de relaciones entre prendas.
- **Carpeta Datos/**:
  - **Originales/**: Datos crudos sin procesar (Datos look&like, Datos looks, Datos UX).
  - **Transformados/**: Datos procesados y limpios listos para modelado (df_grafo.csv, df_limpio.csv, etc.).
- **Carpeta Modelos/**: Archivos de modelos entrenados en formato PyTorch (.pth) (modelo_gnn_final.pth, modelo_sage_final.pth, etc.).

---

### Aplicación Web / Big Data (Carpeta `Web/`)

Esta carpeta contiene la aplicación web full-stack con Kafka y Flask.

**Raíz**
* **`producer.py`**: Servidor Flask. Se encarga de renderizar la interfaz y actúa como **Productor de Kafka**, enviando las solicitudes de los usuarios al *consumer*.
* **`consumer.py`**: El "cerebro" del sistema. Escucha los mensajes de Kafka, carga el modelo GCN, busca la prenda gemela en el grafo y genera 2 recomendaciones compatibles.
* **`grafo_prendas.gexf`**: Grafo con un total de 7555 nodos (versión para web).
* **`modelo_gnn_1000.pth`**: Pesos entrenados de la GCN utilizada para calcular embeddings y similitudes entre prendas.

**Templates**
* **`index.html`**: Página de aterrizaje (Home) con navegación a las distintas herramientas.
* **`bigdata.html`**: Interfaz del **Generador AI**. Aquí el usuario selecciona los parámetros de su prenda (talla, color, estilo) para pedir un look.
* **`resultado.html`**: Pantalla de carga y visualización final. Muestra la prenda del usuario junto con las 2 recomendaciones generadas por la IA.
* **`charts.html`**: Dashboard de análisis de datos. Visualiza métricas de inventario y comportamiento de usuario usando **D3.js**.
* **`reglas.html`**: Documentación visual de las reglas de combinación.
* **`wheel2.html`**: Herramienta interactiva de rueda de colores y armonía cromática.
* **`ejemplos.html`**: Página con 8 imágenes de looks generadas con IA.

**Static**
* **`styles.css`**: Hoja de estilos.
* **`graficos_ux.js`**: Lógica en JavaScript (D3.js) encargada de leer los CSV y renderizar los gráficos en `charts.html`.
* **`colorwheel.js`**: Archivo de JavaScript que procesa la rueda de colores.
* **`resultado_ia.json`**: Archivo temporal generado por el `consumer.py` que sirve de puente para entregar los datos al frontend.
* Archivos de datos para la web: `backtrack_stats.csv`, `time_stats.csv`, `df_limpio.csv`, `look_like_short.csv`.

## Para Ejecutar
### Pasos
1.  **Iniciar Kafka:** 
2.  **Arrancar producer.py:**
    Abre `http://127.0.0.1:5000` en tu navegador.
3.  **Arrancar el consumer.py:**
    Esperar al mensaje *ESPERANDO A QUE EL USUARIO ELIJA UNA PRENDA...*
4.  **Empezar a navegar por la Web**
---

## Requisitos

- Python 3.8+
- Apache Kafka (necesario para la ejecución de la Web App)
- Bibliotecas listadas en `requirements.txt`
- Jupyter Notebook para ejecutar los notebooks de análisis

## Instalación

1. Clona el repositorio.
2. Instala las dependencias:
   ```bash
   pip install -r requirements.txt
