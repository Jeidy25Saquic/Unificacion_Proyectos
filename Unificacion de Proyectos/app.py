from flask import Flask, render_template, request, jsonify
import re
from itertools import product
import heapq
from collections import defaultdict
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import networkx as nx
from io import BytesIO
import base64
import warnings
warnings.filterwarnings('ignore')

app = Flask(__name__, static_folder='static', static_url_path='/static')

# ============ PROYECTO 1: TABLAS DE VERDAD ============

def generar_tabla_verdad(expresion):
    """Genera tabla de verdad para una expresión booleana"""
    expresion = expresion.strip()
    variables = sorted(set(c for c in expresion if c.isalpha()))
    
    if not variables:
        return {'error': 'No se encontraron variables'}, None
    
    tabla = []
    for valores in product([0, 1], repeat=len(variables)):
        contexto = dict(zip(variables, valores))
        try:
            expr_eval = expresion
            for var, val in contexto.items():
                expr_eval = expr_eval.replace(var, str(val))
            
            expr_eval = expr_eval.replace('&', ' and ').replace('|', ' or ').replace('~', 'not ')
            resultado = eval(expr_eval)
            
            fila = list(valores) + [1 if resultado else 0]
            tabla.append(fila)
        except:
            return {'error': 'Expresión inválida'}, None
    
    return {
        'variables': variables,
        'tabla': tabla,
        'expresion': expresion
    }, None

# ============ PROYECTO 2: SIMPLIFICACIÓN BOOLEANA ============

class SimplificadorBooleano:
    """Simplifica expresiones booleanas paso a paso"""
    
    @staticmethod
    def simplificar(expresion):
        """Aplica leyes de simplificación y retorna pasos"""
        expresion = expresion.replace(' ', '')
        pasos = [('Original', expresion)]
        
        for _ in range(10):
            cambio = False
            
            while '~~' in expresion:
                expresion = expresion.replace('~~', '')
                pasos.append(('Doble negación', expresion))
                cambio = True
            
            for op, reemplazo in [('&1', ''), ('|0', ''), ('&0', '0'), ('|1', '1')]:
                if op in expresion:
                    expresion = expresion.replace(op, reemplazo)
                    pasos.append((f'Ley: {op}', expresion))
                    cambio = True
            
            if not cambio:
                break
        
        return pasos

# ============ PROYECTO 3: EXPRESIONES REGULARES ============

class RegexRules:
    """Reglas predefinidas de expresiones regulares"""
    
    rules = {
        "numero_entero": (r"^[0-9]+$", "Solo dígitos, sin decimales ni signos"),
        "palabra_minuscula": (r"^[a-z]+$", "Solo letras minúsculas"),
        "nombre_mayuscula_inicial": (r"^[A-Z][a-z]+$", "Nombre con inicial mayúscula"),
        "telefono_con_guiones": (r"[0-9]{3}-[0-9]{4}-[0-9]{4}", "Teléfono (000-0000-0000)"),
        "digito": (r"[0-9]", "Cualquier dígito"),
        "mayuscula": (r"[A-Z]", "Letra mayúscula"),
        "minuscula": (r"[a-z]", "Letra minúscula"),
        "cero_o_mas": (r"a*", "Cero o más veces 'a'"),
        "uno_o_mas": (r"a+", "Una o más veces 'a'"),
        "entre_n_m": (r"[0-9]{2,4}", "Entre 2 y 4 dígitos"),
        "alternativa": (r"(perro|gato)", "perro o gato"),
        "binario_3": (r"(0|1){3}", "Cadenas binarias de 3 símbolos"),
    }
    
    @classmethod
    def get_rule(cls, name):
        if name in cls.rules:
            return cls.rules[name][0]
        return None
    
    @classmethod
    def get_all_rules(cls):
        return [{'name': k, 'pattern': v[0], 'description': v[1]} for k, v in cls.rules.items()]

def validar_regex(regex):
    """Valida una expresión regular"""
    try:
        re.compile(regex)
        return True, ""
    except re.error as e:
        return False, str(e)

def resaltar_coincidencias(texto, regex):
    """Retorna coincidencias en el texto"""
    try:
        coincidencias = list(re.finditer(regex, texto, re.MULTILINE))
        return [m.group() for m in coincidencias], len(coincidencias)
    except:
        return [], 0

# ============ PROYECTO 4: RUTAS Y AUTÓMATAS ============

