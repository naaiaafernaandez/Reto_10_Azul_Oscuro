import torch
import torch.nn.functional as F
import pandas as pd
import numpy as np
import random
import networkx as nx
import os
from sklearn.preprocessing import LabelEncoder
from torch_geometric.utils import from_networkx
from torch_geometric.data import Data
from torch_geometric.nn import GCNConv
from funciones import *
pd.set_option('display.max_columns', None)
pd.set_option('display.width', 1000)
os.environ['KMP_DUPLICATE_LIB_OK'] = 'True'

REGLAS_NIVEL = {'jersey': 2, 'pantalones': 1, 'jeans': 1, 'shorts': 1, 'leggings': 1,
    'camiseta': 2, 't-shirt': 2, 'top': 2, 'blusa': 2, 'camisa': 2, 'sudadera': 2,
    'vestido': 1, 'mono': 1, 'mono_corto': 1, 'falda': 1,
    'chaqueta': 3, 'abrigo': 3, 'cazadora': 3, 'blazer': 3, 'cardigan': 3,
    'bolso': 3, 'bufanda': 3}
COMBINACIONES_VALIDAS = [[1, 2, 2],[1, 2, 3],[1, 3, 3]]

MAPA_COLORES = {'red': 12, 'brick': 10, 'pale_pink': 16, 'crimson': 11, 'pink': 15, 'strawberry': 14,
    'coral': 23, 'salmon': 24,
    'ochre': 31, 'orange': 33, 'rust': 30, 'brown': 30, 'brown_light': 30, 'mandarine': 32, 'taupe': 30,
    'camel': 41, 'mustand': 40, 'beige': 46, 'nude': 45,
    'gold': 53, 'lemon': 54, 'yellow': 54, 'yellow_light': 56, 'khaki': 50, 'ecru': 51, 'sand': 51,
    'pistachio': 74, 'green_dark': 70, 'green': 71, 'green_light': 75, 'mint': 75, 'jade': 72,
    'blue_turquoise': 85, 'blue_petrol': 81, 'blue_light': 86,
    'baby_blue': 96, 'grey_blue': 95, 'blue_klein': 93, 'blue': 94,
    'blue_dark': 100,
    'indigo': 113, 'purple': 112,
    'fuchsia': 124, 'lilac': 126, 'aubergine': 120, 'wine': 121, 'garnet': 121,
    'gray_light': 2, 'grey_dark': 2, 'grey': 2, 'silver': 2, 'black': 0, 'white': 4}
VALORES_COLORES_POSIBLES = list(set(MAPA_COLORES.values()))

ESTILO_RELAJADO = {'casual', 'street', 'freetime'}
ESTILO_FORMAL = {'classic', 'minimal', 'work', 'working_girl'}
ESTILO_BOHO = {'boho'}
ESTILO_FIESTA = {'night', 'special_occasion'}
GRUPO_LISO = {'smooth', 'solid', 'liso'}
GR_ARRIBA = {'camiseta', 'jersey', 't-shirt', 'top', 'blusa', 'camisa', 'sudadera'}
GR_ABAJO  = {'pantalones', 'falda', 'jeans', 'shorts', 'leggings'}
GR_ENTERO = {'vestido', 'mono', 'mono_corto'}
GR_CAPAS  = {'chaqueta', 'abrigo', 'cazadora', 'blazer', 'cardigan'}
GR_ACCESORIOS = {'bolso', 'bufanda'}
RUTA_CARPETA = "Datos/Originales/Datos looks/"  

def cargar_csv_inteligente(nombre_archivo):
    ruta_completa = os.path.join(RUTA_CARPETA, nombre_archivo)
    print(f"Leemos: {nombre_archivo} ...", end=" ")  
    df = pd.read_csv(ruta_completa, sep=None, engine='python')
    if df.shape[1] < 2:
        df = pd.read_csv(ruta_completa, sep=';')   
    df.columns = df.columns.str.strip().str.replace('"', '').str.replace("'", "")
    print(f"OK ({df.shape[0]} filas, {df.shape[1]} cols)")
    return df

