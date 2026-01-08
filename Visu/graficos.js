import pandas as pd

# 1. Leer tus datos (simulamos que leemos 'datos.csv')
# df = pd.read_csv('turs_datos.csv')
data = {
    'categoria': ['A', 'B', 'C', 'D', 'E'],
    'valor': [10, 25, 15, 30, 20]
}
df = pd.DataFrame(data)

# 2. Convertir a JSON String (formato lista de objetos)
datos_json = df.to_json(orient='records')

# 3. Definir el contenido del archivo .js
# Usamos una f-string para insertar los datos directamente en la variable 'dataset'
js_content = f"""
// Data inyectada desde Python
const dataset = {datos_json};

// Configuración del gráfico
const width = 500;
const height = 300;
const margin = {{top: 20, right: 30, bottom: 40, left: 40}};

// Seleccionar el contenedor (asegúrate de tener un div con id="grafico" en tu HTML)
const svg = d3.select("#grafico")
  .append("svg")
  .attr("width", width)
  .attr("height", height)
  .style("background", "#f0f0f0");

// Escalas
const x = d3.scaleBand()
  .domain(dataset.map(d => d.categoria))
  .range([margin.left, width - margin.right])
  .padding(0.1);

const y = d3.scaleLinear()
  .domain([0, d3.max(dataset, d => d.valor)])
  .range([height - margin.bottom, margin.top]);

// Ejes
svg.append("g")
  .attr("transform", `translate(0,${{height - margin.bottom}})`)
  .call(d3.axisBottom(x));

svg.append("g")
  .attr("transform", `translate(${{margin.left}},0)`)
  .call(d3.axisLeft(y));

// Barras
svg.selectAll("rect")
  .data(dataset)
  .join("rect")
  .attr("x", d => x(d.categoria))
  .attr("y", d => y(d.valor))
  .attr("height", d => y(0) - y(d.valor))
  .attr("width", x.bandwidth())
  .attr("fill", "steelblue");
"""

# 4. Guardar como archivo .js
with open("mi_grafico.js", "w") as f:
    f.write(js_content)

print("Archivo 'mi_grafico.js' generado correctamente.")