from flask import Flask, request, jsonify
from flask_cors import CORS
import networkx as nx
import folium
import math

app = Flask(__name__)
CORS(app)

# Carga el grafo con atributos 'lat' y 'lon'
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

@app.route("/api/route")
def api_route():
    orig = request.args.get("orig")
    dest = request.args.get("dest")
    algo = request.args.get("algo", "dij")
    route_coords = []

    try:
        if algo == "astar":
            path = nx.astar_path(G, orig, dest, heuristic=haversine, weight="dist")
        else:
            path = nx.shortest_path(G, orig, dest, weight="dist")
        for n in path:
            lat = float(G.nodes[n]['lat'])
            lon = float(G.nodes[n]['lon'])
            route_coords.append([lat, lon])
    except Exception as e:
        return jsonify(error=str(e)), 400

    return jsonify(coords=route_coords)

if __name__ == "__main__":
    app.run(port=5000, debug=True)