def clasificar_prenda(palabra):
    if palabra in nivel1:
        return "1"
    elif palabra in nivel2:
        return "2"
    else:
        return "3"
nivel1 = ["pant", "jeans", "jean", "skirt", "falda","short", "shorts", "dress", "jumpsuit","playsuit"]
nivel2 = ["cardigan", "sweater", "shirt", "tshirt", "t-shirt", "top",  "sweatshirt", "pullover","t-shit"]
nivel3=["jacket", "jakect", "jackect", "scarf","parka","coat","bag","foulard","trench","fular"]

def clean_medida(val):
        try:
            val = float(val)
            return val if pd.notna(val) else None
        except:
            return None    

def limpiar_atributos(atributos):
    limpio = atributos.copy()
    campos_set = ['tiempo', 'styles', 'prints', 'fits']
    for f in campos_set:
        val = limpio.get(f)
        if isinstance(val, str): limpio[f] = {val.lower()}
        elif val is None: limpio[f] = set()
        elif isinstance(val, (list, tuple)): limpio[f] = set([str(x).lower() for x in val])
    val_sub = atributos.get('sub_category')
    limpio['sub_category'] = str(val_sub).lower() if val_sub else ''
    if not limpio['prints'] or not limpio['prints'].isdisjoint(GRUPO_LISO):
        limpio['is_print'] = False
    else:
        limpio['is_print'] = True
    limpio['has_style'] = bool(limpio['styles'])
    limpio['nivel'] = int(limpio.get('nivel', 1))
    try:
        limpio['talla'] = int(float(limpio.get('talla', 0)))
    except:
        limpio['talla'] = 0

    return limpio

def calcular_peso_combinacion(p1_raw, p2_raw):
    p1, p2 = limpiar_atributos(p1_raw), limpiar_atributos(p2_raw)
    # TALLAS
    v1, v2 = p1['talla'], p2['talla']
    if not ((v1 == 100 or v2 == 100) or abs(v1 - v2) <= 1):
        return 0.0

    # Incompatibilidad de Categorías
    c1, c2 = p1.get('sub_category'), p2.get('sub_category')
    if c1 == c2: return 0.0
    if (c1 in GR_ABAJO and c2 in GR_ABAJO) or \
       (c1 in GR_ENTERO and c2 in GR_ENTERO) or \
       (c1 in GR_CAPAS and c2 in GR_CAPAS): return 0.0
    if ((c1 in GR_ENTERO) and ((c2 in GR_ARRIBA) or (c2 in GR_ABAJO))) or \
       ((c2 in GR_ENTERO) and ((c1 in GR_ARRIBA) or (c1 in GR_ABAJO))): return 0.0

    # Tiempo
    t1, t2 = p1['tiempo'], p2['tiempo']
    CALIDO, FRIO = {'warm', 'invierno'}, {'cold', 'verano'}
    if (not t1.isdisjoint(CALIDO) and not t2.isdisjoint(FRIO)) or \
       (not t1.isdisjoint(FRIO) and not t2.isdisjoint(CALIDO)): return 0.0
    score_tiempo = 1.5 if (t1 and t2) else 0.25

    # Estilo
    score_style = 0.0
    if p1['has_style'] and p2['has_style']:
        s1, s2 = p1['styles'], p2['styles']
        r1, r2 = not s1.isdisjoint(ESTILO_RELAJADO), not s2.isdisjoint(ESTILO_RELAJADO)
        f1, f2 = not s1.isdisjoint(ESTILO_FORMAL), not s2.isdisjoint(ESTILO_FORMAL)
        b1, b2 = not s1.isdisjoint(ESTILO_BOHO), not s2.isdisjoint(ESTILO_BOHO)
        p1p, p2p = not s1.isdisjoint(ESTILO_FIESTA), not s2.isdisjoint(ESTILO_FIESTA)
        if (r1 and r2) or (f1 and f2) or (b1 and b2) or (p1p and p2p): score_style = 2
        elif (r1 and f2) or (r2 and f1) or (p1p and (f2 or r2)) or (p2p and (f1 or r1)): score_style = 3

    score_color, score_print = 1.0, 0.7
    peso_final = score_tiempo + score_style + score_color + score_print
    return round(min(peso_final / 8.0, 1.0), 4)

