C_RELAXED = {'casual', 'street', 'freetime'}
C_FORMAL  = {'classic', 'minimal', 'work', 'working_girl'}
C_BOHO    = {'boho'}
C_PARTY   = {'night', 'special_occasion'}

# Grupos de Estampados
G_LISO        = {'smooth', 'solid', 'liso'}
G_MICRO       = {'miniprint', 'bodoque', 'two_tone'}
G_RAYAS       = {'horizontal_stripes', 'vertical_stripes', 'diagonal_stripe', 'mariniere'}
G_CUADROS     = {'checked', 'vichy', 'tartan', 'rhombus_fabric', 'geometric', 'prince_of_wales'}
G_ORGANICOS   = {'floral', 'liberty', 'tropical', 'sheets', 'cachemere', 'tie_dye', 'gradient', 'tapestry'}
G_GEOMETRICOS = {'geometric', 'retro', 'ethnic', 'rhombus_fabric', 'herringbone', 'pied_de_poule'}
G_PUNTOS      = {'polka_dot'}
G_AUDACES     = {'animal_print', 'camouflage', 'army'}

def validar_par_final(p1, p2):
    # FASE 0: FÍSICOS
    if p1['nivel'] == 1 and p2['nivel'] == 1: return False
    if 'oversize' in p1['fits'] and 'oversize' in p2['fits']: return False
    # FASE 1: ESTILO
    if p1['has_style'] and p2['has_style']:
        s1, s2 = p1['styles'], p2['styles']
        r1, r2 = not s1.isdisjoint(C_RELAXED), not s2.isdisjoint(C_RELAXED)
        f1, f2 = not s1.isdisjoint(C_FORMAL), not s2.isdisjoint(C_FORMAL)
        match = False
        if (r1 and r2) or (f1 and f2): match = True
        elif not s1.isdisjoint(C_BOHO) and not s2.isdisjoint(C_BOHO): match = True
        elif not s1.isdisjoint(C_PARTY) and not s2.isdisjoint(C_PARTY): match = True
        else:
            if (r1 and f2) or (r2 and f1): match = True
            elif (not s1.isdisjoint(C_BOHO) and r2) or (not s2.isdisjoint(C_BOHO) and r1): match = True
            p1p, p2p = not s1.isdisjoint(C_PARTY), not s2.isdisjoint(C_PARTY)
            if (p1p and (f2 or r2)) or (p2p and (f1 or r1)): match = True
        if not match: return False

    # FASE 2: PRINTS
    if p1['is_print'] and p2['is_print']:
        pr1, pr2 = p1['prints'], p2['prints']
        es_liso_1 = pr1.isdisjoint(G_LISO)
        es_liso_2 = pr2.isdisjoint(G_LISO)
        # ---- 1) LISO + ESTAMPADO → siempre combina ----
        if not p1['is_print'] or not p2['is_print']:
            pass  
        # ---- 2) CUADROS + CUADROS → depende del color (lo validará fase 3) ----
        elif (not pr1.isdisjoint(G_CUADROS)) and (not pr2.isdisjoint(G_CUADROS)):
            pass  
        # ---- 3) ANIMAL + GEOMÉTRICO → mismo tono ----
        elif ((not pr1.isdisjoint(G_AUDACES) and not pr2.isdisjoint(G_GEOMETRICOS)) or
            (not pr2.isdisjoint(G_AUDACES) and not pr1.isdisjoint(G_GEOMETRICOS))):
            if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0:
                return False
        # ---- 4) FLORES + RAYAS → mismo tono ----
        elif ((not pr1.isdisjoint(G_ORGANICOS) and not pr2.isdisjoint(G_RAYAS)) or
            (not pr2.isdisjoint(G_ORGANICOS) and not pr1.isdisjoint(G_RAYAS))):
            if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0:
                return False
        # ---- 5) RAYAS + TOPOS → mismo tono ----
        elif ((not pr1.isdisjoint(G_PUNTOS) and not pr2.isdisjoint(G_RAYAS)) or
            (not pr2.isdisjoint(G_PUNTOS) and not pr1.isdisjoint(G_RAYAS))):
            if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0:
                return False
        else:
            return False

    # FASE 3: COLOR
    c1, c2 = p1['color_nivel'], p2['color_nivel']
    if c1 in (0, 2, 4) or c2 in (0, 2, 4): return True # Colores neutros/comodín
    
    h1, i1 = divmod(c1, 10)
    h2, i2 = divmod(c2, 10)
    
    dist = min(abs(h1 - h2), 12 - abs(h1 - h2))
    
    if dist == 0: return abs(i1 - i2) >= 2 # Mismo tono, diferente intensidad
    if dist in (1, 4, 6): return True # Análogos, Tríada, Complementario
    
    return False

