const colores = [
    { id: 0, color: "#e74c3c" }, // rojo
    { id: 1, color: "#e67e22" }, // naranja
    { id: 2, color: "#f1c40f" }, // amarillo
    { id: 3, color: "#badc58" }, // amarillo verdoso
    { id: 4, color: "#6ab04c" }, // verde
    { id: 5, color: "#1abc9c" }, // verde azulado
    { id: 6, color: "#3498db" }, // azul
    { id: 7, color: "#4834d4" }, // azul violáceo
    { id: 8, color: "#8e44ad" }, // violeta
    { id: 9, color: "#be2edd" }, // violeta rojizo
    { id: 10, color: "#ff7675" }, // rojo rosado
    { id: 11, color: "#d63031" } // rojo profundo
];


function combinan(matizA, matizB) {
    const distancia = Math.abs(matizA - matizB);

    // Análogas
    if (distancia === 1 || distancia === 11) return true;

    // Complementarias
    if (distancia === 6) return true;

    // Triádicas
    if (distancia === 4 || distancia === 8) return true;

    // Monocromáticas (mismo matiz)
    if (matizA === matizB) return true;

    return false;
}

const wheel = document.getElementById("wheel");
const angleStep = 360 / colores.length;

colores.forEach((c, index) => {
    const slice = document.createElement("div");
    slice.className = "color-slice";
    slice.style.background = c.color;
    slice.style.transform = `rotate(${index * angleStep}deg) skewY(-60deg)`;
    slice.dataset.matiz = c.id;

    slice.addEventListener("click", () => seleccionarColor(c.id));

    wheel.appendChild(slice);
});

function seleccionarColor(matizSeleccionado) {
    document.querySelectorAll(".color-slice").forEach(slice => {
        const matiz = parseInt(slice.dataset.matiz);

        if (combinan(matizSeleccionado, matiz)) {
            slice.classList.remove("hidden");
        } else {
            slice.classList.add("hidden");
        }

        slice.classList.toggle("active", matiz === matizSeleccionado);
    });
}