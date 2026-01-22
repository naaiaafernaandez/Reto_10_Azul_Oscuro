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

def calcular_peso_outfit(p1, p2):
    # =========================================================
    # FASE 1-4: FILTROS TÉCNICOS (IDÉNTICOS A TU VALIDACIÓN)
    # =========================================================
    t1, t2 = p1.get('tiempo', set()), p2.get('tiempo', set())
    WARM_TAGS = {'warm'}
    COLD_TAGS = {'cold'}
    is_warm1, is_cold1 = not t1.isdisjoint(WARM_TAGS), not t1.isdisjoint(COLD_TAGS)
    is_warm2, is_cold2 = not t2.isdisjoint(WARM_TAGS), not t2.isdisjoint(COLD_TAGS)
    if (is_warm1 and is_cold2) or (is_cold1 and is_warm2):
        return 0.0
    if t1 and t2:
        score_tiempo = 1.5 #Cold+cold o warm+warm
    elif t1 or t2:
        score_tiempo = 0.75 #Cold+nan o warm+nan
    else:
        score_tiempo = 0.25 #nan+nan

    v1, v2 = p1.get('talla', 0), p2.get('talla', 0)
    if not ((v1 == 100 or v2 == 100) or abs(v1 - v2) <= 1): return 0.0

    c1, c2 = p1.get('sub_category'), p2.get('sub_category')
    if c1 == c2: return 0.0
    if (c1 in GR_ABAJO and c2 in GR_ABAJO) or \
       (c1 in GR_ENTERO and c2 in GR_ENTERO) or \
       (c1 in GR_CAPAS and c2 in GR_CAPAS): return 0.0
    
    if ((c1 in GR_ENTERO) and ((c2 in GR_ARRIBA) or (c2 in GR_ABAJO))) or \
       ((c2 in GR_ENTERO) and ((c1 in GR_ARRIBA) or (c1 in GR_ABAJO))): return 0.0

    # Largos y niveles
    l1, sl1, l2, sl2 = p1.get('long_cm'), p1.get('sleeve_long_cm'), p2.get('long_cm'), p2.get('sleeve_long_cm')
    is_cam_1, is_jer_2 = c1 in {'camiseta', 'top', 't-shirt', 'blusa', 'camisa'}, c2 in {'jersey', 'sudadera'}
    is_cam_2, is_jer_1 = c2 in {'camiseta', 'top', 't-shirt', 'blusa', 'camisa'}, c1 in {'jersey', 'sudadera'}
    
    if is_cam_1 and is_jer_2:
        if (l1 and l2 and l1 > l2) or (sl1 and sl2 and sl1 > sl2): return 0.0
    elif is_cam_2 and is_jer_1:
        if (l2 and l1 and l2 > l1) or (sl2 and sl1 and sl2 > sl1): return 0.0

    if p1.get('nivel') == 1 and p2.get('nivel') == 1: return 0.0
    if 'oversize' in p1.get('fits', []) and 'oversize' in p2.get('fits', []): return 0.0

    # =========================================================
    # FASE 5: ESTILO (FILTRO ESTRICTO)
    # =========================================================
    score_style = 0.0
    if p1.get('has_style') and p2.get('has_style'):
        s1, s2 = p1['styles'], p2['styles']
        r1, r2 = not s1.isdisjoint(C_RELAXED), not s2.isdisjoint(C_RELAXED)
        f1, f2 = not s1.isdisjoint(C_FORMAL), not s2.isdisjoint(C_FORMAL)
        b1, b2 = not s1.isdisjoint(C_BOHO), not s2.isdisjoint(C_BOHO)
        p1p, p2p = not s1.isdisjoint(C_PARTY), not s2.isdisjoint(C_PARTY)
        
        match = False
        if (r1 and r2) or (f1 and f2) or (b1 and b2) or (p1p and p2p):
            match = True
            score_style = 2
        elif (r1 and f2) or (r2 and f1) or (p1p and (f2 or r2)) or (p2p and (f1 or r1)):
            match = True
            score_style = 3
        if not match: return 0.0
    else:
        score_style = 0.0
    # =========================================================
    # FASE 6: PRINTS (FILTRO ESTRICTO)
    # =========================================================
    c_val1, c_val2 = p1.get('color_nivel', 0), p2.get('color_nivel', 0)
    h1, i1 = divmod(c_val1, 10)
    h2, i2 = divmod(c_val2, 10)
    has_p1, has_p2 = p1['is_print'], p2['is_print']
    score_print = 0.0
    if has_p1 and has_p2:
        pr1, pr2 = p1['prints'], p2['prints']
        es_liso_1, es_liso_2 = pr1.isdisjoint(G_LISO), pr2.isdisjoint(G_LISO)
        print_match = False
        if es_liso_1 or es_liso_2: 
            print_match = True
            score_print = 1.5
        elif not pr1.isdisjoint(G_CUADROS) and not pr2.isdisjoint(G_CUADROS):
            print_match = True
            score_print = 2
        else:
            dist_h = min(abs(h1 - h2), 12 - abs(h1 - h2))
            if dist_h == 0:
                if (not pr1.isdisjoint(G_AUDACES) and not pr2.isdisjoint(G_GEOMETRICOS)) or \
                   (not pr1.isdisjoint(G_ORGANICOS) and not pr2.isdisjoint(G_RAYAS)) or \
                   (not pr1.isdisjoint(G_PUNTOS) and not pr2.isdisjoint(G_RAYAS)):
                    print_match = True
                    score_print = 3
        if not print_match: return 0.0 
    else:
        if not has_p1 and not has_p2:
            score_print = 0.5 
        else:
            score_print = 0.7

    # =========================================================
    # FASE 7: COLOR (FILTRO ESTRICTO)
    # =========================================================
    score_color = 0.0
    is_n1, is_n2 = c_val1 in (0, 2, 4), c_val2 in (0, 2, 4)
    if is_n1 or is_n2:
        score_color = 1 if (is_n1 and is_n2) else 1.5
    else:
        dist = min(abs(h1 - h2), 12 - abs(h1 - h2))
        if dist == 0:
            if abs(i1 - i2) >= 2: score_color = 3
            else: return 0.0 
        elif dist == 1:
            score_color = 4
        elif dist in (4,6):
            score_color = 5
        else:
            return 0.0

    final_weight = score_tiempo+score_style + score_color + score_print
    peso_norm = final_weight/12.5
    return round(min(peso_norm, 1.0), 4)
