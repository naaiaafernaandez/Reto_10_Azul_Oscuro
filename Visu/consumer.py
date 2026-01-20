from confluent_kafka import Consumer
import json
import time
import os
import torch
import networkx as nx
import numpy as np
import pandas as pd
from torch_geometric.nn import GCNConv
from torch_geometric.utils import from_networkx
import torch.nn.functional as F
from sklearn.preprocessing import LabelEncoder, MinMaxScaler

# ==========================================
# 1. CONFIGURACIÓN
# ==========================================
TOPIC_NAME = 'solicitud_look'
CONF_KAFKA = {
    'bootstrap.servers': 'localhost:9092',
    'group.id': 'lookiero_ai_fixed_level3_v14',
    'auto.offset.reset': 'latest'
}

PATH_GRAFO = "grafo_prendas.gexf"
PATH_MODELO = "modelo_gnn_1000.pth"
PATH_RESULTADO = "static/resultado_ia.json"

# ==========================================
# 2. DEFINICIONES DE NEGOCIO
# ==========================================
REGLAS_NIVEL = {
    'pantalones': 1, 'jeans': 1, 'shorts': 1, 'leggings': 1, 'falda': 1,
    'vestido': 1, 'mono': 1, 'mono_corto': 1,
    'camiseta': 2, 't-shirt': 2, 'top': 2, 'blusa': 2, 'camisa': 2, 'sudadera': 2,
    'jersey': 3, 'bolso': 3, 'bufanda': 3,
    'chaqueta': 3, 'abrigo': 3, 'cazadora': 3, 'blazer': 3, 'cardigan': 3
}

GR_ARRIBA = {'camiseta', 'jersey', 't-shirt', 'top', 'blusa', 'camisa', 'sudadera'}
GR_ABAJO  = {'pantalones', 'falda', 'jeans', 'shorts', 'leggings'}
GR_ENTERO = {'vestido', 'mono', 'mono_corto'}
GR_CAPAS  = {'chaqueta', 'abrigo', 'cazadora', 'blazer', 'cardigan', 'jersey'}
GR_ACCESORIOS = {'bolso', 'bufanda'}
GRUPO_LISO = {'smooth', 'solid', 'liso'}

COMBINACIONES_VALIDAS = [[1, 2, 2], [1, 2, 3], [1, 3, 3]]

MAPA_COLORES = {
    'red': 12, 'brick': 10, 'pale_pink': 16, 'crimson': 11, 'pink': 15, 'strawberry': 14,
    'coral': 23, 'salmon': 24, 'ochre': 31, 'orange': 33, 'rust': 30, 'brown': 30, 'brown_light': 30,
    'mandarine': 32, 'taupe': 30, 'camel': 41, 'mustand': 40, 'beige': 46, 'nude': 45,
    'gold': 53, 'lemon': 54, 'yellow': 54, 'yellow_light': 56, 'khaki': 50, 'ecru': 51, 'sand': 51,
    'pistachio': 74, 'green_dark': 70, 'green': 71, 'green_light': 75, 'mint': 75, 'jade': 72,
    'blue_turquoise': 85, 'blue_petrol': 81, 'blue_light': 86, 'baby_blue': 96, 'grey_blue': 95,
    'blue_klein': 93, 'blue': 94, 'blue_dark': 100, 'indigo': 113, 'purple': 112,
    'fuchsia': 124, 'lilac': 126, 'aubergine': 120, 'wine': 121, 'garnet': 121,
    'gray_light': 2, 'grey_dark': 2, 'grey': 2, 'silver': 2, 'black': 0, 'white': 4
}
ID_A_COLOR = {int(v): k.upper().replace("_", " ") for k, v in MAPA_COLORES.items()}

# DICCIONARIO DE TALLAS
ID_A_TALLA = {
    1: 'XS', 2: 'S', 3: 'M', 4: 'L', 5: 'XL', 
    6: 'XXL', 7: 'XXXL', 8: 'X4XL', 100: 'UNQ', 0: 'UNQ'
}

# ==========================================
# 3. MODELO GNN
# ==========================================
class Net(torch.nn.Module):
    def __init__(self, in_channels, hidden_channels, out_channels):
        super().__init__()
        self.conv1 = GCNConv(in_channels, hidden_channels)
        self.conv2 = GCNConv(hidden_channels, out_channels)
    def encode(self, x, edge_index):
        x = self.conv1(x, edge_index).relu()
        x = self.conv2(x, edge_index)
        return x

# ==========================================
# 4. CARGA DE RECURSOS
# ==========================================
print("⚙️ Cargando Grafo y Modelo...")
if not os.path.exists(PATH_GRAFO): raise FileNotFoundError(f"Falta {PATH_GRAFO}")
grafo = nx.read_gexf(PATH_GRAFO)
print("✅ Grafo cargado.")

