// ==========================================
//    CONFIGURACIÓN GLOBAL
// ==========================================
const margin = { top: 20, right: 30, bottom: 50, left: 60 };
const height = 400 - margin.top - margin.bottom;
const tooltip = d3.select("#tooltip");

// ==========================================
//    LÓGICA DE PESTAÑAS Y NAVEGACIÓN
// ==========================================
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
            
            // Forzar redimensionado para que D3 calcule bien los anchos
            window.dispatchEvent(new Event('resize'));
        });
    });

    // Cargar gráficos iniciales (Onboarding)
    loadOnboardingCharts();
});

// Función auxiliar para obtener ancho dinámico
function getWidth(containerId) {
    const container = document.getElementById(containerId);
    return container && container.clientWidth > 0 ? container.clientWidth - margin.left - margin.right : 500;
}

// ==========================================
//    SECCIÓN 1: ONBOARDING (UX)
// ==========================================

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
            if(!document.getElementById("section-onboarding").classList.contains("d-none-custom")){
                d3.select("#timeChart").html("");
                d3.select("#backtrackChart").html("");
                drawTimeChart(timeData);
                drawBacktrackChart(backtrackData);
            }
        });

    }).catch(err => console.error("Error cargando CSVs Onboarding:", err));
}

function drawTimeChart(data) {
    const containerId = "timeChart";
    const width = getWidth(containerId);
    
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
//    SECCIÓN 2: LOOK & LIKE
// ==========================================

const btnLookLike = document.querySelector('[data-target="section-looklike"]');
if (btnLookLike) {
    btnLookLike.addEventListener('click', () => {
        const container = document.getElementById("familyChart");
        if (!container || container.innerHTML === "") {
            loadLookLikeCharts();
        }
    });
}

function loadLookLikeCharts() {
    const csvPath = "../Datos/Transformados/look_like_short.csv"; 

    d3.csv(csvPath).then(data => {
        const parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S.%f");
        
        data.forEach(d => {
            d.date = parseDate(d.occurred_on_);
            d.date_day = d3.timeDay(d.date); 
        });

        // Agrupaciones
        const familyRollup = d3.rollup(data, v => v.length, d => d.family);
        let familyData = Array.from(familyRollup, ([key, value]) => ({ family: key, count: value }));
        familyData.sort((a, b) => b.count - a.count);
        familyData = familyData.slice(0, 10); 

        const marketRollup = d3.rollup(data, v => v.length, d => d.user_market);
        const marketData = Array.from(marketRollup, ([key, value]) => ({ market: key, count: value }));

        const timeRollup = d3.rollup(data, v => v.length, d => d.date_day);
        let timeData = Array.from(timeRollup, ([key, value]) => ({ date: key, count: value }));
        timeData.sort((a, b) => a.date - b.date);

        // Inyección HTML Look & Like
        document.getElementById("section-looklike").innerHTML = `
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

        drawFamilyChart(familyData);
        drawMarketChart(marketData);
        drawTimelineChart(timeData);

    }).catch(err => {
        console.error("Error cargando CSV LookLike:", err);
        document.getElementById("section-looklike").innerHTML = `
            <div class="alert alert-danger m-5 text-center">
                No se pudo cargar el archivo <code>${csvPath}</code>.
            </div>`;
    });
}

function drawFamilyChart(data) {
    const containerId = "familyChart";
    const width = getWidth(containerId);
    const localMargin = { top: 20, right: 30, bottom: 40, left: 120 };
    
    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`)
        .append("svg")
        .attr("width", width + localMargin.left + localMargin.right)
        .attr("height", 300 + localMargin.top + localMargin.bottom)
        .append("g")
        .attr("transform", `translate(${localMargin.left},${localMargin.top})`);

    const x = d3.scaleLinear().domain([0, d3.max(data, d => d.count)]).range([0, width]);
    const y = d3.scaleBand().range([0, 300]).domain(data.map(d => d.family)).padding(0.2);

    svg.append("g").attr("transform", `translate(0,300)`).call(d3.axisBottom(x).ticks(5).tickFormat(d3.format(".2s")));
    svg.append("g").call(d3.axisLeft(y));

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

    const svg = d3.select(`#${containerId}`).append("svg")
        .attr("width", containerWidth).attr("height", height)
        .append("g").attr("transform", `translate(${containerWidth / 2},${height / 2})`);

    const color = d3.scaleOrdinal().range(["#0057B8", "#C0392B", "#F1C40F", "#27AE60", "#8e44ad"]);
    const pie = d3.pie().value(d => d.count).sort(null);
    const arc = d3.arc().innerRadius(radius * 0.55).outerRadius(radius * 0.85);

    svg.selectAll('path')
        .data(pie(data))
        .join('path')
        .attr('d', arc)
        .attr('fill', d => color(d.data.market))
        .attr("stroke", "white")
        .style("stroke-width", "2px");

    // Texto Central
    const total = d3.sum(data, d => d.count);
    svg.append("text").attr("text-anchor", "middle").attr("dy", "-0.2em").style("font-size", "24px").style("font-weight", "bold").text(d3.format(".2s")(total));
    svg.append("text").attr("text-anchor", "middle").attr("dy", "1.2em").style("font-size", "12px").style("fill", "#666").text("TOTAL");
}

function drawTimelineChart(data) {
    const containerId = "timelineChart";
    const width = getWidth(containerId);
    const height = 250;
    const margin = { top: 20, right: 30, bottom: 30, left: 50 };

    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`)
        .append("svg").attr("width", width + margin.left + margin.right).attr("height", height + margin.top + margin.bottom)
        .append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleTime().domain(d3.extent(data, d => d.date)).range([0, width]);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.count)]).range([height, 0]);

    svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(x).ticks(5));
    svg.append("g").call(d3.axisLeft(y));

    const area = d3.area().x(d => x(d.date)).y0(height).y1(d => y(d.count)).curve(d3.curveMonotoneX);
    const line = d3.line().x(d => x(d.date)).y(d => y(d.count)).curve(d3.curveMonotoneX);

    svg.append("path").datum(data).attr("fill", "#dbeafe").attr("d", area);
    svg.append("path").datum(data).attr("fill", "none").attr("stroke", "#3b82f6").attr("stroke-width", 2).attr("d", line);
}


// ==========================================
//    SECCIÓN 3: PRENDAS (INVENTARIO)
// ==========================================

const btnPrendas = document.querySelector('[data-target="section-prendas"]');
if (btnPrendas) {
    btnPrendas.addEventListener('click', () => {
        const container = document.getElementById("scatterChart");
        if (container) container.innerHTML = ""; 
        loadPrendasCharts();
    });
}

function loadPrendasCharts() {
    const csvPath = "../Datos/Transformados/df_limpio.csv"; 

    d3.csv(csvPath).then(data => {
        
        // --- 1. PROCESAMIENTO PARA SCATTER PLOT ---
        const scatterRollup = d3.rollup(data, 
            v => {
                return {
                    count: v.length,
                    avgLength: d3.mean(v, d => +d.long_cm1 || 0),
                    mainFit: d3.mode(v, d => d.fit1)
                };
            }, 
            d => d.tipo_prenda2, d => d.style1, d => d.nivel 
        );

        let scatterData = [];
        scatterRollup.forEach((stylesMap, type) => {
            stylesMap.forEach((levelsMap, style) => {
                levelsMap.forEach((stats, nivel) => {
                    if (stats.avgLength > 0 && stats.count > 5) {
                        scatterData.push({
                            type: type, style: style, nivel: nivel, 
                            length: stats.avgLength, count: stats.count, fit: stats.mainFit
                        });
                    }
                });
            });
        });

        // --- 2. DATOS COLORES (Top 12) ---
        const colorRollup = d3.rollup(data, v => v.length, d => d.Color);
        let colorData = Array.from(colorRollup, ([key, value]) => ({ color: key, count: value }));
        colorData.sort((a, b) => b.count - a.count);
        colorData = colorData.slice(0, 12); 

        // --- INYECCIÓN HTML ---
        const sectionContainer = document.getElementById("section-prendas");
        
        if(!document.getElementById("scatterChart")) {
            sectionContainer.innerHTML = `
                <h2 class="mb-4 text-center fw-bold text-dark">Inventario de Prendas</h2>
                <p class="text-center text-muted mb-4">Distribución por Nivel y Estilo.</p>
                
                <div class="row g-4 mb-4">
                    <div class="col-12">
                        <div class="chart-container p-4 shadow-sm border rounded bg-white">
                            <h5 class="fw-bold mb-3">✨ Mapa de Niveles (Scatter Plot)</h5>
                            
                            <p class="mb-3">
                                <span class="text-muted small">Cada punto es una combinación de <strong>Prenda + Estilo + Nivel</strong>.</span><br>
                                <span class="badge rounded-pill" style="background-color:#2ecc71; margin-right:5px;">Nivel 1</span>
                                <span class="badge rounded-pill text-dark" style="background-color:#f1c40f; margin-right:5px;">Nivel 2</span>
                                <span class="badge rounded-pill" style="background-color:#8e44ad;">Nivel 3</span>
                            </p>

                            <div id="scatterChart"></div>
                        </div>
                    </div>
                </div>

                <div class="row g-4">
                    <div class="col-12">
                        <div class="chart-container p-4 shadow-sm border rounded bg-white">
                            <h5 class="fw-bold mb-3">🎨 Colores Reales en Inventario</h5>
                            <div id="realColorChart"></div>
                        </div>
                    </div>
                </div>
            `;
        } else {
             const sc = document.getElementById("scatterChart");
             if(sc) sc.innerHTML = "";
             const rc = document.getElementById("realColorChart");
             if(rc) rc.innerHTML = "";
        }

        // --- DIBUJAR ---
        setTimeout(() => {
            drawScatterPlot(scatterData);
            drawRealColorChart(colorData);
        }, 150);

    }).catch(error => {
        console.error("Error crítico en Prendas:", error);
    });
}

// ------------------------------------------------------
//  FUNCIÓN SCATTER PLOT (Corregida y Recuperada)
// ------------------------------------------------------
function drawScatterPlot(data) {
    const container = document.getElementById("scatterChart");
    if (!container) return; 
    container.innerHTML = ""; 

    const width = container.getBoundingClientRect().width || 800; 
    const height = 500;
    const margin = { top: 40, right: 40, bottom: 60, left: 70 };
    const chartWidth = width - margin.left - margin.right;
    const chartHeight = height - margin.top - margin.bottom;

    const svg = d3.select(container).append("svg")
        .attr("width", width).attr("height", height)
        .append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().domain([0, d3.max(data, d => d.length) * 1.05]).range([0, chartWidth]);
    const y = d3.scaleLog().domain([3, d3.max(data, d => d.count) * 1.5]).range([chartHeight, 0]).nice();
    const color = d3.scaleOrdinal().domain(["1", "2", "3"]).range(["#2ecc71", "#f1c40f", "#8e44ad"]);

    // Ejes
    svg.append("g").attr("transform", `translate(0,${chartHeight})`).call(d3.axisBottom(x))
        .append("text").attr("x", chartWidth / 2).attr("y", 45).attr("fill", "#333").style("text-anchor", "middle").style("font-weight", "bold").text("Longitud Media (cm)");

    svg.append("g").call(d3.axisLeft(y).ticks(5, "~s"))
        .append("text").attr("transform", "rotate(-90)").attr("y", -55).attr("x", -(chartHeight / 2)).attr("dy", "1em").attr("fill", "#333").style("text-anchor", "middle").style("font-weight", "bold").text("Popularidad (Escala Log)");

    // Puntos
    svg.selectAll("circle")
        .data(data).join("circle")
        .attr("cx", d => x(d.length)).attr("cy", d => y(d.count)).attr("r", 6)
        .style("fill", d => color(d.nivel)).style("opacity", 0.7).attr("stroke", "white").attr("stroke-width", 1)
        .on("mouseover", (event, d) => {
            d3.select(event.currentTarget).attr("r", 9).style("opacity", 1).attr("stroke", "#333");
            tooltip.style("opacity", 1)
                .html(`<strong>${d.type}</strong><br>Estilo: ${d.style}<br><span style="color:${color(d.nivel)}">● Nivel ${d.nivel}</span><br>Longitud: ${d.length.toFixed(1)} cm<br>Items: ${d.count}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", (e) => {
            d3.select(e.currentTarget).attr("r", 6).style("opacity", 0.7).attr("stroke", "white");
            tooltip.style("opacity", 0);
        });

    // Leyenda
    const legend = svg.append("g").attr("transform", `translate(${chartWidth - 60}, 10)`);
    legend.append("rect").attr("x", -10).attr("y", -20).attr("width", 70).attr("height", 85).attr("fill", "white").style("opacity", 0.8).attr("rx", 5);
    legend.append("text").attr("x", 0).attr("y", -5).text("Nivel").style("font-size", "12px").style("font-weight", "bold");
    ["1", "2", "3"].forEach((nivel, i) => {
        const row = legend.append("g").attr("transform", `translate(0, ${i * 20 + 15})`);
        row.append("circle").attr("r", 6).attr("fill", color(nivel));
        row.append("text").attr("x", 15).attr("y", 4).text(nivel).style("font-size", "12px");
    });
}

