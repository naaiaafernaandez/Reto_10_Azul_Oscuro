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


// ==========================================
//   SECCIÓN: LOOK & LIKE (Código D3.js)
// ==========================================

// 1. Evento para activar la carga cuando se pulsa el botón
const btnLookLike = document.querySelector('[data-target="section-looklike"]');
if (btnLookLike) {
    btnLookLike.addEventListener('click', () => {
        const container = document.getElementById("familyChart");
        // Solo cargamos si el contenedor está vacío (para no recargar cada vez)
        if (!container || container.innerHTML === "") {
            loadLookLikeCharts();
        }
    });
}

// 2. Función Principal de Carga
function loadLookLikeCharts() {
    // AJUSTA ESTA RUTA SI ES NECESARIO:
    const csvPath = "../Datos/Transformados/look_like_short.csv"; 

    d3.csv(csvPath).then(data => {
        
        // --- A) PREPROCESAMIENTO ---
        const parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S.%f"); // Formato: 2025-01-26 11:17:28.849743
        
        data.forEach(d => {
            d.date = parseDate(d.occurred_on_);
            d.date_day = d3.timeDay(d.date); // Redondear al día para agrupar
        });

        // 1. Datos Familias (Top 10)
        const familyRollup = d3.rollup(data, v => v.length, d => d.family);
        let familyData = Array.from(familyRollup, ([key, value]) => ({ family: key, count: value }));
        familyData.sort((a, b) => b.count - a.count);
        familyData = familyData.slice(0, 10); // Top 10

        // 2. Datos Mercado (Donut)
        const marketRollup = d3.rollup(data, v => v.length, d => d.user_market);
        const marketData = Array.from(marketRollup, ([key, value]) => ({ market: key, count: value }));

        // 3. Datos Temporales (Línea de tiempo diaria)
        const timeRollup = d3.rollup(data, v => v.length, d => d.date_day);
        let timeData = Array.from(timeRollup, ([key, value]) => ({ date: key, count: value }));
        timeData.sort((a, b) => a.date - b.date); // Ordenar cronológicamente

        // --- B) INYECCIÓN HTML ---
        const sectionContainer = document.getElementById("section-looklike");
        sectionContainer.innerHTML = `
            <h2 class="mb-4 text-center fw-bold text-dark">Look & Like (Q1 2025)</h2>
            <p class="text-center text-muted mb-4">Análisis de interacciones del primer trimestre.</p>
            
            <div class="row g-4 mb-4">
                <div class="col-12 col-lg-8">
                    <div class="chart-container p-4">
                        <h5 class="fw-bold mb-3">👕 Top 10 Familias de Prendas</h5>
                        <div id="familyChart"></div>
                    </div>
                </div>
                <div class="col-12 col-lg-4">
                    <div class="chart-container p-4">
                        <h5 class="fw-bold mb-3">🌍 Mercados</h5>
                        <div id="marketChart"></div>
                    </div>
                </div>
            </div>

            <div class="row g-4">
                <div class="col-12">
                    <div class="chart-container p-4">
                        <h5 class="fw-bold mb-3">📈 Evolución Diaria de Interacciones</h5>
                        <div id="timelineChart"></div>
                    </div>
                </div>
            </div>
        `;

        // --- C) DIBUJAR GRÁFICOS ---
        drawFamilyChart(familyData);
        drawMarketChart(marketData);
        drawTimelineChart(timeData);

    }).catch(err => {
        console.error("Error cargando CSV LookLike:", err);
        document.getElementById("section-looklike").innerHTML = `
            <div class="alert alert-danger m-5 text-center">
                No se pudo cargar el archivo <code>${csvPath}</code>.<br>
                Revisa la consola (F12) para más detalles.
            </div>`;
    });
}

// ------------------------------------------------
//  FUNCIONES DE DIBUJO INDIVIDUALES
// ------------------------------------------------

function drawFamilyChart(data) {
    const containerId = "familyChart";
    const width = getWidth(containerId);
    const localMargin = { top: 20, right: 30, bottom: 40, left: 120 }; // Margen izq amplio para nombres largos
    
    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width + localMargin.left + localMargin.right)
        .attr("height", 300 + localMargin.top + localMargin.bottom)
        .append("g")
        .attr("transform", `translate(${localMargin.left},${localMargin.top})`);

    const x = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count)])
        .range([0, width]);

    const y = d3.scaleBand()
        .range([0, 300])
        .domain(data.map(d => d.family))
        .padding(0.2);

    svg.append("g")
        .attr("transform", `translate(0,300)`)
        .call(d3.axisBottom(x).ticks(5).tickFormat(d3.format(".2s")));

    svg.append("g")
        .call(d3.axisLeft(y))
        .selectAll("text")
        .style("font-size", "12px")
        .style("font-weight", "500");

    svg.selectAll("rect")
        .data(data)
        .join("rect")
        .attr("x", x(0))
        .attr("y", d => y(d.family))
        .attr("width", d => x(d.count))
        .attr("height", y.bandwidth())
        .attr("fill", "#6F1E51")
        .attr("rx", 3)
        .on("mouseover", (event, d) => {
            tooltip.style("opacity", 1)
                .html(`<strong>${d.family}</strong><br>${d.count} valoraciones`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
            d3.select(event.currentTarget).attr("fill", "#B53471");
        })
        .on("mouseout", (e) => {
            tooltip.style("opacity", 0);
            d3.select(e.currentTarget).attr("fill", "#6F1E51");
        });
}