class Grafo:
    """Representa un grafo ponderado dirigido o no dirigido"""
    
    def __init__(self, dirigido=False):
        self.adyacencia = defaultdict(list)
        self.nodos = set()
        self.dirigido = dirigido
    
    def agregar_nodo(self, nodo):
        self.nodos.add(nodo)
    
    def agregar_arista(self, origen, destino, peso=1):
        self.agregar_nodo(origen)
        self.agregar_nodo(destino)
        
        self.adyacencia[origen].append((destino, peso))
        
        if not self.dirigido:
            self.adyacencia[destino].append((origen, peso))
    
    def dijkstra(self, origen, destino):
        """Algoritmo de Dijkstra para encontrar la ruta más corta"""
        if origen not in self.nodos or destino not in self.nodos:
            return None, []
        
        distancias = {nodo: float('inf') for nodo in self.nodos}
        distancias[origen] = 0
        previos = {nodo: None for nodo in self.nodos}
        cola = [(0, origen)]
        visitados = set()
        
        while cola:
            distancia_actual, nodo_actual = heapq.heappop(cola)
            
            if nodo_actual in visitados:
                continue
            
            visitados.add(nodo_actual)
            
            if nodo_actual == destino:
                break
            
            for vecino, peso in self.adyacencia[nodo_actual]:
                if vecino not in visitados:
                    nueva_distancia = distancia_actual + peso
                    
                    if nueva_distancia < distancias[vecino]:
                        distancias[vecino] = nueva_distancia
                        previos[vecino] = nodo_actual
                        heapq.heappush(cola, (nueva_distancia, vecino))
        
        ruta = []
        nodo = destino
        
        if distancias[destino] != float('inf'):
            while nodo is not None:
                ruta.append(nodo)
                nodo = previos[nodo]
            ruta.reverse()
        
        return distancias[destino], ruta
    
    def obtener_nodos(self):
        return list(self.nodos)
    
    def obtener_aristas(self):
        aristas = []
        visitadas = set()
        
        for origen in self.adyacencia:
            for destino, peso in self.adyacencia[origen]:
                if self.dirigido or (origen, destino) not in visitadas and (destino, origen) not in visitadas:
                    aristas.append((origen, destino, peso))
                    if not self.dirigido:
                        visitadas.add((origen, destino))
        
        return aristas

class Automata:
    """Autómata formal para validar rutas en el grafo"""
    
    def __init__(self, grafo, estado_inicial, estados_aceptacion):
        self.grafo = grafo
        self.Q = set(grafo.obtener_nodos())
        self.q0 = estado_inicial
        self.F = set(estados_aceptacion) if isinstance(estados_aceptacion, list) else {estados_aceptacion}
        
        self._construir_alfabeto()
        self._construir_transiciones()
    
    def _construir_alfabeto(self):
        self.sigma = set()
        
        for origen in self.grafo.adyacencia:
            for destino, peso in self.grafo.adyacencia[origen]:
                simbolo = f"{origen}→{destino}"
                self.sigma.add(simbolo)
    
    def _construir_transiciones(self):
        self.delta = {}
        self.w = {}
        
        for origen in self.grafo.adyacencia:
            for destino, peso in self.grafo.adyacencia[origen]:
                simbolo = f"{origen}→{destino}"
                self.delta[(origen, simbolo)] = destino
                self.w[simbolo] = peso
    
    def procesar_cadena(self, cadena_nodos):
        if len(cadena_nodos) < 2:
            return {
                'aceptada': False,
                'estado_actual': None,
                'paso_fallo': 0,
                'costo_total': 0
            }
        
        estado_actual = cadena_nodos[0]
        costo_total = 0
        
        if estado_actual != self.q0:
            return {
                'aceptada': False,
                'estado_actual': estado_actual,
                'paso_fallo': 0,
                'costo_total': 0
            }
        
        for i in range(len(cadena_nodos) - 1):
            origen = cadena_nodos[i]
            destino = cadena_nodos[i + 1]
            simbolo = f"{origen}→{destino}"
            
            if (origen, simbolo) not in self.delta:
                return {
                    'aceptada': False,
                    'estado_actual': origen,
                    'paso_fallo': i + 1,
                    'costo_total': costo_total
                }
            
            estado_actual = self.delta[(origen, simbolo)]
            costo_total += self.w[simbolo]
        
        aceptada = estado_actual in self.F
        
        return {
            'aceptada': aceptada,
            'estado_actual': estado_actual,
            'paso_fallo': None if aceptada else len(cadena_nodos),
            'costo_total': costo_total
        }
    
    def obtener_descripcion_formal(self):
        return {
            'Q': sorted(list(self.Q)),
            'sigma': sorted(list(self.sigma)),
            'q0': self.q0,
            'F': sorted(list(self.F)),
            'transiciones': len(self.delta),
            'pesos': dict(sorted(self.w.items()))
        }

# Variables globales para el grafo
grafo_global = None
COLORES = {
    'nodo_normal': '#3498db',
    'nodo_ruta': '#e74c3c',
    'arista_normal': '#95a5a6',
    'arista_ruta': '#e74c3c',
    'fondo': '#f8f9fa'
}

