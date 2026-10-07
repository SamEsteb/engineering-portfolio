import 'package:latlong2/latlong.dart';
import 'dart:convert';
import 'dart:math';
import 'package:collection/collection.dart';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

// Clase que gestiona nodos y búsqueda de caminos
class NodosManager {
  Map<String, Map<String, dynamic>> nodos = {};

Future<void> cargarNodos(String edificio, String piso) async {
  try {
    final url = ApiConfig.nodosUrl(edificio, piso);
    print('Intentando cargar nodos desde: $url'); // Log para debug
    
    final response = await http.get(Uri.parse(url));
    
    if (response.statusCode == 200) {
      //print('Respuesta recibida: ${response.body}'); // Log para debug
      final List<dynamic> data = json.decode(response.body);
      nodos.clear();
      
      for (var nodo in data) {
        String nodoId = nodo['id'];
        nodos[nodoId] = {
          'pos': LatLng(
            nodo['pos']['lat'].toDouble(), 
            nodo['pos']['lng'].toDouble()
          ),
          'conexiones': List<String>.from(nodo['conexiones']),
          'tipo': nodo['tipo'],
          'edificio': nodo['edificio'],
          'piso': nodo['piso']
        };
      }
      print('Nodos cargados exitosamente: ${nodos.length}');
    } else {
      print('Error en la respuesta: ${response.statusCode}');
    }
  } catch (e) {
    print("Error al cargar nodos: $e");
  }
}

  // Método para obtener los nodos
  Map<String, Map<String, dynamic>> obtenerNodosPorEdificioYPiso(
      String edificio, String piso) {
    return Map.fromEntries(
      nodos.entries.where(
        (entry) =>
            entry.value['edificio'] == edificio && entry.value['piso'] == piso,
      ),
    );
  }

  Map<String, Node> createGraph() {
    final graph = <String, Node>{};

    nodos.forEach((id, value) {
      graph[id] = Node(
        id: id,
        position: value['pos'],
        neighbors: List<String>.from(value['conexiones']),
      );
    });

    return graph;
  }

  List<String> calcularCaminoMasCorto(String start, String goal) {
    final graph = createGraph();
    final aStar = AStar(graph);
    return aStar.findPath(start, goal);
  }
}

class Node {
  final String id;
  final LatLng position;
  final List<String> neighbors;

  Node({
    required this.id,
    required this.position,
    required this.neighbors,
  });
}

double calculateDistance(LatLng p1, LatLng p2) {
  final lat1 = p1.latitude;
  final lon1 = p1.longitude;
  final lat2 = p2.latitude;
  final lon2 = p2.longitude;

  final latDiff = lat2 - lat1;
  final lonDiff = lon2 - lon1;

  return sqrt(latDiff * latDiff + lonDiff * lonDiff);
}

class AStar {
  final Map<String, Node> graph;

  AStar(this.graph);

  List<String> findPath(String start, String goal) {
    final openList = PriorityQueue<NodeData>((a, b) => a.f.compareTo(b.f));
    final closedList = Set<String>();

    final startNode = graph[start];
    final goalNode = graph[goal];

    if (startNode == null || goalNode == null) return [];

    final cameFrom = <String, String>{};
    final gScore = <String, double>{start: 0};
    final fScore = <String, double>{
      start: calculateDistance(startNode.position, goalNode.position)
    };

    openList.add(NodeData(start, 0, fScore[start]!));

    while (openList.isNotEmpty) {
      final currentNode = openList.removeFirst();
      final currentId = currentNode.id;

      if (currentId == goal) {
        return reconstructPath(cameFrom, currentId);
      }

      closedList.add(currentId);

      for (final neighborId in graph[currentId]!.neighbors) {
        if (closedList.contains(neighborId)) continue;

        final tentativeGScore = gScore[currentId]! +
            calculateDistance(
                graph[currentId]!.position, graph[neighborId]!.position);

        if (!gScore.containsKey(neighborId) ||
            tentativeGScore < gScore[neighborId]!) {
          cameFrom[neighborId] = currentId;
          gScore[neighborId] = tentativeGScore;
          fScore[neighborId] = tentativeGScore +
              calculateDistance(graph[neighborId]!.position, goalNode.position);

          openList
              .add(NodeData(neighborId, tentativeGScore, fScore[neighborId]!));
        }
      }
    }

    return [];
  }

  List<String> reconstructPath(Map<String, String> cameFrom, String currentId) {
    final path = <String>[];

    while (cameFrom.containsKey(currentId)) {
      path.add(currentId);
      currentId = cameFrom[currentId]!;
    }
    path.add(currentId);

    return path.reversed.toList();
  }
}

class NodeData {
  final String id;
  final double g;
  final double f;

  NodeData(this.id, this.g, this.f);
}
