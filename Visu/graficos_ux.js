// --- CONFIGURACIÓN GLOBAL ---
const margin = { top: 20, right: 30, bottom: 50, left: 60 };
const height = 400 - margin.top - margin.bottom;
const tooltip = d3.select("#tooltip");

// --- LÓGICA DE PESTAÑAS (BOTONES) ---
document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".tab-btn");
    const sections = document.querySelectorAll(".view-section");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            // 1. Quitar clase 'active' de todos los botones
            buttons.forEach(b => b.classList.remove("active"));
            // 2. Añadir clase 'active' al botón clicado
            btn.classList.add("active");

            // 3. Ocultar todas las secciones
            sections.forEach(s => s.classList.add("d-none-custom"));

            // 4. Mostrar la sección correspondiente
            const targetId = btn.getAttribute("data-target");
            document.getElementById(targetId).classList.remove("d-none-custom");
            
            // Opcional: Redimensionar gráficos si D3 no calcula bien al estar ocultos
            window.dispatchEvent(new Event('resize'));
        });
    });

    // Iniciar la carga de gráficos de Onboarding
    loadOnboardingCharts();
});

// Función para obtener ancho dinámico
function getWidth(containerId) {
    const container = document.getElementById(containerId);
    // Si el contenedor está oculto (display: none), clientWidth es 0. 
    // Usamos un fallback o esperamos a que sea visible.
    return container.clientWidth > 0 ? container.clientWidth - margin.left - margin.right : 500;
}

// --- CARGA DE DATOS Y GRÁFICOS (ONBOARDING) ---
function loadOnboardingCharts() {
    Promise.all([
        d3.csv("../Datos/Transformados/time_stats.csv"),
        d3.csv("../Datos/Transformados/backtrack_stats.csv")
    ]).then(([timeData, backtrackData]) => {
        
        // Procesar datos Time
        timeData.forEach(d => {
            d.step_order = +d.step_order;
            d.median_time_to_next = +d.median_time_to_next;
        });
        timeData = timeData.filter(d => d.median_time_to_next > 0).sort((a, b) => a.step_order - b.step_order);

        // Procesar datos Backtrack
        backtrackData.forEach(d => d.n_backtracks = +d.n_backtracks);
        backtrackData.sort((a, b) => b.n_backtracks - a.n_backtracks);

        // Dibujar
        drawTimeChart(timeData);
        drawBacktrackChart(backtrackData);

        // Responsividad
        window.addEventListener("resize", () => {
            // Solo redibujar si la sección está visible para ahorrar recursos
            if(!document.getElementById("section-onboarding").classList.contains("d-none-custom")){
                d3.select("#timeChart").html("");
                d3.select("#backtrackChart").html("");
                drawTimeChart(timeData);
                drawBacktrackChart(backtrackData);
            }
        });

    }).catch(err => console.error("Error cargando CSVs:", err));
}

// --- FUNCIONES DE DIBUJO (Mismas que antes) ---

function drawTimeChart(data) {
    const containerId = "timeChart";
    const width = getWidth(containerId);
    
    // Limpiar antes de dibujar (útil para resize)
    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear()
        .domain(d3.extent(data, d => d.step_order))
        .range([0, width]);

    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.median_time_to_next)])
        .range([height, 0]);

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(data.length).tickFormat(d3.format("d")));

    svg.append("g").call(d3.axisLeft(y));

    const line = d3.line()
        .x(d => x(d.step_order))
        .y(d => y(d.median_time_to_next))
        .curve(d3.curveMonotoneX);

    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "#3b82f6")
        .attr("stroke-width", 3)
        .attr("d", line);

    svg.selectAll(".dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.step_order))
        .attr("cy", d => y(d.median_time_to_next))
        .attr("r", 5)
        .attr("fill", "#1d4ed8")
        .on("mouseover", (event, d) => {
            tooltip.style("opacity", 1)
                .html(`<strong>${d.section}</strong><br>Time: ${d.median_time_to_next.toFixed(1)}s`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", () => tooltip.style("opacity", 0));
        
    // Etiquetas ejes
    svg.append("text").attr("x", width).attr("y", height + 40).attr("text-anchor", "end").style("font-size", "12px").text("Paso");
    svg.append("text").attr("transform", "rotate(-90)").attr("y", -45).attr("x", -20).style("font-size", "12px").text("Segundos");
}

function drawBacktrackChart(data) {
    const containerId = "backtrackChart";
    const width = getWidth(containerId);
    // Ajuste local para etiquetas largas
    const localMarginLeft = 120; 
    const localWidth = width + margin.left - localMarginLeft;

    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${localMarginLeft},${margin.top})`);

    const x = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.n_backtracks)])
        .range([0, localWidth]);

    const y = d3.scaleBand()
        .range([0, height])
        .domain(data.map(d => d.section))
        .padding(0.2);

    svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(x).ticks(5));
    svg.append("g").call(d3.axisLeft(y));

    svg.selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", x(0))
        .attr("y", d => y(d.section))
        .attr("width", d => x(d.n_backtracks))
        .attr("height", y.bandwidth())
        .attr("fill", "#ef4444")
        .attr("opacity", 0.8)
        .on("mouseover", (event, d) => {
            tooltip.style("opacity", 1)
                .html(`<strong>${d.section}</strong><br>Backtracks: ${d.n_backtracks}`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", () => tooltip.style("opacity", 0));
}