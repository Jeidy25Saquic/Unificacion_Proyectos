from flask import Flask, render_template, request, jsonify
import re
from itertools import product

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

class CalculadorRutas:
    """Calcula rutas óptimas en grafos"""
    
    @staticmethod
    def dijkstra(grafo, inicio, fin):
        """Implementa el algoritmo de Dijkstra"""
        if inicio not in grafo or fin not in grafo:
            return None, "Nodo no encontrado"
        
        distancias = {nodo: float('inf') for nodo in grafo}
        distancias[inicio] = 0
        previos = {nodo: None for nodo in grafo}
        visitados = set()
        
        while len(visitados) < len(grafo):
            nodo_actual = min(
                (nodo for nodo in grafo if nodo not in visitados),
                key=lambda n: distancias[n],
                default=None
            )
            
            if nodo_actual is None or distancias[nodo_actual] == float('inf'):
                break
            
            visitados.add(nodo_actual)
            
            for vecino, peso in grafo[nodo_actual]:
                distancia = distancias[nodo_actual] + peso
                if distancia < distancias[vecino]:
                    distancias[vecino] = distancia
                    previos[vecino] = nodo_actual
        
        ruta = []
        nodo = fin
        while nodo is not None:
            ruta.insert(0, nodo)
            nodo = previos[nodo]
        
        if ruta[0] != inicio:
            return None, "No hay ruta disponible"
        
        return ruta, distancias[fin]

# ============ RUTAS PRINCIPALES ============

@app.route('/')
def index():
    return render_template('index.html')

# ---- PROYECTO 1: TABLAS DE VERDAD ----
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

# ---- PROYECTO 2: SIMPLIFICACIÓN ----
@app.route('/simplificacion')
def simplificacion():
    return render_template('simplificacion.html')

@app.route('/api/simplificar', methods=['POST'])
def api_simplificar():
    data = request.get_json()
    expresion = data.get('expresion', '')
    pasos = SimplificadorBooleano.simplificar(expresion)
    
    return jsonify({'pasos': pasos})

# ---- PROYECTO 3: EXPRESIONES REGULARES ----
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
    
    # Resaltar en el texto
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
            offset += 13  # longitud de <mark></mark>
    except:
        pass
    
    return jsonify({
        'valid': True,
        'texto_resaltado': texto_resaltado,
        'coincidencias': coincidencias,
        'total_coincidencias': total
    })

# ---- PROYECTO 4: RUTAS Y AUTÓMATAS ----
@app.route('/rutas-automatas')
def rutas_automatas():
    return render_template('rutas_automatas.html')

@app.route('/api/calcular-ruta', methods=['POST'])
def api_calcular_ruta():
    data = request.get_json()
    
    nodos = {}
    aristas_str = data.get('aristas', '')
    
    try:
        for arista in aristas_str.split(','):
            partes = arista.strip().split('-')
            if len(partes) != 3:
                continue
            
            origen, destino, peso = partes[0].strip(), partes[1].strip(), int(partes[2])
            
            if origen not in nodos:
                nodos[origen] = []
            if destino not in nodos:
                nodos[destino] = []
            
            nodos[origen].append((destino, peso))
        
        inicio = data.get('inicio', '').strip()
        fin = data.get('fin', '').strip()
        
        ruta, distancia = CalculadorRutas.dijkstra(nodos, inicio, fin)
        
        if ruta is None:
            return jsonify({'error': distancia}), 400
        
        return jsonify({
            'ruta': ' → '.join(ruta),
            'distancia': distancia
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 400

if __name__ == '__main__':
    app.run(debug=True, port=5000)