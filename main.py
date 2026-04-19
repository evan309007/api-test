# main.py
from flask import Flask, jsonify, request
import os
from dotenv import load_dotenv
import requests
from deep_translator import GoogleTranslator
from bd import recursos, next_id
import bd

load_dotenv()

app = Flask(__name__)


API_NINJAS_KEY = os.getenv("API_NINJAS_KEY")
API_URL = "https://api.api-ninjas.com/v1/facts?limit=1" 

print(f"API Key cargada: {API_NINJAS_KEY[:5]}...")

@app.route('/api/chiste', methods=['GET'])
def obtener_hecho_curioso():
    """Obtiene chiste de Chuck Norris y lo traduce al español"""
    try:
        # Obtener chiste en inglés
        url = "https://api.chucknorris.io/jokes/random"
        response = requests.get(url, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            joke_en = data["value"]
            
            # Traducir a español usando deep-translator
            traductor = GoogleTranslator(source='en', target='es')
            joke_es = traductor.translate(joke_en)
            
            return jsonify({
                "fuente": "Chuck Norris API (traducido)",
                "hecho_original": joke_en,
                "hecho": joke_es
            }), 200
        else:
            return jsonify({"error": f"Error {response.status_code}"}), 500
    except Exception as e:
        return jsonify({"error": f"Error: {str(e)}"}), 500

@app.route('/api/recursos', methods=['GET'])
def listar_recursos():
    """GET /api/recursos → Lista todos los registros"""
    return jsonify(list(recursos.values())), 200


@app.route('/api/recursos/<int:recurso_id>', methods=['GET'])
def obtener_recurso(recurso_id):
    """GET /api/recursos/<id> → Obtiene un registro por ID"""
    if recurso_id not in recursos:
        return jsonify({"error": "Recurso no encontrado"}), 404
    return jsonify(recursos[recurso_id]), 200


@app.route('/api/recursos', methods=['POST'])
def crear_recurso():
    """POST /api/recursos → Crea un nuevo registro"""
    if not request.is_json:
        return jsonify({"error": "El cuerpo debe ser JSON"}), 400

    data = request.get_json()

    # Validación básica
    if not data or "nombre" not in data:
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400

    # Generar ID automático
    global next_id
    nuevo_id = bd.next_id
    bd.next_id += 1

    nuevo_recurso = {
        "id": nuevo_id,
        "nombre": data["nombre"],
        "descripcion": data.get("descripcion", ""),
    }

    recursos[nuevo_id] = nuevo_recurso
    return jsonify(nuevo_recurso), 201


@app.route('/api/recursos/<int:recurso_id>', methods=['PUT'])
def actualizar_recurso(recurso_id):
    """PUT /api/recursos/<id> → Actualiza un registro existente"""
    if recurso_id not in recursos:
        return jsonify({"error": "Recurso no encontrado"}), 404

    if not request.is_json:
        return jsonify({"error": "El cuerpo debe ser JSON"}), 400

    data = request.get_json()

    if not data or "nombre" not in data:
        return jsonify({"error": "El campo 'nombre' es obligatorio"}), 400

    recursos[recurso_id].update({
        "nombre": data["nombre"],
        "descripcion": data.get("descripcion", recursos[recurso_id]["descripcion"])
    })

    return jsonify(recursos[recurso_id]), 200


@app.route('/api/recursos/<int:recurso_id>', methods=['DELETE'])
def eliminar_recurso(recurso_id):
    """DELETE /api/recursos/<id> → Elimina un registro"""
    if recurso_id not in recursos:
        return jsonify({"error": "Recurso no encontrado"}), 404

    del recursos[recurso_id]
    return jsonify({"mensaje": "Recurso eliminado correctamente"}), 200


if __name__ == '__main__':
    app.run(debug=True, port=5000)
    