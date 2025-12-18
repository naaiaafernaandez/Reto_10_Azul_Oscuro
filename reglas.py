# C_RELAXED = {'casual', 'street', 'freetime'}
# C_FORMAL  = {'classic', 'minimal', 'work', 'working_girl'}
# C_BOHO    = {'boho'}
# C_PARTY   = {'night', 'special_occasion'}

# # Grupos de Estampados
# G_LISO        = {'smooth', 'solid', 'liso'}
# G_MICRO       = {'miniprint', 'bodoque', 'two_tone'}
# G_RAYAS       = {'horizontal_stripes', 'vertical_stripes', 'diagonal_stripe', 'mariniere'}
# G_CUADROS     = {'checked', 'vichy', 'tartan', 'rhombus_fabric', 'geometric', 'prince_of_wales'}
# G_ORGANICOS   = {'floral', 'liberty', 'tropical', 'sheets', 'cachemere', 'tie_dye', 'gradient', 'tapestry'}
# G_GEOMETRICOS = {'geometric', 'retro', 'ethnic', 'rhombus_fabric', 'herringbone', 'pied_de_poule'}
# G_PUNTOS      = {'polka_dot'}
# G_AUDACES     = {'animal_print', 'camouflage', 'army'}

# def validar_par_final(p1, p2):
#     # FASE 0: FÍSICOS
#     if p1['nivel'] == 1 and p2['nivel'] == 1: return False
#     if 'oversize' in p1['fits'] and 'oversize' in p2['fits']: return False
#     # FASE 1: ESTILO
#     if p1['has_style'] and p2['has_style']:
#         s1, s2 = p1['styles'], p2['styles']
#         r1, r2 = not s1.isdisjoint(C_RELAXED), not s2.isdisjoint(C_RELAXED)
#         f1, f2 = not s1.isdisjoint(C_FORMAL), not s2.isdisjoint(C_FORMAL)
#         match = False
#         if (r1 and r2) or (f1 and f2): match = True
#         elif not s1.isdisjoint(C_BOHO) and not s2.isdisjoint(C_BOHO): match = True
#         elif not s1.isdisjoint(C_PARTY) and not s2.isdisjoint(C_PARTY): match = True
#         else:
#             if (r1 and f2) or (r2 and f1): match = True
#             elif (not s1.isdisjoint(C_BOHO) and r2) or (not s2.isdisjoint(C_BOHO) and r1): match = True
#             p1p, p2p = not s1.isdisjoint(C_PARTY), not s2.isdisjoint(C_PARTY)
#             if (p1p and (f2 or r2)) or (p2p and (f1 or r1)): match = True
#         if not match: return False

#     # FASE 2: PRINTS
#     if p1['is_print'] and p2['is_print']:
#         pr1, pr2 = p1['prints'], p2['prints']
#         es_liso_1 = pr1.isdisjoint(G_LISO)
#         es_liso_2 = pr2.isdisjoint(G_LISO)
#         # ---- 1) LISO + ESTAMPADO → siempre combina ----
#         if not p1['is_print'] or not p2['is_print']:
#             pass  
#         # ---- 2) CUADROS + CUADROS → depende del color (lo validará fase 3) ----
#         elif (not pr1.isdisjoint(G_CUADROS)) and (not pr2.isdisjoint(G_CUADROS)):
#             pass  
#         # ---- 3) ANIMAL + GEOMÉTRICO → mismo tono ----
#         elif ((not pr1.isdisjoint(G_AUDACES) and not pr2.isdisjoint(G_GEOMETRICOS)) or
#             (not pr2.isdisjoint(G_AUDACES) and not pr1.isdisjoint(G_GEOMETRICOS))):
#             if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0:
#                 return False
#         # ---- 4) FLORES + RAYAS → mismo tono ----
#         elif ((not pr1.isdisjoint(G_ORGANICOS) and not pr2.isdisjoint(G_RAYAS)) or
#             (not pr2.isdisjoint(G_ORGANICOS) and not pr1.isdisjoint(G_RAYAS))):
#             if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0:
#                 return False
#         # ---- 5) RAYAS + TOPOS → mismo tono ----
#         elif ((not pr1.isdisjoint(G_PUNTOS) and not pr2.isdisjoint(G_RAYAS)) or
#             (not pr2.isdisjoint(G_PUNTOS) and not pr1.isdisjoint(G_RAYAS))):
#             if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0:
#                 return False
#         else:
#             return False

