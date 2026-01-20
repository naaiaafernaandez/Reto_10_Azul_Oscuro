/* =====================================================
   CONFIGURACIÓN DE COLOR
===================================================== */

const baseColors = [
  "#0057B8", // Azul
  "#3B3B98", // Azul violeta
  "#6F1E51", // Violeta
  "#B53471", // Rojo violeta
  "#C0392B", // Rojo
  "#D35400", // Rojo naranja
  "#E67E22", // Naranja
  "#F39C12", // Amarillo naranja
  "#F1C40F", // Amarillo
  "#A3CB38", // Amarillo verdoso
  "#27AE60", // Verde
  "#16A085"  // Azul verdoso
];

const TOTAL_MATICES = 12;
const TOTAL_INTENSIDADES = 7;

// LÓGICA CORREGIDA:
function colorConIntensidad(hex, intensidad) {
  let color = tinycolor(hex);

  // 1. EL CENTRO (Anillo 0): Profundidad Sutil
  // Antes era darken(18), lo bajamos a 8 para que no sea "demasiado oscuro".
  if (intensidad === 0) {
    return color.darken(8).toString(); 
  }

  // 2. EL PRIMER ANILLO (Anillo 1): Color Base Exacto
  // Mantenemos este anillo como la referencia pura del color.
  if (intensidad === 1) {
    return color.toString();
  }

  // 3. ANILLOS EXTERIORES: Gradiente hacia el blanco
  // Ajustamos el multiplicador para que el degradado sea suave hasta el final.
  const paso = intensidad - 1; // 1, 2, 3, 4...
  const brillo = paso * 10;    
  const desaturacion = paso * 3;

  return color
    .brighten(brillo)
    .desaturate(desaturacion)
    .toString();
}

/* =====================================================
   SVG / GEOMETRÍA
===================================================== */

const svg = document.getElementById("wheel");
const CENTER = 260;       
const DONUT_WIDTH = 26;   
const START_RADIUS = 70;  

function donutSlicePath(cx, cy, r1, r2, startAngle, endAngle) {
  const rad = a => (Math.PI / 180) * a;

  const x1 = cx + r2 * Math.cos(rad(startAngle));
  const y1 = cy + r2 * Math.sin(rad(startAngle));
  const x2 = cx + r2 * Math.cos(rad(endAngle));
  const y2 = cy + r2 * Math.sin(rad(endAngle));
  const x3 = cx + r1 * Math.cos(rad(endAngle));
  const y3 = cy + r1 * Math.sin(rad(endAngle));
  const x4 = cx + r1 * Math.cos(rad(startAngle));
  const y4 = cy + r1 * Math.sin(rad(startAngle));

  return `
    M ${x1} ${y1}
    A ${r2} ${r2} 0 0 1 ${x2} ${y2}
    L ${x3} ${y3}
    A ${r1} ${r1} 0 0 0 ${x4} ${y4}
    Z
  `;
}

/* =====================================================
   REGLAS DE COMBINACIÓN
===================================================== */

function combinan(a, b) {
  const dm = Math.abs(a.matiz - b.matiz);
  const di = Math.abs(a.intensidad - b.intensidad);

  if (a.matiz === b.matiz && a.intensidad === b.intensidad) return false;
  if (a.matiz === b.matiz) return di >= 2;
  if (dm === 1 || dm === 11) return true;
  if (dm === 6) return true;
  if (dm === 4 || dm === 8) return true;

  return false;
}

/* =====================================================
   DIBUJAR LA RUEDA
===================================================== */

const slices = [];

while (svg.firstChild) {
  svg.removeChild(svg.firstChild);
}

for (let intensidad = 0; intensidad < TOTAL_INTENSIDADES; intensidad++) {
  const r1 = START_RADIUS + intensidad * DONUT_WIDTH;
  const r2 = r1 + DONUT_WIDTH;

  for (let matiz = 0; matiz < TOTAL_MATICES; matiz++) {
    const startAngle = (360 / TOTAL_MATICES) * matiz - 90;
    const endAngle = startAngle + 360 / TOTAL_MATICES;

    const path = document.createElementNS(
      "http://www.w3.org/2000/svg",
      "path"
    );

    path.setAttribute(
      "d",
      donutSlicePath(CENTER, CENTER, r1, r2, startAngle, endAngle)
    );

    path.setAttribute(
      "fill",
      colorConIntensidad(baseColors[matiz], intensidad)
    );

    path.classList.add("slice");

    const colorData = { matiz, intensidad };
    slices.push({ el: path, data: colorData });

    path.addEventListener("click", () => seleccionar(colorData));

    svg.appendChild(path);
  }
}

/* =====================================================
   INTERACCIÓN
===================================================== */

function seleccionar(colorSeleccionado) {
  slices.forEach(({ el, data }) => {
    const esCompatible = combinan(colorSeleccionado, data);
    el.classList.toggle("hidden", !esCompatible);

    const esElMismo = 
      data.matiz === colorSeleccionado.matiz &&
      data.intensidad === colorSeleccionado.intensidad;
      
    el.classList.toggle("active", esElMismo);
  });
}