# 3. UTILIDADES DE GENERACIÓN Y BÚSQUEDA
def obtener_mapeadores(grafo):
    datos_nodos = list(grafo.nodes(data=True))
    todas_claves = set()
    for _, d in datos_nodos:
        todas_claves.update(d.keys())
    mapeadores = {'num': {}, 'cat': {}}
    for k in todas_claves:
        vals = [n[1].get(k) for n in datos_nodos if n[1].get(k) is not None]
        if not vals: continue
        if isinstance(vals[0], (int, float)) and not isinstance(vals[0], bool):
             mapeadores['num'][k] = {'min': min(vals), 'max': max(vals)}
        else:
             encoder = LabelEncoder()
             vals_str = [str(v) for v in vals]
             encoder.fit(vals_str)
             mapeadores['cat'][k] = encoder
    return mapeadores


import pandas as pd
import joblib
import re
import numpy as np
def simular_match(df_users,df_products,user_id, product_id):
    artifacts = joblib.load('Modelos/modelo_Stacking.pkl')
    model = artifacts['model']
    encoder = artifacts['encoder']
    imputer = artifacts['imputer']
    model_features = artifacts['features']
    train_num_cols = artifacts['num_cols']
    train_cat_cols = artifacts['cat_cols']
    threshold = artifacts.get('threshold', 0.5)
    u_data = df_users[df_users['user_id'] == user_id].copy()
    p_data = df_products[df_products['product_variant_id'] == product_id].copy()
    row = pd.concat([u_data.reset_index(drop=True), p_data.reset_index(drop=True)], axis=1)
    
    row['month'] = pd.Timestamp.now().month
    mapa_precios = {'30-60': 45, '60-100': 80, '100+': 140}
    if 'prices' in row.columns:
        user_budget = row['prices'].map(mapa_precios).fillna(45)
        row['price_divergence'] = (row['current_price_eur'] - user_budget) / user_budget
        row['price_divergence'] = row['price_divergence'].fillna(0)
    else:
        row['price_divergence'] = 0
    row.columns = [re.sub(r'[^\w]', '_', col) for col in row.columns]
    input_row = pd.DataFrame(columns=model_features)
    for col in model_features:
        if col in row.columns:
            input_row.loc[0, col] = row[col].iloc[0]
        else:
            input_row.loc[0, col] = np.nan
    cols_to_impute = [c for c in train_num_cols if c in input_row.columns]
    if cols_to_impute:
        input_row[cols_to_impute] = input_row[cols_to_impute].astype(float)
        input_row[cols_to_impute] = imputer.transform(input_row[cols_to_impute])
    cols_to_encode = [c for c in train_cat_cols if c in input_row.columns]
    if cols_to_encode:
        input_row[cols_to_encode] = input_row[cols_to_encode].astype(object)
        input_row[cols_to_encode] = input_row[cols_to_encode].fillna("Unknown").astype(str)
        input_row[cols_to_encode] = encoder.transform(input_row[cols_to_encode])
    input_row = input_row[model_features]
    prob = model.predict_proba(input_row)[0][1]
    decision = "❤️ LIKE" if prob >= threshold else "❌ DISLIKE"
    print(f"SIMULADOR")
    print(f"User: {user_id}")
    print(f"Prod: {product_id}")
    print(f"{'-'*50}")
    print(f"Probabilidad: {prob*100:.2f}%")
    print(f"Resultado:    {decision}")