#     # FASE 3: COLOR
#     c1, c2 = p1['color_nivel'], p2['color_nivel']
#     if c1 in (0, 2, 4) or c2 in (0, 2, 4): return True # Colores neutros/comodín
    
#     h1, i1 = divmod(c1, 10)
#     h2, i2 = divmod(c2, 10)
    
#     dist = min(abs(h1 - h2), 12 - abs(h1 - h2))
    
#     if dist == 0: return abs(i1 - i2) >= 2 # Mismo tono, diferente intensidad
#     if dist in (1, 4, 6): return True # Análogos, Tríada, Complementario
    
#     return False

# ==============================================================================
# 1. CONSTANTES (Sin cambios)
# ==============================================================================
# MISMAS CONSTANTES DE SIEMPRE
C_RELAXED = {'casual', 'street', 'freetime'}
C_FORMAL = {'classic', 'minimal', 'work', 'working_girl'}
C_BOHO = {'boho'}
C_PARTY = {'night', 'special_occasion'}

G_LISO = {'smooth', 'solid', 'liso'}
G_MICRO = {'miniprint', 'bodoque', 'two_tone'}
G_RAYAS = {'horizontal_stripes', 'vertical_stripes', 'diagonal_stripe', 'mariniere'}
G_CUADROS = {'checked', 'vichy', 'tartan', 'rhombus_fabric', 'geometric', 'prince_of_wales'}
G_ORGANICOS = {'floral', 'liberty', 'tropical', 'sheets', 'cachemere', 'tie_dye', 'gradient', 'tapestry'}
G_GEOMETRICOS = {'geometric', 'retro', 'ethnic', 'rhombus_fabric', 'herringbone', 'pied_de_poule'}
G_PUNTOS = {'polka_dot'}
G_AUDACES = {'animal_print', 'camouflage', 'army'}
GR_ARRIBA = {'camiseta', 'jersey', 't-shirt', 'top', 'blusa', 'camisa', 'sudadera'}
GR_ABAJO  = {'pantalones', 'falda', 'jeans', 'shorts', 'leggings'}
GR_ENTERO = {'vestido', 'mono', 'mono_corto'}
GR_CAPAS  = {'chaqueta', 'abrigo', 'cazadora', 'blazer', 'cardigan'}