nodes_data = list(grafo.nodes(data=True))
mapeadores = {'num': {}, 'cat': {}}
all_features = []
todas_claves = sorted(['color_nivel', 'fits', 'nivel', 'prints', 'styles', 'sub_category', 'talla', 'tiempo'])

for key in todas_claves:
    raw_values = [str(n[1].get(key, '')) for n in nodes_data]
    if key in ['nivel', 'color_nivel', 'talla']:
        float_vals = []
        for v in raw_values:
            try: float_vals.append(float(v))
            except: float_vals.append(0.0)
        col_values = np.array(float_vals).reshape(-1, 1)
        scaler = MinMaxScaler()
        col_values = scaler.fit_transform(col_values)
        mapeadores['num'][key] = scaler
        all_features.append(col_values)
    else:
        encoder = LabelEncoder()
        col_values = encoder.fit_transform(raw_values)
        mapeadores['cat'][key] = encoder
        col_values = col_values.reshape(-1, 1)
        all_features.append(col_values)

features_combined = np.hstack(all_features)
data_grafo = from_networkx(grafo)
data_grafo.x = torch.tensor(features_combined, dtype=torch.float)

device = torch.device('cpu')
model = Net(in_channels=data_grafo.num_features, hidden_channels=128, out_channels=64)
if os.path.exists(PATH_MODELO):
    model.load_state_dict(torch.load(PATH_MODELO, map_location=device))
    print("✅ Modelo IA cargado.")
model.eval()

# ==========================================
# 5. FUNCIONES AUXILIARES
# ==========================================

def get_color_name(val):
    try: return ID_A_COLOR.get(int(float(val)), "NEUTRO")
    except: return str(val).upper()

def get_talla_real(val_id):
    """Traduce el número (5.0) a Texto (XL)"""
    try:
        id_int = int(float(val_id))
        return ID_A_TALLA.get(id_int, "UNQ") 
    except: return "UNQ"

def clean_text_ui(valor):
    if not valor: return "-"
    s = str(valor)
    for char in ["{", "}", "[", "]", "'", '"']: s = s.replace(char, "")
    return s.title() if s.strip() else "-"

def format_node_reco(attrs):
    cat = str(attrs.get('sub_category', 'Prenda')).upper()
    color_val = attrs.get('color_nivel', attrs.get('color', 0))
    talla_val = attrs.get('talla', 0)
    
    talla_texto = get_talla_real(talla_val)
    if cat in ['BOLSO', 'BUFANDA']: talla_texto = 'UNQ'

    return {
        "category": cat,
        "color": get_color_name(color_val),
        "talla": talla_texto, 
        "fit": clean_text_ui(attrs.get('fits', attrs.get('fit', '-'))),
        "style": clean_text_ui(attrs.get('styles', attrs.get('style', '-'))),
        "print": clean_text_ui(attrs.get('prints', attrs.get('print', '-'))),
        "tiempo": clean_text_ui(attrs.get('tiempo', '-')),
        "nivel": str(int(float(attrs.get('nivel', 0))))
    }

def format_user_choice(display_data):
    cat = str(display_data.get('sub_category', 'Prenda')).upper()
    raw_talla = str(display_data.get('talla', 'U'))
    final_talla = 'UNQ' if cat in ['BOLSO', 'BUFANDA'] else raw_talla

    return {
        "category": cat,
        "color": str(display_data.get('color', 'Neutro')).upper(),
        "talla": final_talla,
        "fit": clean_text_ui(display_data.get('fit', '-')),
        "style": clean_text_ui(display_data.get('style', '-')),
        "print": clean_text_ui(display_data.get('print', '-')),
        "tiempo": clean_text_ui(display_data.get('tiempo', '-')),
        "nivel": str(display_data.get('nivel', '-'))
    }

def limpiar_atributos(atributos):
    limpio = atributos.copy()
    campos_set = ['tiempo', 'styles', 'prints', 'fits']
    for f in campos_set:
        val = limpio.get(f)
        if isinstance(val, str): limpio[f] = {val.lower()}
        elif val is None: limpio[f] = set()
        elif isinstance(val, (list, tuple)): limpio[f] = set([str(x).lower() for x in val])
    prints_set = limpio['prints']
    if isinstance(prints_set, str): prints_set = {prints_set}
    if not prints_set or not prints_set.isdisjoint(GRUPO_LISO): limpio['is_print'] = False
    else: limpio['is_print'] = True
    val_sub = atributos.get('sub_category')
    limpio['sub_category'] = str(val_sub).lower() if val_sub else ''
    limpio['has_style'] = bool(limpio['styles'])
    try: limpio['talla'] = int(float(limpio.get('talla', 0)))
    except: limpio['talla'] = 0
    return limpio