def simular_prenda(mapeadores, num_caracteristicas):
    datos_legibles, caracteristicas_generadas = {}, []
    print("\n--- FICHA TECNICA DEL NUEVO PRODUCTO (Simulado) ---")
    if 'sub_category' in mapeadores['cat']:
        encoder_sub = mapeadores['cat']['sub_category']
        sub_cat_elegida = random.choice(encoder_sub.classes_)
    else:
        sub_cat_elegida = 'camiseta'
    nivel_fijo = REGLAS_NIVEL.get(sub_cat_elegida.lower(), 2)
    todas_claves = list(mapeadores['num'].keys()) + list(mapeadores['cat'].keys())
    todas_claves.sort()
    for key in todas_claves:

        # Color
        if key == 'color_nivel':
            val_elegido = random.choice(VALORES_COLORES_POSIBLES)
            nombre_visual = next((k for k, v in MAPA_COLORES.items() if v == val_elegido), "Personalizado")
            datos_legibles[key] = val_elegido
            caracteristicas_generadas.append(float(val_elegido))
            print(f"  COLOR: {nombre_visual.upper()} (ID: {val_elegido})")
            continue
        if key == 'sub_category':
            datos_legibles[key] = sub_cat_elegida
            val_enc = mapeadores['cat'][key].transform([sub_cat_elegida])[0]
            caracteristicas_generadas.append(float(val_enc))
            print(f"  {key.capitalize()}: {sub_cat_elegida}")
        elif key == 'nivel':
            datos_legibles[key] = nivel_fijo
            caracteristicas_generadas.append(float(nivel_fijo))
        elif key in mapeadores['num']:
            limites = mapeadores['num'][key]
            val_real = random.randint(int(limites['min']), int(limites['max']))
            datos_legibles[key] = val_real
            caracteristicas_generadas.append(float(val_real))
            if key == 'talla':
                print(f"  Talla: {val_real}")
        elif key in mapeadores['cat']:
            encoder = mapeadores['cat'][key]
            opcion = random.choice(encoder.classes_)
            datos_legibles[key] = opcion
            val_enc = encoder.transform([opcion])[0]
            caracteristicas_generadas.append(float(val_enc))
            print(f"  {key.capitalize()}: {opcion}")
    print(f"  Nivel Asignado: {nivel_fijo} (Por ser {sub_cat_elegida})")

    tensor_x = torch.tensor([caracteristicas_generadas], dtype=torch.float)
    if tensor_x.shape[1] != num_caracteristicas:
        if tensor_x.shape[1] < num_caracteristicas:
            relleno = torch.zeros((1, num_caracteristicas - tensor_x.shape[1]))
            tensor_x = torch.cat([tensor_x, relleno], dim=1)
        else:
            tensor_x = tensor_x[:, :num_caracteristicas]
    return tensor_x, datos_legibles