def validar_par_final(p1, p2):
    #FASE 1: MEDIDAS
    c1 = p1.get('sub_category')
    c2 = p2.get('sub_category')
    if c1 == c2: 
        return False
    if c1 in GR_ABAJO and c2 in GR_ABAJO: return False
    if c1 in GR_ENTERO and c2 in GR_ENTERO: return False
    if c1 in GR_CAPAS and c2 in GR_CAPAS: return False
    es_entero_1 = c1 in GR_ENTERO
    es_entero_2 = c2 in GR_ENTERO
    es_suelta_1 = (c1 in GR_ARRIBA) or (c1 in GR_ABAJO)
    es_suelta_2 = (c2 in GR_ARRIBA) or (c2 in GR_ABAJO)
    if (es_entero_1 and es_suelta_2) or (es_entero_2 and es_suelta_1):
        return False
    l1 = p1.get('long_cm')
    sl1 = p1.get('sleeve_long_cm')
    l2 = p2.get('long_cm')
    sl2 = p2.get('sleeve_long_cm')
    is_cam_1 = c1 in {'camiseta', 'top', 't-shirt', 'blusa', 'camisa'}
    is_jer_2 = c2 in {'jersey', 'sudadera'}
    is_cam_2 = c2 in {'camiseta', 'top', 't-shirt', 'blusa', 'camisa'}
    is_jer_1 = c1 in {'jersey', 'sudadera'}
    if is_cam_1 and is_jer_2:
        if l1 and l2 and l1 > l2: return False
        if sl1 and sl2 and sl1 > sl2: return False
    elif is_cam_2 and is_jer_1:
        if l2 and l1 and l2 > l1: return False
        if sl2 and sl1 and sl2 > sl1: return False
    es_interior_1 = (c1 in GR_ARRIBA) 
    es_capa_2     = (c2 in GR_CAPAS)
    es_interior_2 = (c2 in GR_ARRIBA)
    es_capa_1     = (c1 in GR_CAPAS)
    if es_interior_1 and es_capa_2:
        if l1 and l2 and l1 > l2: return False
        if sl1 and sl2 and sl1 > sl2: return False
    elif es_interior_2 and es_capa_1:
        if l2 and l1 and l2 > l1: return False
        if sl2 and sl1 and sl2 > sl1: return False

    # FASE 2: FÍSICOS
    if p1.get('nivel') == 1 and p2.get('nivel') == 1: return False
    if 'oversize' in p1.get('fits', []) and 'oversize' in p2.get('fits', []): return False

    # FASE 3: ESTILO
    if p1.get('has_style') and p2.get('has_style'):
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

    # FASE 4: PRINTS
    c_val1 = p1.get('color_nivel', 0)
    c_val2 = p2.get('color_nivel', 0)
    h1, i1 = divmod(c_val1, 10)
    h2, i2 = divmod(c_val2, 10)
    if p1.get('is_print') and p2.get('is_print'):
        pr1, pr2 = p1['prints'], p2['prints']
        if not p1['is_print'] or not p2['is_print']: pass
        elif (not pr1.isdisjoint(G_CUADROS)) and (not pr2.isdisjoint(G_CUADROS)): pass
        elif ((not pr1.isdisjoint(G_AUDACES) and not pr2.isdisjoint(G_GEOMETRICOS)) or
              (not pr2.isdisjoint(G_AUDACES) and not pr1.isdisjoint(G_GEOMETRICOS))):
            if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0: return False
        elif ((not pr1.isdisjoint(G_ORGANICOS) and not pr2.isdisjoint(G_RAYAS)) or
              (not pr2.isdisjoint(G_ORGANICOS) and not pr1.isdisjoint(G_RAYAS))):
            if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0: return False
        elif ((not pr1.isdisjoint(G_PUNTOS) and not pr2.isdisjoint(G_RAYAS)) or
              (not pr2.isdisjoint(G_PUNTOS) and not pr1.isdisjoint(G_RAYAS))):
            if min(abs(h1 - h2), 12 - abs(h1 - h2)) != 0: return False
        else:
            return False

    # FASE 5: COLOR
    if c_val1 in (0, 2, 4) or c_val2 in (0, 2, 4): return True
    dist = min(abs(h1 - h2), 12 - abs(h1 - h2))
    if dist == 0: return abs(i1 - i2) >= 2
    if dist in (1, 4, 6): return True
    return False


