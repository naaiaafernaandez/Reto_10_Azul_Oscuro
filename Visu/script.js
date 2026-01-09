document.addEventListener('DOMContentLoaded', () => {

  // ===== CONFIGURACIÓN DE COLORES =====
  const baseColors = [
    "#0057B8", "#3B3B98", "#6F1E51", "#B53471",
    "#C0392B", "#D35400", "#E67E22", "#F39C12",
    "#F1C40F", "#A3CB38", "#27AE60", "#16A085"
  ];

  const TOTAL_MATICES = 12;
  const TOTAL_INTENSIDADES = 7;
  const CENTER = 260; // Centro del viewBox (520 / 2)
  const DONUT_WIDTH = 26;
  const START_RADIUS = 70;

  const svg = document.getElementById("wheel");

  // ===== FUNCIONES AUXILIARES =====
  function colorConIntensidad(hex, intensidad) {
    let color = tinycolor(hex);
    if (intensidad === 0) return color.darken(8).toString();
    if (intensidad === 1) return color.toString();
    const paso = intensidad - 1;
    const brillo = paso * 10;
    const desaturacion = paso * 3;
    return color.brighten(brillo).desaturate(desaturacion).toString();
  }

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

    return `M ${x1} ${y1} A ${r2} ${r2} 0 0 1 ${x2} ${y2} L ${x3} ${y3} A ${r1} ${r1} 0 0 0 ${x4} ${y4} Z`;
  }

  function combinan(a, b) {
    const dm = Math.abs(a.matiz - b.matiz);
    const di = Math.abs(a.intensidad - b.intensidad);
    
    // Si es el mismo, devuelve false en la lógica matemática
    if (a.matiz === b.matiz && a.intensidad === b.intensidad) return false;
    
    if (a.matiz === b.matiz) return di >= 2;
    if (dm === 1 || dm === 11) return true;
    if (dm === 6) return true;
    if (dm === 4 || dm === 8) return true;
    return false;
  }

  // ===== DIBUJAR LA RUEDA =====
  const slices = [];
  
  // Limpiamos el SVG antes de dibujar
  while (svg.firstChild) svg.removeChild(svg.firstChild);

  // 1. CREAR EL BOTÓN CENTRAL (RESET)
  // Lo creamos primero o después, pero necesitamos que esté ahí.
  // Usamos un círculo transparente en el centro.
  const centerBtn = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  centerBtn.setAttribute("cx", CENTER);
  centerBtn.setAttribute("cy", CENTER);
  centerBtn.setAttribute("r", START_RADIUS - 5); // Un poco menos que el inicio de la rueda
  centerBtn.setAttribute("fill", "transparent"); // Invisible
  centerBtn.style.cursor = "pointer"; // Manita al pasar por encima
  
  // Evento Reset al pulsar el centro
  centerBtn.addEventListener("click", resetWheel);
  
  // Nota: Lo añadimos al final del todo para que esté "encima" de todo por si acaso,
  // aunque al ser un hueco no importa mucho.

  // 2. DIBUJAR LOS TROZOS (SLICES)
  for (let intensidad = 0; intensidad < TOTAL_INTENSIDADES; intensidad++) {
    const r1 = START_RADIUS + intensidad * DONUT_WIDTH;
    const r2 = r1 + DONUT_WIDTH;

    for (let matiz = 0; matiz < TOTAL_MATICES; matiz++) {
      const startAngle = (360 / TOTAL_MATICES) * matiz - 90;
      const endAngle = startAngle + 360 / TOTAL_MATICES;

      const path = document.createElementNS("http://www.w3.org/2000/svg", "path");
      path.setAttribute("d", donutSlicePath(CENTER, CENTER, r1, r2, startAngle, endAngle));
      path.setAttribute("fill", colorConIntensidad(baseColors[matiz], intensidad));
      path.classList.add("slice");

      const colorData = { matiz, intensidad };
      slices.push({ el: path, data: colorData });

      path.addEventListener("click", (e) => {
        // Evitamos que el click se propague al círculo central si se solapan
        e.stopPropagation(); 
        seleccionar(colorData);
      });

      svg.appendChild(path);
    }
  }

  // Añadimos el botón central al final
  svg.appendChild(centerBtn);

  // ===== INTERACCIÓN =====
  
  function seleccionar(colorSeleccionado) {
    slices.forEach(({ el, data }) => {
      const esCompatible = combinan(colorSeleccionado, data);
      
      // Comprobamos si es exactamente el mismo que pulsamos
      const esElMismo = data.matiz === colorSeleccionado.matiz && data.intensidad === colorSeleccionado.intensidad;

      // LÓGICA DE OCULTAR:
      // Ocultamos SI (NO es compatible) Y (NO es el mismo que pulsé)
      // De esta forma, el que pulsé se queda visible.
      const debeOcultarse = !esCompatible && !esElMismo;
      
      el.classList.toggle("hidden", debeOcultarse);
      el.classList.toggle("active", esElMismo);
    });
  }

  function resetWheel() {
    // Quitamos las clases hidden y active de todos
    slices.forEach(({ el }) => {
      el.classList.remove("hidden");
      el.classList.remove("active");
    });
  }

});