def calcular_afinidad(p1, p2):
    """
    Calcula la compatibilidad entre dos prendas devolviendo un score de 0 a 100.
    
    Retorna 0: Combinación prohibida (rompe reglas duras).
    Retorna >0: Grado de afinidad (mientras más alto, mejor look).
    """
    score = 0
    
    # ==========================================================================
    # 1. FILTROS BLOQUEANTES (Hard Constraints) -> Return 0
    # ==========================================================================
    
    # Regla: Mismo nivel principal (ej. dos pantalones no hacen un look)
    # Asumimos que nivel 1 es parte baja/cuerpo entero.
    if p1.get('nivel') == 1 and p2.get('nivel') == 1:
        return 0
        
    # Regla: Temporada (Deben ser de la misma temporada)
    # Si tus datos tienen valores nulos en temporada, puedes suavizar esto.
    if p1.get('temporada') != p2.get('temporada'):
        return 0

    # Regla: Fits incompatibles (Dos oversize juntos pueden verse mal)
    if 'oversize' in p1.get('fits', set()) and 'oversize' in p2.get('fits', set()):
        return 0

    # ==========================================================================
    # 2. EVALUACIÓN DE ESTAMPADOS (Prints)
    # ==========================================================================
    # Si ambos tienen estampados "difíciles", verificamos reglas complejas.
    
    tiene_print_1 = p1.get('is_print', False)
    tiene_print_2 = p2.get('is_print', False)
    
    # Bonificación base: Combinar Liso + Estampado es ideal
    if tiene_print_1 != tiene_print_2:
        score += 15
    
    # Si AMBOS son estampados, aplicamos tus reglas restrictivas
    elif tiene_print_1 and tiene_print_2:
        pr1, pr2 = p1.get('prints', set()), p2.get('prints', set())
        prints_compatibles = False
        
        # Caso A: Microestampados o Rayas suelen ser neutros
        if (not pr1.isdisjoint(G_MICRO)) or (not pr2.isdisjoint(G_MICRO)):
            prints_compatibles = True
            score += 5
            
        # Caso B: Cuadros + Cuadros (Aceptable)
        elif (not pr1.isdisjoint(G_CUADROS)) and (not pr2.isdisjoint(G_CUADROS)):
            prints_compatibles = True
            score += 5
            
        # Caso C: Animal/Audaz + Geométrico (Solo si combinan color)
        # Nota: Aquí simplificamos. Si quieres ser estricto con el color exacto,
        # lo penalizaremos en la sección de color si no combinan.
        elif ((not pr1.isdisjoint(G_AUDACES) and not pr2.isdisjoint(G_GEOMETRICOS)) or
              (not pr2.isdisjoint(G_AUDACES) and not pr1.isdisjoint(G_GEOMETRICOS))):
             prints_compatibles = True
             score += 10 # Premiamos el riesgo si sale bien
             
        # Caso D: Orgánicos (Flores) + Rayas
        elif ((not pr1.isdisjoint(G_ORGANICOS) and not pr2.isdisjoint(G_RAYAS)) or
              (not pr2.isdisjoint(G_ORGANICOS) and not pr1.isdisjoint(G_RAYAS))):
             prints_compatibles = True
             score += 10

        # Si son dos estampados y NO caen en ninguna regla compatible -> Prohibido
        if not prints_compatibles:
            return 0

    # ==========================================================================
    # 3. AFINIDAD DE ESTILO
    # ==========================================================================
    if p1.get('has_style') and p2.get('has_style'):
        s1, s2 = p1.get('styles', set()), p2.get('styles', set())
        
        # Coincidencia exacta (ej. Boho + Boho)
        if not s1.isdisjoint(s2):
            score += 30
            
        # Estilos compatibles cruzados
        # Relaxed + Formal = Smart Casual (Muy buena combi)
        elif (not s1.isdisjoint(C_RELAXED) and not s2.isdisjoint(C_FORMAL)) or \
             (not s2.isdisjoint(C_RELAXED) and not s1.isdisjoint(C_FORMAL)):
            score += 20
            
        # Boho + Relaxed (Natural)
        elif (not s1.isdisjoint(C_BOHO) and not s2.isdisjoint(C_RELAXED)) or \
             (not s2.isdisjoint(C_BOHO) and not s1.isdisjoint(C_RELAXED)):
            score += 15
            
        # Party + Formal (Elegante noche)
        elif (not s1.isdisjoint(C_PARTY) and not s2.isdisjoint(C_FORMAL)) or \
             (not s2.isdisjoint(C_PARTY) and not s1.isdisjoint(C_FORMAL)):
            score += 25
    else:
        # Si faltan datos de estilo, sumamos algo neutro
        score += 10

    # ==========================================================================
    # 4. ARMONÍA DE COLOR
    # ==========================================================================
    # Usamos tu lógica de color_nivel (0-120 aprox) donde decenas=matiz, unidad=brillo
    c1, c2 = p1.get('color_nivel', 0), p2.get('color_nivel', 0)
    
    # Colores neutros (Negro, Gris, Blanco) combinan con todo
    # Asumimos valores típicos: 0=Negro, 2=Gris, 4=Blanco (según tu notebook)
    NEUTROS = {0, 2, 4} 
    if c1 in NEUTROS or c2 in NEUTROS:
        score += 20
    else:
        # Extraemos Matiz (hue) e Intensidad
        h1, i1 = divmod(c1, 10)
        h2, i2 = divmod(c2, 10)
        
        # Distancia en círculo cromático de 12 colores
        dist = min(abs(h1 - h2), 12 - abs(h1 - h2))
        
        if dist == 0: 
            # Monocromático (Mismo color base)
            # Se ve mejor si hay contraste de intensidad (Claro con Oscuro)
            if abs(i1 - i2) >= 2:
                score += 30
            else:
                score += 10
        elif dist == 1:
            # Análogos (Vecinos, ej. Azul y Azul-Verdoso) -> Armonía suave
            score += 20
        elif dist >= 4:
            # Complementarios o Triada (Contraste fuerte) -> Look vibrante
            score += 35
        else:
            # Colores sin relación clara
            score += 5

    # ==========================================================================
    # 5. NORMALIZACIÓN FINAL
    # ==========================================================================
    # Aseguramos base mínima para que no queden en 0 si pasaron los filtros duros
    score += 10 
    
    return min(score, 100)