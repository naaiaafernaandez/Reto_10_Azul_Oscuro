from flask import Flask, render_template, request
from confluent_kafka import Producer
import json
import socket
import os

app = Flask(__name__)

# --- KAFKA CONFIG ---
TOPIC_NAME = 'solicitud_look'
conf = {'bootstrap.servers': 'localhost:9092', 'client.id': socket.gethostname()}
producer = None

try:
    producer = Producer(conf)
    print(f"KAFKA: Conectado.")
except:
    print(f"KAFKA: No conectado (Modo Demo).")

def delivery_report(err, msg):
    if err: print(f"Error envío: {err}")
    else: print(f"Enviado a Kafka: {msg.value().decode('utf-8')}")

# --- DEFINICIÓN DE DATOS ---

# 1. TALLAS
MAPA_TALLAS = {
    'XS':1, 'S':2, 'M':3, 'L':4, 'XL':5, 'XXL':6, 'XXXL':7, 'X4XL':8, 'UNQ':100
}

# 2. COLORES CONSOLIDADOS (43 Colores Únicos)
# He agrupado por ID. Ejemplo: Todos los ID 2 son ahora solo 'GREY'.
COLORES_INFO = {
    'black': {'id': 0, 'hex': '#000000'},
    'grey': {'id': 2, 'hex': '#808080'}, # Consolida: gray_light, grey_dark, silver
    'white': {'id': 4, 'hex': '#FFFFFF'},
    'brick': {'id': 10, 'hex': '#8B0000'},
    'crimson': {'id': 11, 'hex': '#DC143C'},
    'red': {'id': 12, 'hex': '#FF0000'},
    'strawberry': {'id': 14, 'hex': '#FC5A8D'},
    'pink': {'id': 15, 'hex': '#FFC0CB'},
    'pale_pink': {'id': 16, 'hex': '#FADADD'},
    'coral': {'id': 23, 'hex': '#FF7F50'},
    'salmon': {'id': 24, 'hex': '#FA8072'},
    'brown': {'id': 30, 'hex': '#8B4513'}, # Consolida: rust, brown_light, taupe
    'ochquetare': {'id': 31, 'hex': '#CC7722'},
    'mandarine': {'id': 32, 'hex': '#FF8C42'},
    'orange': {'id': 33, 'hex': '#FFA500'},
    'mustard': {'id': 40, 'hex': '#E1AD01'},
    'camel': {'id': 41, 'hex': '#C19A6B'},
    'nude': {'id': 45, 'hex': '#E3BC9A'},
    'beige': {'id': 46, 'hex': '#F5F5DC'},
    'khaki': {'id': 50, 'hex': '#C3B091'},
    'ecru': {'id': 51, 'hex': '#C2B280'}, # Consolida: sand
    'gold': {'id': 53, 'hex': '#FFD700'},
    'yellow': {'id': 54, 'hex': '#FFFF00'}, # Consolida: lemon
    'yellow_light': {'id': 56, 'hex': '#FFFFE0'},
    'green_dark': {'id': 70, 'hex': '#006400'},
    'green': {'id': 71, 'hex': '#008000'},
    'jade': {'id': 72, 'hex': '#00A86B'},
    'pistachio': {'id': 74, 'hex': '#93C572'},
    'mint': {'id': 75, 'hex': '#98FF98'}, # Consolida: green_light
    'blue_petrol': {'id': 81, 'hex': '#006C84'},
    'blue_turquoise': {'id': 85, 'hex': '#30D5C8'},
    'blue_light': {'id': 86, 'hex': '#ADD8E6'},
    'blue_klein': {'id': 93, 'hex': '#002FA7'},
    'blue': {'id': 94, 'hex': '#0000FF'},
    'grey_blue': {'id': 95, 'hex': '#6699CC'},
    'baby_blue': {'id': 96, 'hex': '#89CFF0'},
    'blue_dark': {'id': 100, 'hex': '#00008B'},
    'purple': {'id': 112, 'hex': '#800080'},
    'indigo': {'id': 113, 'hex': '#4B0082'},
    'aubergine': {'id': 120, 'hex': '#580F41'},
    'garnet': {'id': 121, 'hex': '#733635'}, # Consolida: wine
    'fuchsia': {'id': 124, 'hex': '#FF00FF'},
    'lilac': {'id': 126, 'hex': '#C8A2C8'}
}

# 3. LISTAS RESTANTES
LISTAS_DATA = {
    'tiempo': ['warm', 'cold'],
    'styles': sorted(['boho', 'classic', 'minimal', 'street', 'night', 'casual']),
    'fits': sorted([x for x in ['loose', 'straight', 'tight', 'oversize'] if x]),
    'prints': sorted(list(set([
        'smooth', 'animal_print', 'sheets', 'bodoque', 'miniprint', 'retro',
        'herringbone', 'horizontal_stripes', 'vertical_stripes', 'printed',
        'floral', 'ethnic', 'geometric', 'liberty', 'polka_dot', 'checked',
        'tie_dye', 'camouflage', 'cachemere', 'tropical', 'tapestry', 
        'prince_of_wales', 'diagonal_stripe', 'two_tone'
    ])))
}

# --- RUTAS DE NAVEGACIÓN ---

@app.route('/')
@app.route('/index.html')
def home(): return render_template('index.html')

@app.route('/charts.html')
def charts(): return render_template('charts.html')

@app.route('/reglas.html')
def reglas(): return render_template('reglas.html')

@app.route('/wheel2.html')
def wheel(): return render_template('wheel2.html')

@app.route('/ejemplos.html')
def ejemplos():
    return render_template('ejemplos.html')

@app.route('/bigdata.html')
def generator():
    return render_template('bigdata.html', 
                           tallas=MAPA_TALLAS, 
                           colores=COLORES_INFO, 
                           data=LISTAS_DATA)

@app.route('/enviar', methods=['POST']) 
def enviar():
    # Borrar caché anterior
    if os.path.exists("static/resultado_ia.json"):
        try: os.remove("static/resultado_ia.json")
        except: pass

    # Captura
    raw_talla = request.form.get('talla')
    raw_color = request.form.get('color')
    
    # Traducción para GCN
    val_talla = MAPA_TALLAS.get(raw_talla, 0)
    # Si falla, devuelve ID 0 (black) por defecto
    val_color = COLORES_INFO.get(raw_color, {'id': 0})['id']

    datos_finales = {
        'display': {
            'talla': raw_talla,
            'color': raw_color,
            'nivel': request.form.get('nivel'),
            'sub_category': request.form.get('sub_category'),
            'tiempo': request.form.get('tiempo'),
            'style': request.form.get('style'),
            'print': request.form.get('print'),
            'fit': request.form.get('fit')
        },
        'gcn_input': {
            'talla_id': val_talla,
            'nivel_id': int(request.form.get('nivel')),
            'color_id': val_color
        }
    }
    
    if producer:
        producer.produce(TOPIC_NAME, json.dumps(datos_finales).encode('utf-8'), callback=delivery_report)
        producer.poll(0)
        producer.flush()

    return render_template('resultado.html', datos=datos_finales['display'])

if __name__ == '__main__':
    app.run(debug=True, port=5000)