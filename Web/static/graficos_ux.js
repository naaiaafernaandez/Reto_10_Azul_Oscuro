// ==========================================
//    CONFIGURACIÓN GLOBAL Y PALETA
// ==========================================
const margin = { top: 30, right: 30, bottom: 60, left: 60 };
const height = 400 - margin.top - margin.bottom;
const tooltip = d3.select("#tooltip");

// PALETA TIERRA & CORAL
const PALETA = {
    primary:   "#c1634f", // Rust
    secondary: "#a67665", // Marrón medio
    accent:    "#f29b88", // Peach
    dark:      "#593831", // Marrón oscuro
    highlight: "#c75551", // Coral
    empty:     "#f3f4f6"  // Gris muy claro para valores 0
};

// ==========================================
//    LÓGICA DE PESTAÑAS Y NAVEGACIÓN
// ==========================================
document.addEventListener("DOMContentLoaded", () => {
    const buttons = document.querySelectorAll(".tab-btn");
    const sections = document.querySelectorAll(".view-section");

    buttons.forEach(btn => {
        btn.addEventListener("click", () => {
            buttons.forEach(b => b.classList.remove("active"));
            btn.classList.add("active");

            sections.forEach(s => s.classList.add("d-none-custom"));

            const targetId = btn.getAttribute("data-target");
            const targetSection = document.getElementById(targetId);
            if(targetSection) {
                targetSection.classList.remove("d-none-custom");
            }
            
            window.dispatchEvent(new Event('resize'));
        });
    });

    loadOnboardingCharts();
});

function getWidth(containerId) {
    const container = document.getElementById(containerId);
    return container && container.clientWidth > 0 ? container.clientWidth - margin.left - margin.right : 500;
}

// ==========================================
//    SECCIÓN 1: ONBOARDING (UX)
// ==========================================

function loadOnboardingCharts() {
    Promise.all([
        d3.csv("/static/time_stats.csv"),
        d3.csv("/static/backtrack_stats.csv")
    ]).then(([timeData, backtrackData]) => {
        
        const formatName = (name) => {
            if (!name) return "";
            let clean = name.replace("quiz_", "");
            return clean.charAt(0).toUpperCase() + clean.slice(1);
        };

        // Procesar Time Data
        timeData.forEach(d => {
            d.step_order = +d.step_order;
            d.median_time_to_next = +d.median_time_to_next;
            d.section = formatName(d.section);
        });
        timeData = timeData.filter(d => d.median_time_to_next > 0).sort((a, b) => a.step_order - b.step_order);

        // Procesar Backtrack Data
        backtrackData.forEach(d => {
            d.n_backtracks = +d.n_backtracks;
            d.section = formatName(d.section);
        });
        backtrackData.sort((a, b) => b.n_backtracks - a.n_backtracks);

        drawTimeChart(timeData);
        drawBacktrackChart(backtrackData);

        window.addEventListener("resize", () => {
            const section = document.getElementById("section-onboarding");
            if(section && !section.classList.contains("d-none-custom")){
                drawTimeChart(timeData);
                drawBacktrackChart(backtrackData);
            }
        });

    }).catch(err => console.error("Error CSV Onboarding:", err));
}