def generar_visualizacion_simple():
    """Genera visualización del grafo sin ruta destacada"""
    global grafo_global
    
    if grafo_global is None or len(grafo_global.obtener_nodos()) == 0:
        return None
    
    G = nx.Graph() if not grafo_global.dirigido else nx.DiGraph()
    
    for nodo in grafo_global.obtener_nodos():
        G.add_node(nodo)
    
    for origen, destino, peso in grafo_global.obtener_aristas():
        G.add_edge(origen, destino, weight=peso)
    
    plt.figure(figsize=(10, 8), facecolor=COLORES['fondo'])
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    nx.draw(G, pos, with_labels=True,
            node_color=COLORES['nodo_normal'],
            node_size=1500,
            font_weight='bold',
            font_color='white',
            edge_color=COLORES['arista_normal'],
            arrows=grafo_global.dirigido,
            arrowsize=20)
    
    edge_labels = {(u, v): w for u, v, w in grafo_global.obtener_aristas()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=10)
    
    plt.axis('off')
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor=COLORES['fondo'])
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return imagen_base64

def generar_visualizacion(ruta_destacada):
    """Genera visualización del grafo con ruta destacada"""
    global grafo_global
    
    G = nx.Graph() if not grafo_global.dirigido else nx.DiGraph()
    
    for nodo in grafo_global.obtener_nodos():
        G.add_node(nodo)
    
    for origen, destino, peso in grafo_global.obtener_aristas():
        G.add_edge(origen, destino, weight=peso)
    
    plt.figure(figsize=(10, 8), facecolor=COLORES['fondo'])
    pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
    
    nodos_normales = [n for n in G.nodes() if n not in ruta_destacada]
    nx.draw_networkx_nodes(G, pos, nodelist=nodos_normales,
                           node_color=COLORES['nodo_normal'], node_size=1500)
    nx.draw_networkx_nodes(G, pos, nodelist=ruta_destacada,
                           node_color=COLORES['nodo_ruta'], node_size=1500)
    
    aristas_ruta = [(ruta_destacada[i], ruta_destacada[i + 1])
                    for i in range(len(ruta_destacada) - 1)]
    aristas_normales = [(u, v) for u, v in G.edges() if (u, v) not in aristas_ruta and (v, u) not in aristas_ruta]
    
    nx.draw_networkx_edges(G, pos, edgelist=aristas_normales,
                           width=1, edge_color=COLORES['arista_normal'],
                           arrows=grafo_global.dirigido, arrowsize=20)
    
    nx.draw_networkx_edges(G, pos, edgelist=aristas_ruta,
                           width=3, edge_color=COLORES['arista_ruta'],
                           arrows=grafo_global.dirigido, arrowsize=25)
    
    nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold', font_color='white')
    
    edge_labels = {(u, v): w for u, v, w in grafo_global.obtener_aristas()}
    nx.draw_networkx_edge_labels(G, pos, edge_labels, font_size=10)
    
    plt.axis('off')
    
    buffer = BytesIO()
    plt.savefig(buffer, format='png', dpi=100, bbox_inches='tight', facecolor=COLORES['fondo'])
    buffer.seek(0)
    imagen_base64 = base64.b64encode(buffer.read()).decode()
    plt.close()
    
    return imagen_base64

# ============ RUTAS PRINCIPALES ============

@app.route('/')
def index():
    return render_template('index.html')

# ---- PROYECTO 1 ----
@app.route('/tablas-verdad')
def tablas_verdad():
    return render_template('tablas_verdad.html')

@app.route('/api/generar-tabla', methods=['POST'])
def api_generar_tabla():
    data = request.get_json()
    expresion = data.get('expresion', '')
    resultado, error = generar_tabla_verdad(expresion)
    
    if error:
        return jsonify({'error': error}), 400
    
    return jsonify(resultado)

# ---- PROYECTO 2 ----
@app.route('/simplificacion')
def simplificacion():
    return render_template('simplificacion.html')

# ---- PROYECTO 3 ----
@app.route('/expresiones-regulares')
def expresiones_regulares():
    reglas = RegexRules.get_all_rules()
    return render_template('expresiones_regulares.html', reglas=reglas)