function drawMarketChart(data) {
    const containerId = "marketChart";
    const containerWidth = getWidth(containerId);
    const height = 300;
    const radius = Math.min(containerWidth, height) / 2;

    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", containerWidth)
        .attr("height", height)
        .append("g")
        .attr("transform", `translate(${containerWidth / 2},${height / 2})`);

    const color = d3.scaleOrdinal()
        .domain(data.map(d => d.market))
        .range(["#0057B8", "#C0392B", "#F1C40F", "#27AE60", "#8e44ad"]);

    const pie = d3.pie().value(d => d.count).sort(null);
    const arc = d3.arc().innerRadius(radius * 0.55).outerRadius(radius * 0.85);
    const arcHover = d3.arc().innerRadius(radius * 0.55).outerRadius(radius * 0.95);

    svg.selectAll('path')
        .data(pie(data))
        .join('path')
        .attr('d', arc)
        .attr('fill', d => color(d.data.market))
        .attr("stroke", "white")
        .style("stroke-width", "2px")
        .on("mouseover", function(event, d) {
            d3.select(this).transition().duration(200).attr("d", arcHover);
            tooltip.style("opacity", 1)
                .html(`<strong>${d.data.market}</strong><br>${d.data.count} usuarios`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).transition().duration(200).attr("d", arc);
            tooltip.style("opacity", 0);
        });

    // Texto Central
    const total = d3.sum(data, d => d.count);
    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "-0.2em")
        .style("font-size", "24px")
        .style("font-weight", "bold")
        .text(d3.format(".2s")(total));
    svg.append("text")
        .attr("text-anchor", "middle")
        .attr("dy", "1.2em")
        .style("font-size", "12px")
        .style("fill", "#666")
        .text("TOTAL");
}

function drawTimelineChart(data) {
    const containerId = "timelineChart";
    const width = getWidth(containerId);
    const height = 250;
    const margin = { top: 20, right: 30, bottom: 30, left: 50 };

    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // Ejes
    const x = d3.scaleTime()
        .domain(d3.extent(data, d => d.date))
        .range([0, width]);
        
    const y = d3.scaleLinear()
        .domain([0, d3.max(data, d => d.count)])
        .range([height, 0]);

    svg.append("g")
        .attr("transform", `translate(0,${height})`)
        .call(d3.axisBottom(x).ticks(5));

    svg.append("g")
        .call(d3.axisLeft(y));

    // Línea
    const line = d3.line()
        .x(d => x(d.date))
        .y(d => y(d.count))
        .curve(d3.curveMonotoneX); // Suavizar la línea

    // Gradiente para el área bajo la curva (efecto visual moderno)
    const area = d3.area()
        .x(d => x(d.date))
        .y0(height)
        .y1(d => y(d.count))
        .curve(d3.curveMonotoneX);

    svg.append("path")
        .datum(data)
        .attr("fill", "#dbeafe") // Azul muy claro
        .attr("d", area);

    svg.append("path")
        .datum(data)
        .attr("fill", "none")
        .attr("stroke", "#3b82f6") // Azul principal
        .attr("stroke-width", 2)
        .attr("d", line);

    // Puntos interactivos (solo si no son demasiados, aquí son ~90 días, ok)
    svg.selectAll(".dot")
        .data(data)
        .enter()
        .append("circle")
        .attr("cx", d => x(d.date))
        .attr("cy", d => y(d.count))
        .attr("r", 3)
        .attr("fill", "#2563eb")
        .attr("opacity", 0) // Ocultos por defecto, aparecen al hover
        .on("mouseover", function(event, d) {
            d3.select(this).attr("opacity", 1).attr("r", 5);
            const fechaStr = d.date.toLocaleDateString('es-ES', { day: 'numeric', month: 'short' });
            tooltip.style("opacity", 1)
                .html(`<strong>${fechaStr}</strong><br>${d.count} eventos`)
                .style("left", (event.pageX + 10) + "px")
                .style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).attr("opacity", 0).attr("r", 3);
            tooltip.style("opacity", 0);
        });
}