function drawTimeChart(data) {
    const containerId = "timeChart";
    const container = document.getElementById(containerId);
    if (!container) return;

    const width = getWidth(containerId);
    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const x = d3.scaleLinear().domain(d3.extent(data, d => d.step_order)).range([0, width]);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.median_time_to_next)]).range([height, 0]);

    svg.append("g").attr("transform", `translate(0,${height})`)
       .call(d3.axisBottom(x).ticks(data.length).tickFormat(d3.format("d")))
       .selectAll("text").style("fill", PALETA.dark);

    svg.append("g").call(d3.axisLeft(y))
       .selectAll("text").style("fill", PALETA.dark);

    const line = d3.line()
        .x(d => x(d.step_order))
        .y(d => y(d.median_time_to_next))
        .curve(d3.curveMonotoneX);

    svg.append("path").datum(data)
        .attr("fill", "none")
        .attr("stroke", PALETA.primary)
        .attr("stroke-width", 3)
        .attr("d", line);

    svg.selectAll(".dot").data(data).enter().append("circle")
        .attr("cx", d => x(d.step_order))
        .attr("cy", d => y(d.median_time_to_next))
        .attr("r", 5)
        .attr("fill", PALETA.secondary)
        .on("mouseover", (event, d) => {
            d3.select(event.currentTarget).attr("r", 8).attr("fill", PALETA.highlight);
            tooltip.style("opacity", 1)
                .html(`<strong>${d.section}</strong><br>Time: ${d.median_time_to_next.toFixed(1)}s`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", (e) => {
            d3.select(e.currentTarget).attr("r", 5).attr("fill", PALETA.secondary);
            tooltip.style("opacity", 0);
        });
        
    svg.append("text").attr("x", width/2).attr("y", height + 40).attr("fill", PALETA.dark).style("text-anchor", "middle").text("Paso del Flow");
    svg.append("text").attr("transform", "rotate(-90)").attr("y", -45).attr("x", -height/2).attr("fill", PALETA.dark).style("text-anchor", "middle").text("Tiempo (s)");
}

