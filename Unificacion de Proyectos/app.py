from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# Ruta principal
@app.route('/')
def index():
    return render_template('index.html')

# ============ PROYECTO 1: TABLAS DE VERDAD ============
@app.route('/tablas-verdad')
def tablas_verdad():
    return render_template('tablas_verdad.html')

@app.route('/api/generar-tabla', methods=['POST'])
def generar_tabla():
    # Aquí conectarás tu lógica del Proyecto 1
    data = request.json
    expresion = data.get('expresion', '')
    
    # TODO: Implementar tu lógica de tablas de verdad
    resultado = {
        'status': 'success',
        'mensaje': 'Funcionalidad pendiente de conectar',
        'expresion': expresion
    }
    
    return jsonify(resultado)

# ============ PROYECTO 2: SIMPLIFICACIÓN BOOLEANA ============
@app.route('/simplificacion')
def simplificacion():
    return render_template('simplificacion.html')

@app.route('/api/simplificar', methods=['POST'])
def simplificar():
    # Aquí conectarás tu lógica del Proyecto 2
    data = request.json
    expresion = data.get('expresion', '')
    
    # TODO: Implementar tu lógica de simplificación
    resultado = {
        'status': 'success',
        'mensaje': 'Funcionalidad pendiente de conectar',
        'expresion': expresion
    }
    
    return jsonify(resultado)

# ============ PROYECTO 3: EXPRESIONES REGULARES ============
@app.route('/expresiones-regulares')
def expresiones_regulares():
    return render_template('expresiones_regulares.html')

@app.route('/api/validar-regex', methods=['POST'])
def validar_regex():
    # Aquí conectarás tu lógica del Proyecto 3
    data = request.json
    patron = data.get('patron', '')
    texto = data.get('texto', '')
    
    # TODO: Implementar tu lógica de regex
    resultado = {
        'status': 'success',
        'mensaje': 'Funcionalidad pendiente de conectar',
        'patron': patron,
        'texto': texto
    }
    
    return jsonify(resultado)

# ============ PROYECTO 4: RUTAS Y AUTÓMATAS ============
@app.route('/rutas-automatas')
def rutas_automatas():
    return render_template('rutas_automatas.html')

@app.route('/api/calcular-ruta', methods=['POST'])
def calcular_ruta():
    # Aquí conectarás tu lógica del Proyecto 4
    data = request.json
    grafo = data.get('grafo', {})
    origen = data.get('origen', '')
    destino = data.get('destino', '')
    
    # TODO: Implementar tu lógica de rutas
    resultado = {
        'status': 'success',
        'mensaje': 'Funcionalidad pendiente de conectar',
        'origen': origen,
        'destino': destino
    }
    
    return jsonify(resultado)

if __name__ == '__main__':
    app.run(debug=True, port=5000)