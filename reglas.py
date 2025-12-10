
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