@app.route('/procesar', methods=['POST'])
def procesar_regex():
    data = request.get_json()
    patron = data.get('regex', '')
    texto = data.get('texto', '')
    
    es_valida, error = validar_regex(patron)
    
    if not es_valida:
        return jsonify({'valid': False, 'error': f'Error en la expresión regular: {error}'})
    
    lineas = texto.split('\n')
    if len(lineas) < 5:
        return jsonify({'valid': False, 'error': 'El texto debe tener al menos 5 líneas.'})
    
    coincidencias, total = resaltar_coincidencias(texto, patron)
    
    texto_resaltado = texto
    offset = 0
    try:
        for match in re.finditer(patron, texto, re.MULTILINE):
            inicio, fin = match.span()
            texto_resaltado = (
                texto_resaltado[:inicio + offset] +
                "<mark>" + texto_resaltado[inicio + offset:fin + offset] + "</mark>" +
                texto_resaltado[fin + offset:]
            )
            offset += 13
    except:
        pass
    
    return jsonify({
        'valid': True,
        'texto_resaltado': texto_resaltado,
        'coincidencias': coincidencias,
        'total_coincidencias': total
    })

# ---- PROYECTO 4 ----
@app.route('/rutas-automatas')
def rutas_automatas():
    return render_template('rutas_automatas.html')

@app.route('/iniciar_grafo', methods=['POST'])
def iniciar_grafo():
    global grafo_global
    
    datos = request.json
    dirigido = datos.get('dirigido', False)
    grafo_global = Grafo(dirigido=dirigido)
    
    return jsonify({'exito': True})

@app.route('/agregar_arista', methods=['POST'])
def agregar_arista():
    global grafo_global
    
    if grafo_global is None:
        return jsonify({'exito': False, 'error': 'Grafo no inicializado'}), 400
    
    datos = request.json
    origen = datos.get('origen', '').strip().upper()
    destino = datos.get('destino', '').strip().upper()
    peso = float(datos.get('peso', 1))
    
    if not origen or not destino:
        return jsonify({'exito': False, 'error': 'Origen y destino requeridos'}), 400
    
    if origen == destino:
        return jsonify({'exito': False, 'error': 'El origen y destino no pueden ser iguales'}), 400
    
    if peso <= 0:
        return jsonify({'exito': False, 'error': 'El peso debe ser mayor a 0'}), 400
    
    grafo_global.agregar_arista(origen, destino, peso)
    img_base64 = generar_visualizacion_simple()
    
    return jsonify({
        'exito': True,
        'nodos': grafo_global.obtener_nodos(),
        'aristas': grafo_global.obtener_aristas(),
        'imagen': img_base64
    })

@app.route('/crear_grafo_ejemplo', methods=['POST'])
def crear_grafo_ejemplo():
    global grafo_global
    
    grafo_global = Grafo(dirigido=False)
    
    aristas = [
        ('A', 'B', 4),
        ('A', 'C', 2),
        ('B', 'D', 2),
        ('C', 'D', 3),
        ('C', 'E', 5),
        ('D', 'E', 1)
    ]
    
    for origen, destino, peso in aristas:
        grafo_global.agregar_arista(origen, destino, peso)
    
    img_base64 = generar_visualizacion_simple()
    
    return jsonify({
        'exito': True,
        'nodos': grafo_global.obtener_nodos(),
        'aristas': grafo_global.obtener_aristas(),
        'imagen': img_base64
    })

@app.route('/calcular_ruta', methods=['POST'])
def calcular_ruta():
    global grafo_global
    
    if grafo_global is None:
        return jsonify({'exito': False, 'error': 'Grafo no inicializado'}), 400
    
    datos = request.json
    origen = datos.get('origen', '').strip().upper()
    destino = datos.get('destino', '').strip().upper()
    
    if not origen or not destino:
        return jsonify({'exito': False, 'error': 'Origen y destino requeridos'}), 400
    
    distancia, ruta = grafo_global.dijkstra(origen, destino)
    
    if not ruta:
        return jsonify({'exito': False, 'error': f'No hay ruta entre {origen} y {destino}'}), 404
    
    automata = Automata(grafo_global, origen, destino)
    validacion = automata.procesar_cadena(ruta)
    img_base64 = generar_visualizacion(ruta)
    
    return jsonify({
        'exito': True,
        'distancia': distancia,
        'ruta': ruta,
        'validacion_formal': validacion,
        'imagen': img_base64,
        'descripcion_automata': automata.obtener_descripcion_formal()
    })

@app.route('/info_automata', methods=['GET'])
def info_automata():
    global grafo_global
    
    if grafo_global is None:
        return jsonify({'exito': False, 'error': 'Grafo no inicializado'}), 400
    
    nodos = grafo_global.obtener_nodos()
    if len(nodos) < 2:
        return jsonify({'exito': False, 'error': 'Se necesitan al menos 2 nodos'}), 400
    
    automata = Automata(grafo_global, nodos[0], nodos[-1])
    
    return jsonify({
        'exito': True,
        'descripcion': automata.obtener_descripcion_formal()
    })

if __name__ == '__main__':
    app.run(debug=True, port=5000)