from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
import math

app = Flask(__name__)
CORS(app)

# Carga el grafo con atributos 'lat', 'lon' y peso 'dist'
G = nx.read_graphml("CajamarcaSimpleRoads.graphml")

# Heurística Haversine

def haversine(u, v):
    lat1, lon1 = float(G.nodes[u]['lat']), float(G.nodes[u]['lon'])
    lat2, lon2 = float(G.nodes[v]['lat']), float(G.nodes[v]['lon'])
    R = 6371.0
    dphi = math.radians(lat2 - lat1)
    dlambda = math.radians(lon2 - lon1)
    a = math.sin(dphi/2)**2 + math.cos(math.radians(lat1)) * \
        math.cos(math.radians(lat2)) * math.sin(dlambda/2)**2
    return 2 * R * math.atan2(math.sqrt(a), math.sqrt(1 - a))

# Endpoint para obtener la lista de nodos
@app.route("/api/nodes")
def api_nodes():
    # Devuelve una lista de IDs de nodos en el grafo
    nodes = list(G.nodes())
    return jsonify(nodes)

# Verificación de conectividad (BFS, O(V+E))
@app.route("/api/connectivity")
def api_connectivity():
    orig = request.args.get("orig")
    dest = request.args.get("dest")
    if not orig or not dest:
        return jsonify(error="Parámetros 'orig' y 'dest' requeridos"), 400
    connected = nx.has_path(G, orig, dest)
    return jsonify(connected=connected)

# Heurística Nearest Neighbor para TSP aproximado (O(V^2))
def nearest_neighbor_path(orig):
    unvisited = set(G.nodes())
    if orig not in unvisited:
        raise ValueError(f"Nodo origen '{orig}' no en el grafo")
    path = [orig]
    unvisited.remove(orig)
    current = orig
    while unvisited:
        # seleccionar el nodo más cercano por línea recta
        next_node = min(unvisited, key=lambda v: haversine(current, v))
        path.append(next_node)
        unvisited.remove(next_node)
        current = next_node
    return path

# Placeholder clustering jerárquico: particionar y resolver subrutas
# Aquí simplemente usamos Dijkstra como fallback

def cluster_path(orig, dest):
    # TODO: implementar clustering jerárquico real
    return nx.shortest_path(G, orig, dest, weight="dist")

# Endpoint principal de rutas
@app.route("/api/route")
def api_route():
    orig = request.args.get("orig")
    dest = request.args.get("dest")
    algo = request.args.get("algo", "dij")

    if not orig or not dest:
        return jsonify(error="Parámetros 'orig' y 'dest' requeridos"), 400

    try:
        if algo == "astar":
            path = nx.astar_path(G, orig, dest, heuristic=haversine, weight="dist")
        elif algo == "nn":
            path = nearest_neighbor_path(orig)
        elif algo == "cluster":
            path = cluster_path(orig, dest)
        else:
            # dij o valor por defecto
            path = nx.shortest_path(G, orig, dest, weight="dist")

        # Construir coordenadas para el frontend
        coords = []
        for n in path:
            coords.append([float(G.nodes[n]['lat']), float(G.nodes[n]['lon'])])

    except Exception as e:
        return jsonify(error=str(e)), 400

    return jsonify(coords=coords)

if __name__ == "__main__":
    app.run(port=5000, debug=True)