def calcular_peso_outfit(p1, p2):
    """
    Retorna:
      - None: Si la combinación es IMPOSIBLE (Rompe reglas Fase 1 o 2).
      - Float (0.1 a 1.0): Si es posible, indicando la calidad estética.
    """
    
    # ==========================================
    # FASE 1 & 2: VETO (HARD RULES)
    # Si entra en cualquier if, devolvemos None (No hay arista)
    # ==========================================
    
    c1, c2 = p1.get('sub_category'), p2.get('sub_category')
    
    # Reglas de bloqueo de categorías
    if c1 == c2: return None
    if c1 in GR_ABAJO and c2 in GR_ABAJO: return None
    if c1 in GR_ENTERO and c2 in GR_ENTERO: return None
    if c1 in GR_CAPAS and c2 in GR_CAPAS: return None
    
    # Lógica Entero vs Suelta
    es_entero_1 = c1 in GR_ENTERO
    es_entero_2 = c2 in GR_ENTERO
    es_suelta_1 = (c1 in GR_ARRIBA) or (c1 in GR_ABAJO)
    es_suelta_2 = (c2 in GR_ARRIBA) or (c2 in GR_ABAJO)
    if (es_entero_1 and es_suelta_2) or (es_entero_2 and es_suelta_1): return None

    # Lógica de medidas (Layering)
    l1, sl1 = p1.get('long_cm'), p1.get('sleeve_long_cm')
    l2, sl2 = p2.get('long_cm'), p2.get('sleeve_long_cm')
    
    is_cam_1 = c1 in {'camiseta', 'top', 't-shirt', 'blusa', 'camisa'}
    is_jer_2 = c2 in {'jersey', 'sudadera'}
    # (Agrega aquí el reverso: is_cam_2 y is_jer_1)
    
    if is_cam_1 and is_jer_2:
        if l1 and l2 and l1 > l2: return None # VETO: Camisa más larga que jersey
        if sl1 and sl2 and sl1 > sl2: return None # VETO: Manga camisa asoma mal
    
    # Oversize check
    if p1.get('nivel') == 1 and p2.get('nivel') == 1: return None
    if 'oversize' in p1.get('fits', []) and 'oversize' in p2.get('fits', []): return None

    # ==========================================
    # A PARTIR DE AQUÍ: ES VÁLIDO. CALCULAMOS CALIDAD (SOFT RULES)
    # ==========================================

    score_style = 0.5 
    score_print = 0.5
    score_color = 0.5

    # --- FASE 3: ESTILO ---
    s1, s2 = p1.get('styles', set()), p2.get('styles', set())
    
    r1, r2 = not s1.isdisjoint(C_RELAXED), not s2.isdisjoint(C_RELAXED)
    f1, f2 = not s1.isdisjoint(C_FORMAL), not s2.isdisjoint(C_FORMAL)
    b1, b2 = not s1.isdisjoint(C_BOHO), not s2.isdisjoint(C_BOHO)
    p1p, p2p = not s1.isdisjoint(C_PARTY), not s2.isdisjoint(C_PARTY)

    if (r1 and r2) or (f1 and f2) or (b1 and b2) or (p1p and p2p): score_style = 1.0
    elif (r1 and f2) or (r2 and f1): score_style = 0.85 
    elif (p1p and (f2 or r2)) or (p2p and (f1 or r1)): score_style = 0.8 
    elif (b1 and r2) or (b2 and r1): score_style = 0.75 
    else: score_style = 0.3 # Penalización por estilo incoherente, pero NO veto

    # --- FASE 4: PRINTS ---
    has_p1 = p1.get('is_print', False)
    has_p2 = p2.get('is_print', False)
    
    if not has_p1 and not has_p2: score_print = 1.0 
    elif has_p1 != has_p2: score_print = 0.9 
    else:
        # Lógica compleja de prints
        pr1, pr2 = p1.get('prints', set()), p2.get('prints', set())
        # ... (Tu lógica de validación de prints va aquí) ...
        # IMPORTANTE: Si tus reglas de prints eran estrictas (return False),
        # cámbialo aquí a `return None` si quieres vetar prints incompatibles.
        # Si permites prints feos pero válidos, usa score bajo.
        
        # Ejemplo asumiendo que vetamos combinaciones horribles de prints:
        mix_valido = False
        # ... logica de validacion ...
        if not mix_valido:
             # Opcion A: Vetar (No existe conexión)
             return None 
             # Opcion B: Penalizar (Existe pero score bajo)
             # score_print = 0.1 

    # --- FASE 5: COLOR ---
    c_val1, c_val2 = p1.get('color_nivel', 0), p2.get('color_nivel', 0)
    
    # Lógica de color ponderada
    if c_val1 in (0, 2, 4) or c_val2 in (0, 2, 4):
        score_color = 1.0 if (c_val1 in (0,2,4) and c_val2 in (0,2,4)) else 0.95
    else:
        h1, i1 = divmod(c_val1, 10)
        h2, i2 = divmod(c_val2, 10)
        dist = min(abs(h1 - h2), 12 - abs(h1 - h2))
        
        if dist == 0: score_color = 1.0 if abs(i1 - i2) >= 2 else 0.4
        elif dist == 6: score_color = 0.95
        elif dist in (4, 1): score_color = 0.85
        else: score_color = 0.2 # Color feo pero no prohibido

    # CALCULO FINAL
    final_weight = (score_style * 0.30) + (score_color * 0.50) + (score_print * 0.20)
    
    return round(final_weight, 4)