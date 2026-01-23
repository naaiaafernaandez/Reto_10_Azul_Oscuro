# Reto_10_Azul_Oscuro

# Lookiero AI Dashboard & Recommendation System

Este proyecto es una aplicación web full-stack que utiliza **Inteligencia Artificial (Graph Neural Networks)** para generar recomendaciones de moda personalizadas (Looks completos). Combina un backend basado en eventos con **Apache Kafka** y un frontend interactivo de visualización de datos.

## Estructura del Proyecto

A continuación se detalla la función de los archivos principales del repositorio:

### Raíz
* **`producer.py`**: Servidor Flask. Se encarga de renderizar la interfaz y actúa como **Productor de Kafka**, enviando las solicitudes de los usuarios al ***consumer***.
* **`consumer.py`**: El "cerebro" del sistema. Escucha los mensajes de Kafka, carga el modelo GCN, busca la prenda gemela en el grafo y genera 2 recomendaciones compatibles.
* **`grafo_prendas.gexf`**: Grafo con un total de 7555 nodos
* **`modelo_gnn_1000.pth`**: Pesos entrenados de la  (GCN) utilizada para calcular embeddings y similitudes entre prendas.

### Templates
* **`index.html`**: Página de aterrizaje (Home) con navegación a las distintas herramientas.
* **`bigdata.html`**: Interfaz del **Generador AI**. Aquí el usuario selecciona los parámetros de su prenda (talla, color, estilo) para pedir un look.
* **`resultado.html`**: Pantalla de carga y visualización final. Muestra la prenda del usuario junto con las 2 recomendaciones generadas por la IA.
* **`charts.html`**: Dashboard de análisis de datos. Visualiza métricas de inventario y comportamiento de usuario usando **D3.js**.
* **`reglas.html`**: Documentación visual de las reglas de combinación.
* **`wheel2.html`**: Herramienta interactiva de rueda de colores y armonía cromática.
* **`ejemplos.html`**: Página con 8 imagenes de looks generadas con IA.

### Static
* **`styles.css`**: Hoja de estilos.
* **`graficos_ux.js`**: Lógica en JavaScript (D3.js) encargada de leer los CSV y renderizar los gráficos en `charts.html`.
* **`colorwheel.js`**: Archivo de JavaScript que procesa la rueda de colores.
* **`resultado_ia.json`**: Archivo temporal generado por el `consumer.py` que sirve de puente para entregar los datos al frontend.
* **`8 look.png`**: Fotos Generadas por IA de los looks.
* **`backtrack_stats.csv`**
* **`time_stats.csv`**
* **`df_limpio.csv`**
* **`look_like_short.csv`**
* 

## Para Ejecutar
### Pasos
1.  **Iniciar Kafka:** 
2.  **Arrancar producer.py:**
    Abre `http://127.0.0.1:5000` en tu navegador.
3.  **Arrancar el consumer.py:**
    Esperar al mensaje *ESPERANDO A QUE EL USUARIO ELIJA UNA PRENDA...*
4.  **Empezar a navegar por la Web**