def calcular_peso_combinacion(p1_raw, p2_raw):
    p1, p2 = limpiar_atributos(p1_raw), limpiar_atributos(p2_raw)
    v1, v2 = p1['talla'], p2['talla']
    if not ((v1 == 100 or v2 == 100) or abs(v1 - v2) <= 1): return 0.0
    c1, c2 = p1.get('sub_category'), p2.get('sub_category')
    if c1 == c2: return 0.0
    if (c1 in GR_ABAJO and c2 in GR_ABAJO) or \
       (c1 in GR_ENTERO and c2 in GR_ENTERO) or \
       (c1 in GR_CAPAS and c2 in GR_CAPAS): return 0.0
    score_tiempo = 1.0 
    score_style = 0.5
    if p1['has_style'] and p2['has_style']:
        s1, s2 = p1['styles'], p2['styles']
        if not s1.isdisjoint(s2): score_style = 2.0 
    return round(score_style + score_tiempo, 2)

# ==========================================
# 6. LÓGICA PRINCIPAL
# ==========================================

def procesar_solicitud(display, gcn_in):
    # 1. User Choice
    user_item_final = format_user_choice(display)

    # 2. Vectorizar
    features = []
    input_data = {
        'sub_category': str(display.get('sub_category', 'camiseta')).lower(),
        'nivel': float(gcn_in.get('nivel_id', 2)),
        'color_nivel': float(gcn_in.get('color_id', 0)),
        'talla': float(gcn_in.get('talla_id', 0)),
        'tiempo': str(display.get('tiempo', 'warm')),
        'styles': str(display.get('style', 'casual')),
        'prints': str(display.get('print', 'smooth')),
        'fits': str(display.get('fit', 'regular'))
    }
    
    for key in todas_claves:
        val = input_data.get(key)
        if key in mapeadores['num']:
            feat = mapeadores['num'][key].transform([[val]])[0][0]
        else:
            enc = mapeadores['cat'][key]
            val_str = str(val)
            feat = enc.transform([val_str])[0] if val_str in enc.classes_ else 0
        features.append(feat)
    
    tensor_nuevo = torch.tensor([features], dtype=torch.float)
    
    # 3. Buscar Gemelo
    dummy_edge = torch.tensor([[],[]], dtype=torch.long)
    z_nuevo = model.encode(tensor_nuevo, dummy_edge)
    z_existente = model.encode(data_grafo.x, data_grafo.edge_index)
    similitudes = F.cosine_similarity(z_nuevo, z_existente)
    _, indices_ordenados = torch.sort(similitudes, descending=True)
    
    cat_objetivo = input_data['sub_category']
    # IGNORAMOS el nivel objetivo en la búsqueda para evitar conflictos (User:3 vs Grafo:2)
    talla_objetivo = int(input_data['talla'])
    color_objetivo = int(input_data['color_nivel'])
    familia_colores = set([(color_objetivo // 10) * 10 + i for i in range(7)])
    
    gemelo_exacto = None
    gemelo_reserva = None
    lista_nodos = list(grafo.nodes(data=True))
    
    print(f"   🔎 Buscando match para: {cat_objetivo} (Ignorando nivel estricto)...")
    
    for i in range(min(500, len(indices_ordenados))):
        idx = indices_ordenados[i].item()
        nid, attrs = lista_nodos[idx]
        
        # 1. Filtro Categoría
        if str(attrs.get('sub_category')).lower() != cat_objetivo: continue
        
        # 2. Filtro Talla
        t_cand = int(float(attrs.get('talla', 0)))
        if not ((talla_objetivo == 100 or t_cand == 100) or abs(talla_objetivo - t_cand) <= 1): continue
        
        # 3. Filtro Color
        c_cand = int(float(attrs.get('color_nivel', 0)))
        if c_cand == color_objetivo:
            gemelo_exacto = (nid, attrs)
            break
        elif gemelo_reserva is None and (c_cand in familia_colores):
            gemelo_reserva = (nid, attrs)
            
    gemelo_final = gemelo_exacto if gemelo_exacto else gemelo_reserva
    
    # Fallback Búsqueda Gemelo (Si falla talla o color, busca solo categoría)
    if not gemelo_final:
        print("   ⚠️ No match exacto. Usando fallback de categoría...")
        for i in range(100):
            nid, attrs = lista_nodos[indices_ordenados[i].item()]
            if str(attrs.get('sub_category')).lower() == cat_objetivo:
                gemelo_final = (nid, attrs)
                break
    
    if not gemelo_final:
        print("   ⚠️ Fallback Total. Usando Top 1 similitud.")
        nid, attrs = lista_nodos[indices_ordenados[0].item()]
        gemelo_final = (nid, attrs)

    gemelo_id, gemelo_attrs = gemelo_final
    print(f"   👯 Gemelo ID {gemelo_id}: {gemelo_attrs.get('sub_category')}")

    # 4. RECOMENDADOR
    vecinos = list(grafo.neighbors(gemelo_id))
    validos = []
    
    for vid in vecinos:
        attrs_v = grafo.nodes[vid]
        peso = calcular_peso_combinacion(gemelo_attrs, attrs_v)
        if peso > 0: validos.append({'id': vid, 'attrs': attrs_v, 'w': peso})
        
    mejor_look = None
    mejor_score = -1
    
    # Intento 1: Triángulo
    for i in range(len(validos)):
        for j in range(i+1, len(validos)):
            cA, cB = validos[i], validos[j]
            if grafo.has_edge(cA['id'], cB['id']):
                niveles = sorted([
                    int(float(gemelo_attrs.get('nivel', 2))),
                    int(float(cA['attrs'].get('nivel', 2))),
                    int(float(cB['attrs'].get('nivel', 2)))
                ])
                if niveles in COMBINACIONES_VALIDAS:
                    peso_AB = calcular_peso_combinacion(cA['attrs'], cB['attrs'])
                    score = (cA['w'] + cB['w'] + peso_AB) / 3
                    if score > mejor_score:
                        mejor_score = score
                        mejor_look = (cA['attrs'], cB['attrs'])
                        
    rec1, rec2 = {}, {}
    if mejor_look:
        rec1, rec2 = format_node_reco(mejor_look[0]), format_node_reco(mejor_look[1])
        print(f"   ✅ Triángulo (Score: {mejor_score:.2f})")
    else:
        # Intento 2: Buscar en Grafo Global (Para evitar que Nivel 3 sin vecinos se cuelgue)
        print("   ⚠️ Sin triángulo. Buscando en grafo global...")
        target_levels = []
        nivel_G = int(float(gemelo_attrs.get('nivel', 2)))
        if nivel_G == 2: target_levels = [1, 3]
        elif nivel_G == 1: target_levels = [2, 3]
        elif nivel_G == 3: target_levels = [1, 2]
        
        candidatos_global = []
        for i in range(min(300, len(indices_ordenados))):
            idx = indices_ordenados[i].item()
            nid, attrs = lista_nodos[idx]
            if nid == gemelo_id: continue
            
            n_cand = int(float(attrs.get('nivel', 0)))
            if n_cand in target_levels:
                peso = calcular_peso_combinacion(gemelo_attrs, attrs)
                if peso > 0:
                    candidatos_global.append({'attrs': attrs, 'lvl': n_cand})
        
        best_r1 = next((c for c in candidatos_global if c['lvl'] == target_levels[0]), None)
        best_r2 = next((c for c in candidatos_global if c['lvl'] == target_levels[1]), None)
        
        if best_r1: rec1 = format_node_reco(best_r1['attrs'])
        if best_r2: rec2 = format_node_reco(best_r2['attrs'])
        
        if not rec1 and len(validos) > 0: rec1 = format_node_reco(validos[0]['attrs'])
        if not rec2 and len(validos) > 1: rec2 = format_node_reco(validos[1]['attrs'])

    return user_item_final, rec1, rec2

# ==========================================
# 7. BUCLE
# ==========================================
consumer = Consumer(CONF_KAFKA)
consumer.subscribe([TOPIC_NAME])
print("\n---------------------------------------------------------")
print(f"🎧 IA LISTA (CORRECCIÓN DE BÚSQUEDA NIVEL 3)")
print("---------------------------------------------------------")

try:
    while True:
        msg = consumer.poll(1.0)
        if msg is None: continue
        if msg.error(): continue

        try:
            valor_str = msg.value().decode('utf-8')
            paquete = json.loads(valor_str)
            user_item, r1, r2 = procesar_solicitud(paquete.get('display', {}), paquete.get('gcn_input', {}))
            
            resultado = {"user_item": user_item, "rec_1": r1, "rec_2": r2}
            
            if not os.path.exists("static"): os.makedirs("static")
            with open(PATH_RESULTADO, "w") as f:
                json.dump({"status": "success", "data": resultado}, f)
            print("   💾 Resultado guardado.")
                
        except Exception as e:
            print(f"⚠️ Error: {e}")
            import traceback
            traceback.print_exc()

except KeyboardInterrupt: pass