// ------------------------------------------------------
//  FUNCIÓN BAR CHART COLORES
// ------------------------------------------------------
function drawRealColorChart(data) {
    const container = document.getElementById("realColorChart");
    if (!container) return;
    container.innerHTML = "";

    const width = container.getBoundingClientRect().width || 600;
    const height = 400;
    const margin = { top: 20, right: 20, bottom: 60, left: 50 };

    const svg = d3.select(container).append("svg")
        .attr("width", width).attr("height", height)
        .append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleBand().range([0, width - margin.left - margin.right]).domain(data.map(d => d.color)).padding(0.2);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.count)]).range([height - margin.top - margin.bottom, 0]);

    svg.append("g").attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(x)).selectAll("text").attr("transform", "translate(-10,0)rotate(-45)").style("text-anchor", "end");
    svg.append("g").call(d3.axisLeft(y));

    const getColorHex = (colorName) => {
        const map = {
            'black': '#2d3436', 'white': '#dfe6e9', 'navy': '#0c2461', 'blue': '#0984e3', 'blue_dark': '#0c2461',
            'blue_light': '#74b9ff', 'red': '#d63031', 'grey': '#b2bec3', 'green': '#00b894', 'green_dark': '#006266',
            'khaki': '#f0e68c', 'beige': '#f5f5dc', 'pink': '#fd79a8', 'purple': '#6c5ce7', 'yellow': '#ffeaa7',
            'orange': '#e17055', 'brown': '#8d6e63', 'ecru': '#C2B280'
        };
        return map[colorName.toLowerCase()] || colorName || '#636e72';
    };

    svg.selectAll("mybar").data(data).join("rect")
        .attr("x", d => x(d.color)).attr("y", d => y(d.count))
        .attr("width", x.bandwidth()).attr("height", d => height - margin.top - margin.bottom - y(d.count))
        .attr("fill", d => getColorHex(d.color)).attr("stroke", "#b2bec3").attr("rx", 4) 
        .on("mouseover", function(event, d) {
            d3.select(this).style("opacity", 0.7);
            tooltip.style("opacity", 1).html(`Color: <strong>${d.color}</strong><br>Items: ${d.count}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).style("opacity", 1);
            tooltip.style("opacity", 0);
        });
}