@torch.no_grad()
def buscar_coincidencia(modelo, datos, grafo, mapeadores):
    modelo.eval()
    dispositivo = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    # 1. Genera la prenda nueva
    tensor_nuevo, info_nueva = simular_prenda(mapeadores, datos.num_features)
    cat_objetivo = str(info_nueva.get('sub_category', '')).lower()
    try:
        nivel_objetivo = int(info_nueva.get('nivel', 2))
    except:
        nivel_objetivo = 2
    try:
        talla_objetivo = int(float(info_nueva.get('talla', 0)))
    except:
        talla_objetivo = 0
    color_raw = info_nueva.get('color') if 'color' in info_nueva else info_nueva.get('color_nivel', 0)
    color_objetivo = int(float(color_raw))
    if not cat_objetivo:
        return pd.DataFrame(), None

    # 2. Embeddings y similitud
    indice_aristas_dummy = torch.tensor([[],[]], dtype=torch.long).to(dispositivo)
    z_nuevo = modelo.encode(tensor_nuevo.to(dispositivo), indice_aristas_dummy)
    z_existente = modelo.encode(datos.x.to(dispositivo), datos.edge_index.to(dispositivo))
    similitudes = F.cosine_similarity(z_nuevo, z_existente)
    valores_ordenados, indices_ordenados = torch.sort(similitudes, descending=True)
    gemelo_exacto = None
    gemelo_reserva = None
    lista_nodos = list(grafo.nodes(data=True))

    # Definimos la regla de colores si no es la misma
    decena_objetivo = (color_objetivo // 10) * 10
    familia_colores = set([decena_objetivo + i for i in range(7)])
    print(f"\nBuscando COINCIDENCIA para {cat_objetivo.upper()}:")
    print(f"   Requisitos: Nivel {nivel_objetivo} | Talla {talla_objetivo} (±1)")
    print(f"   Color Objetivo: {color_objetivo} (Exacto) | Plan B: {decena_objetivo}-{decena_objetivo+6}")

    # 3. Busqueda
    for i in range(len(indices_ordenados)):
        idx = indices_ordenados[i].item()
        candidato = lista_nodos[idx]
        atributos = candidato[1]
        cat_candidato = str(atributos.get('sub_category', '')).lower()

        # FILTRO 0: EXCLUSIÓN CAPAS vs ACCESORIOS
        if (cat_objetivo in GR_CAPAS) and (cat_candidato in GR_ACCESORIOS):
            continue
        if (cat_objetivo in GR_ACCESORIOS) and (cat_candidato in GR_CAPAS):
            continue

        # FILTRO 1: NIVEL
        if int(atributos.get('nivel', 2)) != nivel_objetivo:
            continue

        # FILTRO 2: TALLA
        try:
            talla_candidato = int(float(atributos.get('talla', 0)))
        except:
            talla_candidato = 0
        dif_talla = abs(talla_objetivo - talla_candidato)
        talla_valida = (dif_talla <= 1) or (talla_objetivo == 100) or (talla_candidato == 100)
        if not talla_valida:
            continue

        # FILTRO 3: COLOR
        val_cand_raw = atributos.get('color') if atributos.get('color') is not None else atributos.get('color_nivel')
        if isinstance(val_cand_raw, str):
            val_candidato = MAPA_COLORES.get(val_cand_raw.lower(), -999)
        elif val_cand_raw is None:
            val_candidato = -999
        else:
            val_candidato = int(float(val_cand_raw))

        # CASO 1: Color Exacto
        if val_candidato == color_objetivo:
            gemelo_exacto = candidato
            print(f"   Encontrado Color Exacto en la posicion #{i}!")
            break

        # CASO 2: Color cercano
        if gemelo_reserva is None and (val_candidato in familia_colores):
            gemelo_reserva = candidato

    # 4. Selección
    gemelo_final = None
    tipo_match = ""
    if gemelo_exacto is not None:
        gemelo_final = gemelo_exacto
        tipo_match = "EXACTO"
    elif gemelo_reserva is not None:
        gemelo_final = gemelo_reserva
        tipo_match = "APROXIMADO (Familia - Reserva)"

    # 5. Resultados
    if gemelo_final:
        attrs_final = gemelo_final[1]
        val_color_fin = attrs_final.get('color') if attrs_final.get('color') is not None else attrs_final.get('color_nivel')
        try: val_color_fin = int(float(val_color_fin))
        except: val_color_fin = -999
        nombre_visual = next((k for k, v in MAPA_COLORES.items() if v == val_color_fin), str(val_color_fin))

        print("\n--- MATCH SELECCIONADO ---")
        print(f"   Simulada -> {cat_objetivo} | Talla {talla_objetivo} | Color {color_objetivo}")
        print(f"   Predicha -> {attrs_final.get('sub_category')} | Talla {attrs_final.get('talla')} | Color {nombre_visual} (ID {val_color_fin})")
        print(f"   Tipo de Match: {tipo_match}")

        id_gemelo = gemelo_final[0]
        vecinos = list(grafo.neighbors(id_gemelo))
        recomendaciones = [{'ID_Recomendado': vid} for vid in vecinos if vid != id_gemelo]
        return pd.DataFrame(recomendaciones), str(id_gemelo)
    else:
        print(f"No se encontro ningun gemelo. Ni exacto ({color_objetivo}) ni familia ({decena_objetivo}-6).")
        return pd.DataFrame(), None

def obtener_id_inteligente(id_str, grafo):
    primer_nodo = list(grafo.nodes())[0]
    if isinstance(primer_nodo, int): return int(id_str)
    return str(id_str)

# 4. Recomendador
def recomendador(modelo, datos, grafo):
    print("--- INICIANDO MOTOR DE RECOMENDACION ---")
    mis_mapeadores = obtener_mapeadores(grafo)
    df_resultados, id_gemelo_str = buscar_coincidencia(modelo, datos, grafo, mis_mapeadores)

    if df_resultados.empty or id_gemelo_str is None:
        print("No se encontro gemelo compatible. Intenta de nuevo.")
        return
    try:
        id_gemelo = obtener_id_inteligente(id_gemelo_str, grafo)
        attrs_gemelo = grafo.nodes[id_gemelo]
        nivel_gemelo = int(attrs_gemelo.get('nivel', 2))
        print(f"\nCalculando Combinaciones (Outfits)...")
        validos = []
        ids_candidatos = df_resultados['ID_Recomendado'].tolist()

        # Filtro 1: Similar -> Candidato
        for cid in ids_candidatos:
            try:
                attrs_c = grafo.nodes[cid]
                peso = calcular_peso_combinacion(attrs_gemelo, attrs_c)
                if peso > 0: validos.append({'id': cid, 'attrs': attrs_c, 'w': peso})
            except KeyError: continue
        looks_finales = []

        # Filtro 2: Triángulos
        for i in range(len(validos)):
            for j in range(i+1, len(validos)):
                cA, cB = validos[i], validos[j]
                if grafo.has_edge(cA['id'], cB['id']):
                    nivel_A = int(cA['attrs'].get('nivel', 2))
                    nivel_B = int(cB['attrs'].get('nivel', 2))
                    niveles_triangulo = sorted([nivel_gemelo, nivel_A, nivel_B])
                    if niveles_triangulo not in COMBINACIONES_VALIDAS:
                        continue
                    peso_AB = calcular_peso_combinacion(cA['attrs'], cB['attrs'])
                    if peso_AB > 0:
                        score_total = (cA['w'] + cB['w'] + peso_AB) / 3
                        datos_look = {'Puntuacion': score_total,
                            'Niveles': str(niveles_triangulo),'P1_Sub': cA['attrs'].get('sub_category'),
                            'P2_Sub': cB['attrs'].get('sub_category'),'IDs_Ref': f"{cA['id']} + {cB['id']}",
                            'P1_ID': cA['id'], 'P2_ID': cB['id']}
                        for k, v in cA['attrs'].items(): datos_look[f"P1_{k}"] = v
                        for k, v in cB['attrs'].items(): datos_look[f"P2_{k}"] = v
                        looks_finales.append(datos_look)

        if looks_finales:
            df_final = pd.DataFrame(looks_finales).sort_values(by='Puntuacion', ascending=False).head(5)
            print("\n--- MEJORES LOOKS VALIDADOS ---")
            cols_interes = ['Puntuacion','IDs_Ref','P1_talla','P1_nivel','P1_sub_category','P1_color_nivel','P1_tiempo','P1_styles','P1_prints','P1_fits',
                            'P2_talla','P2_nivel','P2_sub_category','P2_color_nivel','P2_tiempo','P2_styles','P2_prints','P2_fits']
            cols_existentes = [c for c in cols_interes if c in df_final.columns]
            print(df_final[cols_existentes].to_string(index=False))
        else:
            print("\nSe encontraron conexiones, pero ninguna cumplia todas las reglas.")
    except KeyError as e:
        print(f"\nError de ID: {e}.")