function drawBacktrackChart(data) {
    const containerId = "backtrackChart";
    const width = getWidth(containerId);
    const localLeft = 120; 
    const localWidth = width + margin.left - localLeft;

    d3.select(`#${containerId}`).html("");

    const svg = d3.select(`#${containerId}`).append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g").attr("transform", `translate(${localLeft},${margin.top})`);

    const x = d3.scaleLinear().domain([0, d3.max(data, d => d.n_backtracks)]).range([0, localWidth]);
    const y = d3.scaleBand().range([0, height]).domain(data.map(d => d.section)).padding(0.2);

    svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(x).ticks(5));
    svg.append("g").call(d3.axisLeft(y)).selectAll("text").style("fill", PALETA.dark).style("font-size", "11px");

    svg.selectAll("rect").data(data).join("rect")
        .attr("x", x(0))
        .attr("y", d => y(d.section))
        .attr("width", d => x(d.n_backtracks))
        .attr("height", y.bandwidth())
        .attr("fill", PALETA.highlight)
        .attr("opacity", 0.9)
        .on("mouseover", (event, d) => {
            d3.select(event.currentTarget).attr("opacity", 1);
            tooltip.style("opacity", 1)
                .html(`<strong>${d.section}</strong><br>Backtracks: ${d.n_backtracks}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", (e) => {
            d3.select(e.currentTarget).attr("opacity", 0.9);
            tooltip.style("opacity", 0);
        });
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
    d3.csv("/static/look_like_short.csv").then(data => {
        const parseDate = d3.timeParse("%Y-%m-%d %H:%M:%S.%f");
        data.forEach(d => {
            d.date = parseDate(d.occurred_on_);
            d.date_day = d3.timeDay(d.date); 
        });

        const familyRollup = d3.rollup(data, v => v.length, d => d.family);
        let familyData = Array.from(familyRollup, ([key, value]) => ({ family: key, count: value }));
        familyData.sort((a, b) => b.count - a.count).slice(0, 10); 

        const marketRollup = d3.rollup(data, v => v.length, d => d.user_market);
        const marketData = Array.from(marketRollup, ([key, value]) => ({ market: key, count: value }));

        const timeRollup = d3.rollup(data, v => v.length, d => d.date_day);
        let timeData = Array.from(timeRollup, ([key, value]) => ({ date: key, count: value }));
        timeData.sort((a, b) => a.date - b.date);

        const sectionContainer = document.getElementById("section-looklike");
        if(sectionContainer && sectionContainer.innerHTML.includes("Esperando")) {
            sectionContainer.innerHTML = `
                <h2 class="mb-2 text-center fw-bold" style="color:${PALETA.dark}">Look & Like</h2>
                <p class="text-center mb-4" style="color:${PALETA.secondary}">Análisis de interacciones.</p>
                <div class="row g-4 mb-4">
                    <div class="col-12 col-lg-8">
                        <div class="chart-container p-4">
                            <h5 class="fw-bold mb-3" style="color:${PALETA.primary}">Top Prendas por Categoría</h5>
                            <div id="familyChart"></div>
                        </div>
                    </div>
                    <div class="col-12 col-lg-4">
                        <div class="chart-container p-4">
                            <h5 class="fw-bold mb-3" style="color:${PALETA.primary}">Interacciones por País</h5>
                            <div id="marketChart"></div>
                        </div>
                    </div>
                </div>
                <div class="row g-4">
                    <div class="col-12">
                        <div class="chart-container p-4">
                            <h5 class="fw-bold mb-3" style="color:${PALETA.primary}">Evolución Temporal</h5>
                            <div id="timelineChart"></div>
                        </div>
                    </div>
                </div>
            `;
            drawFamilyChart(familyData);
            drawMarketChart(marketData);
            drawTimelineChart(timeData);
            window.addEventListener("resize", () => {
                if(!document.getElementById("section-looklike").classList.contains("d-none-custom")){
                    drawFamilyChart(familyData);
                    drawMarketChart(marketData);
                    drawTimelineChart(timeData);
                }
            });
        }
    });
}

function drawFamilyChart(data) {
    const containerId = "familyChart";
    const width = getWidth(containerId);
    const localMargin = { top: 20, right: 30, bottom: 40, left: 100 };
    
    d3.select(`#${containerId}`).html("");
    const svg = d3.select(`#${containerId}`).append("svg")
        .attr("width", width + localMargin.left + localMargin.right)
        .attr("height", 300 + localMargin.top + localMargin.bottom)
        .append("g").attr("transform", `translate(${localMargin.left},${localMargin.top})`);

    // === FUNCIÓN DE FORMATO DE ETIQUETAS ===
    const formatFamily = (name) => {
        if(!name) return "";
        const lower = name.toLowerCase();
        const map = {
            'blusa_camisa': 'Camisa/Blusa',
            'camisa': 'Camisa',
            'camiseta': 'Camiseta',
            'pantalones': 'Pantalón',
            'pantalon': 'Pantalón',
            'jeans': 'Jeans',
            'vestido': 'Vestido',
            'falda': 'Falda',
            'chaqueta': 'Chaqueta',
            'abrigo': 'Abrigo',
            'jersey': 'Jersey',
            'cardigan': 'Cárdigan',
            'top': 'Top',
            'mono': 'Mono',
            'mono_corto': 'Mono Corto',
            'bolso': 'Bolso',
            'bufanda': 'Bufanda',
            'calzado': 'Calzado',
            'accesorios': 'Accesorios'
        };
        // Si está en el mapa, úsalo. Si no, quita guiones y capitaliza.
        return map[lower] || lower.replace(/_/g, " ").replace(/\b\w/g, l => l.toUpperCase());
    };

    const x = d3.scaleLinear().domain([0, d3.max(data, d => d.count)]).range([0, width]);
    const y = d3.scaleBand().range([0, 300]).domain(data.map(d => d.family)).padding(0.2);

    svg.append("g").attr("transform", `translate(0,300)`).call(d3.axisBottom(x).ticks(5));
    
    // Aplicamos el formateador al eje Y
    svg.append("g").call(d3.axisLeft(y).tickFormat(formatFamily))
       .selectAll("text").style("fill", PALETA.dark).style("font-size", "12px");

    svg.selectAll("rect").data(data).join("rect")
        .attr("x", x(0)).attr("y", d => y(d.family)).attr("width", d => x(d.count)).attr("height", y.bandwidth())
        .attr("fill", PALETA.secondary).attr("rx", 3)
        .on("mouseover", (event, d) => {
            d3.select(event.currentTarget).attr("fill", PALETA.highlight);
            tooltip.style("opacity", 1).html(`<strong>${formatFamily(d.family)}</strong>: ${d.count}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", (e) => {
            d3.select(e.currentTarget).attr("fill", PALETA.secondary);
            tooltip.style("opacity", 0);
        });
}

function drawMarketChart(data) {
    const containerId = "marketChart";
    const container = document.getElementById(containerId);
    if (!container) return;
    const containerWidth = container.clientWidth;
    const height = 300;
    const radius = Math.min(containerWidth, height) / 2 - 10;
    d3.select(`#${containerId}`).html("");
    const svg = d3.select(`#${containerId}`).append("svg")
        .attr("width", containerWidth).attr("height", height)
        .append("g").attr("transform", `translate(${containerWidth / 2},${height / 2})`);
    const color = d3.scaleOrdinal().range([PALETA.primary, PALETA.secondary, PALETA.accent, PALETA.dark, "#dba598"]);
    const pie = d3.pie().value(d => d.count).sort(null);
    const arc = d3.arc().innerRadius(radius * 0.5).outerRadius(radius * 0.9);
    const arcHover = d3.arc().innerRadius(radius * 0.5).outerRadius(radius * 1);
    svg.selectAll('path').data(pie(data)).join('path')
        .attr('d', arc).attr('fill', d => color(d.data.market)).attr("stroke", "white").style("stroke-width", "2px")
        .on("mouseover", function(event, d) {
            d3.select(this).transition().duration(200).attr("d", arcHover);
            tooltip.style("opacity", 1).html(`<strong>${d.data.market}</strong><br>${d.data.count} usuarios`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).transition().duration(200).attr("d", arc);
            tooltip.style("opacity", 0);
        });
    const total = d3.sum(data, d => d.count);
    svg.append("text").attr("text-anchor", "middle").attr("dy", "-0.2em").style("font-size", "22px").style("font-weight", "bold").style("fill", PALETA.dark).text(d3.format(".2s")(total));
    svg.append("text").attr("text-anchor", "middle").attr("dy", "1.2em").style("font-size", "11px").style("fill", PALETA.secondary).text("TOTAL");
}

function drawTimelineChart(data) {
    const containerId = "timelineChart";
    const width = getWidth(containerId);
    const height = 250;
    const margin = { top: 20, right: 30, bottom: 30, left: 50 };
    d3.select(`#${containerId}`).html("");
    const svg = d3.select(`#${containerId}`).append("svg")
        .attr("width", width + margin.left + margin.right).attr("height", height + margin.top + margin.bottom)
        .append("g").attr("transform", `translate(${margin.left},${margin.top})`);
    const x = d3.scaleTime().domain(d3.extent(data, d => d.date)).range([0, width]);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.count)]).range([height, 0]);
    svg.append("g").attr("transform", `translate(0,${height})`).call(d3.axisBottom(x).ticks(5));
    svg.append("g").call(d3.axisLeft(y));
    const area = d3.area().x(d => x(d.date)).y0(height).y1(d => y(d.count)).curve(d3.curveMonotoneX);
    svg.append("path").datum(data).attr("fill", PALETA.accent).attr("opacity", 0.4).attr("d", area);
    const line = d3.line().x(d => x(d.date)).y(d => y(d.count)).curve(d3.curveMonotoneX);
    svg.append("path").datum(data).attr("fill", "none").attr("stroke", PALETA.primary).attr("stroke-width", 2).attr("d", line);
    svg.selectAll(".dot").data(data).enter().append("circle")
        .attr("cx", d => x(d.date)).attr("cy", d => y(d.count)).attr("r", 4)
        .attr("fill", PALETA.secondary).attr("stroke", "white").attr("stroke-width", 2).style("opacity", 0)
        .on("mouseover", function(event, d) {
            d3.select(this).transition().duration(100).attr("r", 7).style("opacity", 1).attr("fill", PALETA.highlight);
            tooltip.style("opacity", 1).html(`<strong>Fecha:</strong> ${d3.timeFormat("%d/%m/%Y")(d.date)}<br><strong>Interacciones:</strong> ${d.count}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).transition().duration(100).attr("r", 4).style("opacity", 0).attr("fill", PALETA.secondary);
            tooltip.style("opacity", 0);
        });
}

// ==========================================
//    SECCIÓN 3: PRENDAS (INVENTARIO)
// ==========================================

const btnPrendas = document.querySelector('[data-target="section-prendas"]');
if (btnPrendas) {
    btnPrendas.addEventListener('click', () => {
        const container = document.getElementById("section-prendas");
        loadPrendasCharts();
    });
}

function loadPrendasCharts() {
    d3.csv("/static/df_limpio.csv").then(data => {
        
        // --- 1. PREPARAR DATOS HEATMAP (RELLENO DE CEROS) ---
        const heatmapRollup = d3.rollup(data, v => v.length, d => d.tipo_prenda2, d => d.style1);
        
        const allTypes = Array.from(new Set(data.map(d => d.tipo_prenda2).filter(d => d))).sort();
        const allStyles = Array.from(new Set(data.map(d => d.style1).filter(d => d && d !== "nan"))).sort();

        let heatmapData = [];
        allTypes.forEach(type => {
            allStyles.forEach(style => {
                const val = heatmapRollup.get(type)?.get(style) || 0;
                heatmapData.push({ group: type, variable: style, value: val });
            });
        });

        // --- 2. PREPARAR DATOS COLORES ---
        const colorRollup = d3.rollup(data, v => v.length, d => d.Color);
        let colorData = Array.from(colorRollup, ([key, value]) => ({ color: key, count: value }))
            .sort((a, b) => b.count - a.count).slice(0, 15);

        // --- 3. DATOS FIT ---
        const fitRollup = d3.rollup(data, v => v.length, d => d.fit1);
        let fitData = Array.from(fitRollup, ([key, value]) => ({ fit: key, count: value }))
            .filter(d => d.fit && d.fit !== "nan");

        // --- 4. DATOS WEATHER ---
        const weatherRollup = d3.rollup(data, v => v.length, d => d.weather);
        let weatherData = Array.from(weatherRollup, ([key, value]) => ({ weather: key, count: value }))
            .filter(d => d.weather && d.weather !== "nan");

        const sectionContainer = document.getElementById("section-prendas");
        if(sectionContainer) {
            sectionContainer.innerHTML = `
                <h2 class="mb-2 text-center fw-bold" style="color:${PALETA.dark}">Inventario Inteligente</h2>
                <p class="text-center mb-4" style="color:${PALETA.secondary}">Análisis de Stock, Estilos y Ajustes</p>
                <div class="row g-4 mb-4">
                    <div class="col-12">
                        <div class="chart-container p-4">
                            <div class="d-flex justify-content-between align-items-center mb-3">
                                <h5 class="fw-bold mb-0" style="color:${PALETA.primary}">Mapa de Estilos</h5>
                                <small class="text-muted">Densidad por Estilo y Tipo</small>
                            </div>
                            <div id="heatmapChart"></div>
                        </div>
                    </div>
                </div>
                <div class="row g-4">
                    <div class="col-12 col-lg-6">
                        <div class="chart-container p-4">
                            <h5 class="fw-bold mb-3" style="color:${PALETA.primary}">Colores Top 15</h5>
                            <div id="realColorChart"></div>
                        </div>
                    </div>
                    <div class="col-12 col-md-6 col-lg-3">
                        <div class="chart-container p-4">
                            <h5 class="fw-bold mb-3" style="color:${PALETA.primary}">Distribución por Fit</h5>
                            <div id="fitChart" class="d-flex justify-content-center"></div>
                        </div>
                    </div>
                    <div class="col-12 col-md-6 col-lg-3">
                        <div class="chart-container p-4">
                            <h5 class="fw-bold mb-3" style="color:${PALETA.primary}">Clima (Weather)</h5>
                            <div id="weatherChart" class="d-flex justify-content-center"></div>
                        </div>
                    </div>
                </div>
            `;
        }

        setTimeout(() => {
            drawHeatmap(heatmapData, allStyles, allTypes);
            drawRealColorChart(colorData);
            drawDonutChart(fitData, "fitChart", "fit");
            drawPieChart(weatherData, "weatherChart", "weather");
        }, 100);
    });
}

function drawHeatmap(data, xLabels, yLabels) {
    const container = document.getElementById("heatmapChart");
    if (!container) return;
    container.innerHTML = "";

    const width = container.getBoundingClientRect().width || 800;
    const height = 450;
    const margin = { top: 30, right: 30, bottom: 60, left: 100 };

    const svg = d3.select(container).append("svg")
        .attr("width", width).attr("height", height)
        .append("g").attr("transform", `translate(${margin.left},${margin.top})`);

    const w = width - margin.left - margin.right;
    const h = height - margin.top - margin.bottom;

    const x = d3.scaleBand().range([0, w]).domain(xLabels).padding(0.05);
    const y = d3.scaleBand().range([h, 0]).domain(yLabels).padding(0.05);

    const myColor = d3.scaleLinear().domain([0, d3.max(data, d => d.value)]).range(["#ffebe6", PALETA.primary]); 

    svg.append("g").attr("transform", `translate(0,${h})`).call(d3.axisBottom(x).tickSize(0)).select(".domain").remove();
    svg.selectAll(".tick text").style("font-size", "12px").style("fill", PALETA.dark).style("font-weight", "500");
    svg.append("g").call(d3.axisLeft(y).tickSize(0)).select(".domain").remove();

    svg.selectAll()
        .data(data, d => d.group + ':' + d.variable)
        .join("rect")
        .attr("x", d => x(d.variable))
        .attr("y", d => y(d.group))
        .attr("width", x.bandwidth())
        .attr("height", y.bandwidth())
        .style("fill", d => d.value === 0 ? PALETA.empty : myColor(d.value))
        .style("rx", 4).style("ry", 4)
        .style("stroke", "none")
        .on("mouseover", function(event, d) {
            d3.select(this).style("stroke", PALETA.dark).style("stroke-width", 2);
            tooltip.style("opacity", 1)
                .html(`<strong>${d.group}</strong> - ${d.variable}<br>Cantidad: ${d.value}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function(event, d) {
            d3.select(this).style("stroke", "none");
            tooltip.style("opacity", 0);
        });
}

function drawDonutChart(data, containerId, keyLabel) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const width = 250, height = 250, margin = 20;
    const radius = Math.min(width, height) / 2 - margin;
    const svg = d3.select(`#${containerId}`)
      .append("svg").attr("width", width).attr("height", height)
      .append("g").attr("transform", `translate(${width / 2},${height / 2})`);
    const color = d3.scaleOrdinal().range([PALETA.primary, PALETA.secondary, PALETA.accent, PALETA.dark, "#dba598"]);
    const pie = d3.pie().value(d => d.count);
    const data_ready = pie(data);
    const arc = d3.arc().innerRadius(radius * 0.5).outerRadius(radius);
    const arcHover = d3.arc().innerRadius(radius * 0.5).outerRadius(radius * 1.1);
    svg.selectAll('path').data(data_ready).join('path')
        .attr('d', arc).attr('fill', d => color(d.data[keyLabel])).attr("stroke", "white").style("stroke-width", "2px")
        .on("mouseover", function(event, d) {
            d3.select(this).transition().duration(200).attr("d", arcHover);
            tooltip.style("opacity", 1).html(`<strong>${d.data[keyLabel]}</strong><br>${d.data.count}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).transition().duration(200).attr("d", arc);
            tooltip.style("opacity", 0);
        });
}

function drawPieChart(data, containerId, keyLabel) {
    const container = document.getElementById(containerId);
    if (!container) return;
    const width = 200, height = 200, margin = 10;
    const radius = Math.min(width, height) / 2 - margin;
    const svg = d3.select(`#${containerId}`)
      .append("svg").attr("width", width).attr("height", height)
      .append("g").attr("transform", `translate(${width / 2},${height / 2})`);
    const colorMap = {"warm": PALETA.accent, "cold": "#74b9ff"}; 
    const pie = d3.pie().value(d => d.count);
    const data_ready = pie(data);
    const arc = d3.arc().innerRadius(0).outerRadius(radius);
    svg.selectAll('path').data(data_ready).join('path')
        .attr('d', arc).attr('fill', d => colorMap[d.data[keyLabel]] || PALETA.secondary).attr("stroke", "white").style("stroke-width", "2px")
        .on("mouseover", function(event, d) {
            d3.select(this).attr("opacity", 0.8);
            tooltip.style("opacity", 1).html(`<strong>${d.data[keyLabel]}</strong><br>${d.data.count}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", function() {
            d3.select(this).attr("opacity", 1);
            tooltip.style("opacity", 0);
        });
}

function drawRealColorChart(data) {
    const container = document.getElementById("realColorChart");
    if (!container) return;
    container.innerHTML = "";
    const width = container.getBoundingClientRect().width || 400;
    const height = 300; 
    const margin = { top: 20, right: 20, bottom: 80, left: 40 };
    const svg = d3.select(container).append("svg")
        .attr("width", width).attr("height", height)
        .append("g").attr("transform", `translate(${margin.left},${margin.top})`);
    const x = d3.scaleBand().range([0, width - margin.left - margin.right]).domain(data.map(d => d.color)).padding(0.2);
    const y = d3.scaleLinear().domain([0, d3.max(data, d => d.count)]).range([height - margin.top - margin.bottom, 0]);
    svg.append("g").attr("transform", `translate(0,${height - margin.top - margin.bottom})`)
        .call(d3.axisBottom(x)).selectAll("text")
        .attr("transform", "translate(-10,0)rotate(-45)").style("text-anchor", "end").style("fill", PALETA.dark);
    svg.append("g").call(d3.axisLeft(y).ticks(5));
    const getColorHex = (name) => {
        const lowerName = name ? name.toLowerCase() : "";
        const map = {
            'black': '#2d3436', 'white': '#f5f6fa', 'navy': '#0c2461', 'blue': '#0984e3', 
            'blue_dark': '#0c2461', 'blue_light': '#74b9ff', 'red': '#d63031', 'grey': '#b2bec3', 
            'green': '#00b894', 'green_dark': '#006266', 'beige': '#f5f5dc', 'pink': '#fd79a8', 
            'purple': '#6c5ce7', 'yellow': '#ffeaa7', 'orange': '#e17055', 'brown': '#8d6e63', 
            'ecru': '#C2B280', 'mustard': '#E1AD01', 'rust': '#B7410E', 'camel': '#C19A6B',
            'khaki': '#C3B091', 'lilac': '#C8A2C8', 'fuchsia': '#FF00FF', 'salmon': '#FA8072',
            'crimson': '#DC143C', 'coral': '#FF7F50', 'brick': '#8B0000', 'garnet': '#733635',
            'aubergine': '#580F41', 'nude': '#E3BC9A', 'silver': '#C0C0C0', 'gold': '#FFD700',
            'mint': '#98FF98', 'olive': '#808000', 'multicolor': '#bdc3c7'
        };
        return map[lowerName] || '#95a5a6';
    };
    svg.selectAll("mybar").data(data).join("rect")
        .attr("x", d => x(d.color)).attr("y", d => y(d.count))
        .attr("width", x.bandwidth()).attr("height", d => (height - margin.top - margin.bottom) - y(d.count))
        .attr("fill", d => getColorHex(d.color)).attr("stroke", "#999").attr("stroke-width", "0.5px")
        .on("mouseover", (event, d) => {
            d3.select(event.currentTarget).attr("opacity", 0.7);
            tooltip.style("opacity", 1).html(`<strong>${d.color}</strong><br>${d.count}`)
                .style("left", (event.pageX + 10) + "px").style("top", (event.pageY - 28) + "px");
        })
        .on("mouseout", (e) => {
            d3.select(e.currentTarget).attr("opacity", 1);
            tooltip.style("opacity", 0);
        });
}