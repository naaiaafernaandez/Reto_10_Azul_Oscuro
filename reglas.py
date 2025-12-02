

def reglas_color(codigo_A, codigo_B):
    # 0. REGLA DE NEUTROS (Blanco y Negro)
    # Asume que tienes una lista con los códigos de blanco y negro
    # Si tus códigos son numéricos fuera del rango 0-116, ponlos aquí.
    neuros = [999, -1] # Ejemplo: Sustituye con tus códigos reales de blanco/negro
    
    if codigo_A in neuros or codigo_B in neuros:
        return True # Combinan con todo

    # DECODIFICACIÓN
    matiz_A = codigo_A // 10
    intensidad_A = codigo_A % 10
    
    matiz_B = codigo_B // 10
    intensidad_B = codigo_B % 10
    
    # Calcular distancia en la rueda (0 a 11)
    # Esto nos dice cuántos "quesitos" del círculo los separan
    distancia = abs(matiz_A - matiz_B)
    
    # ---------------------------------------------------------
    # 1. MONOCROMÁTICAS (Mismo color, distinta intensidad)
    # ---------------------------------------------------------
    if matiz_A == matiz_B:
        # La regla dice: NO pueden ser consecutivas (salto >= 2)
        # Ejemplo: 15 y 16 (diferencia 1) -> False
        # Ejemplo: 15 y 17 (diferencia 2) -> True
        if abs(intensidad_A - intensidad_B) >= 2:
            return True
        else:
            return False # Son el mismo color pero intensidades muy cercanas

    # ---------------------------------------------------------
    # 2. ANÁLOGAS (Vecinos en la rueda)
    # ---------------------------------------------------------
    # Vecinos significa distancia 1.
    # OJO: El color 0 y el color 11 son vecinos (cierre del círculo)
    if distancia == 1 or distancia == 11:
        return True

    # ---------------------------------------------------------
    # 3. COMPLEMENTARIAS (Opuestos en la rueda)
    # ---------------------------------------------------------
    # En una rueda de 12, el opuesto está exactamente a 6 pasos.
    if distancia == 6:
        return True

    # ---------------------------------------------------------
    # 4. TRIÁDICAS (Triángulo equilátero)
    # ---------------------------------------------------------
    # En una rueda de 12, un triángulo divide el círculo en 3 partes de 4 pasos.
    # Ejemplo: 0, 4, 8. 
    # Distancia entre 0 y 4 es 4. Distancia entre 0 y 8 es 8.
    if distancia == 4 or distancia == 8:
        return True

    # Si no cumple ninguna, no hay arista
    return False

reglas_color(12, 15)

season1 = 0
season2 = 0

def reglas_estructura_niveles(prenda_A, prenda_B):
    # Definimos los niveles (esto debería venir de tus datos)
    # Supongamos que en tu df tienes una columna 'nivel' con valores 1, 2 o 3
    nivel_A = prenda_A['nivel']
    nivel_B = prenda_B['nivel']

    # REGLA CRÍTICA: Nunca conectar dos prendas de Nivel 1
    # No queremos looks con dos pantalones o pantalón + vestido
    if nivel_A == 1 and nivel_B == 1:
        return False
    
    # OPCIONAL: Si quieres ser estricto con la regla de "1 de nivel 1 + 2 de otros"
    # Podrías decidir conectar Nivel 1 SOLO con Nivel 2 o 3.
    # Pero conectar Nivel 2 con Nivel 2 (Camiseta + Jersey) SÍ está permitido.
    # Conectar Nivel 3 con Nivel 3 (Chaqueta + Bufanda) SÍ está permitido.
    
    return True





def validar_conexion(prenda_A, prenda_B):
    """
    Devuelve True si prenda_A y prenda_B cumplen TODAS las reglas (Temporada, Nivel y Color).
    Asume que las prendas son diccionarios/filas con: 'season', 'nivel', 'color_code'.
    """

    # -----------------------------------------------------
    # 1. REGLA DE TEMPORADA (Obligatoria) 
    # -----------------------------------------------------
    if prenda_A['season'] != prenda_B['season']:
        return False

    # -----------------------------------------------------
    # 2. REGLA DE NIVELES (Estructural)
    # -----------------------------------------------------
    # Evitar conectar dos prendas de Nivel 1 (ej. Pantalón + Falda)
    # Esto facilita luego buscar triangulos de 1 prenda Nvl1 + 2 prendas Nvl2/3
    if prenda_A['nivel'] == 1 and prenda_B['nivel'] == 1:
        return False

    # -----------------------------------------------------
    # 3. REGLAS DE COLOR (Matemática del círculo cromático)
    # -----2wqx------------------------------------------------
    code_A = prenda_A['color_code']
    code_B = prenda_B['color_code']

    # CASO ESPECIAL: Neutros (Blanco/Negro)
    # Si tienes códigos específicos para ellos (ej. -1 o 999), ponlos aquí.
    # Si combinan con todo, devolvemos True directamente.
    codigos_neutros = [-1, 999] 
    if code_A in codigos_neutros or code_B in codigos_neutros and code_A != code_B:
        return True

    # Decodificación (Tu sistema: Decena=Matiz, Unidad=Intensidad)
    matiz_A = code_A // 10    # Del 0 al 11
    int_A   = code_A % 10     # Del 0 al 6
    
    matiz_B = code_B // 10
    int_B   = code_B % 10
    
    # Distancia en la rueda (número de pasos entre colores)
    distancia = abs(matiz_A - matiz_B)

    # --- A) Monocromáticas ---
    # Mismo matiz, pero saltando intensidades (diferencia >= 2)
    if matiz_A == matiz_B:
        if abs(int_A - int_B) >= 2:
            return True
        else:
            return False # Intensidades consecutivas o iguales no valen

    # --- B) Análogas ---
    # Colores vecinos (distancia 1) o el cierre del círculo (0 y 11)
    if distancia == 1 or distancia == 11:
        return True

    # --- C) Complementarias ---
    # Colores opuestos exactos (mitad del reloj de 12 horas)
    if distancia == 6:
        return True

    # --- D) Triádicas ---
    # Triángulo equilátero (cada 4 horas)
    if distancia == 4 or distancia == 8:
        return True

    # Si no ha entrado en ningún if anterior, no combinan
    return False