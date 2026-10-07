import 'package:flutter/material.dart';
import 'package:flutter_map/flutter_map.dart';
import 'package:latlong2/latlong.dart';
import 'package:geolocator/geolocator.dart';
import 'nodos_manager.dart';
import 'dart:convert';
import 'package:http/http.dart' as http;
import 'dart:async';
import 'package:shared_preferences/shared_preferences.dart';
import 'package:udecmapp/screens/search_history.dart';
import 'package:intl/intl.dart';
import '../config/api_config.dart';

List<Map<String, dynamic>> habitaciones = [];

// Coordenadas centrales de cada edificio
final Map<String, LatLng> _buildingCenters = {
  'EDIFICIO 1': LatLng(-x, -y),
  'EDIFICIO 2': LatLng(-x, -y),
};

Future<void> cargarHabitaciones(String edificio, String piso) async {
  try {
    final url = ApiConfig.habitacionesUrl(edificio, piso);
    print('Intentando cargar habitaciones desde: $url');
    
    final response = await http.get(Uri.parse(url));
    print('Respuesta habitaciones - Status: ${response.statusCode}');
    
    if (response.statusCode == 200) {
      final List<dynamic> data = json.decode(response.body);
      print('Habitaciones recibidas: ${data.length}');
      
      habitaciones = data.map((habitacion) {
        return {
          'id': habitacion['id'],
          'piso': habitacion['piso'],
          'edificio': habitacion['edificio'],
          'coords': (habitacion['coords'] as List<dynamic>)
              .map((coord) => LatLng(
                    coord['lat'].toDouble(),
                    coord['lng'].toDouble(),
                  ))
              .toList(),
        };
      }).toList();
      
      print('Habitaciones procesadas: ${habitaciones.length}');
    } else {
      print('Error al obtener habitaciones: ${response.statusCode}');
      print('Respuesta: ${response.body}');
    }
  } catch (e) {
    print('Error al cargar habitaciones: $e');
    print('Stack trace: ${StackTrace.current}');
  }
}

// Coordenadas del edificio (esquinas del plano)
final List<LatLng> edificioCoords = [
  LatLng(-x, -y), // Esquina 1
  LatLng(-x, -y), // Esquina 2
  LatLng(-x, -y), // Esquina 3
  LatLng(-x, -y), // Esquina 4
  LatLng(-x, -y),
  LatLng(-x, -y),
  LatLng(-x, -y),
  LatLng(-x, -y),
  LatLng(-x, -y),
  LatLng(-x, -y),
  LatLng(-x, -y),
];

final List<LatLng> edificio2Coords = [
  LatLng(-x, -y), // Esquina 1
  LatLng(-x, -y), // Esquina 2
  LatLng(-x, -y), // Esquina 3
  LatLng(-x, -y), // Esquina 4
  LatLng(-x, -y),
  LatLng(-x, -y),
];

class MapView extends StatefulWidget {
  final String? selectedBuilding; // Edificio seleccionado
  final String? selectedFloor; // Piso seleccionado

  const MapView({
    super.key,
    this.selectedBuilding,
    this.selectedFloor,
  });

  @override
  _MapViewState createState() => _MapViewState();
}

class _MapViewState extends State<MapView> with SingleTickerProviderStateMixin {
  final NodosManager nodosManager = NodosManager();
  late MapController _mapController;
  bool _mapReady = false;
  String? _startNode;
  String? _endNode;
  List<LatLng> _pathCoordinates = [];
  Marker? _currentLocationMarker;
  StreamSubscription<Position>? _positionStream;
  String? previousSelectedBuilding;
  String? previousSelectedFloor;

  late AnimationController _animationController;
  List<LatLng> _animatedPathPoints = [];

  bool _isLocationEnabled = false;
  StreamSubscription<Position>? _positionStreamSubscription;


  @override
  void initState() {
    super.initState();
    
    _animationController = AnimationController(
      vsync: this,
      duration: const Duration(milliseconds: 2000), // Ajustado para animación más suave
    );
    
    // Nuevo listener para animación más suave
    _animationController.addListener(() {
      if (_pathCoordinates.isEmpty) return;
      
      final progress = _animationController.value;
      final totalDistance = _calculateTotalDistance();
      final targetDistance = totalDistance * progress;
      
      final interpolated = _interpolatePoints(targetDistance);
      setState(() {
        _animatedPathPoints = interpolated;
      });
    });

    _mapController = MapController();

    WidgetsBinding.instance.addPostFrameCallback((_) {
      setState(() {
        _mapReady = true;
      });
      _setInitialMapCenter();
    });
  }

  @override
  void didUpdateWidget(MapView oldWidget) {
    super.didUpdateWidget(oldWidget);
    
    // Solo cargar datos si hay un edificio y piso seleccionados
    if (widget.selectedBuilding != null && widget.selectedFloor != null) {
      // Si el edificio o piso cambiaron, cargar los nuevos datos
      if (widget.selectedBuilding != oldWidget.selectedBuilding || 
          widget.selectedFloor != oldWidget.selectedFloor) {
        _loadData();
      }
    }
  }

  Future<void> _loadData() async {
    try {
      // Cargar datos en paralelo
      await Future.wait([
        cargarHabitaciones(widget.selectedBuilding!, widget.selectedFloor!),
        nodosManager.cargarNodos(widget.selectedBuilding!, widget.selectedFloor!)
      ]);
      setState(() {});
    } catch (e) {
      print("Error al cargar datos: $e");
    }
  }

  void _setInitialMapCenter() {
    // Solo mover el mapa si ya está listo
    if (_mapReady) {
      final center = _buildingCenters[widget.selectedBuilding] ??
          LatLng(-36.830492703728666,
              -73.03684140759844); // Valor predeterminado si no hay edificio seleccionado
      _mapController.move(center, 18.0); // Mueve el mapa al centro inicial
    }
  }

  @override
  void dispose() {
    _animationController.dispose();
    _positionStream?.cancel();
    _positionStreamSubscription?.cancel();
    super.dispose();
  }

  Future<bool> _handleLocationPermission() async {
  bool serviceEnabled;
  LocationPermission permission;

  // Verificar si el servicio de ubicación está habilitado
  serviceEnabled = await Geolocator.isLocationServiceEnabled();
  if (!serviceEnabled) {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
      content: Text('Los servicios de ubicación están deshabilitados. Por favor, actívalos.'),
    ));
    return false;
  }

  // Verificar permisos de ubicación
  permission = await Geolocator.checkPermission();
  if (permission == LocationPermission.denied) {
    permission = await Geolocator.requestPermission();
    if (permission == LocationPermission.denied) {
      ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
        content: Text('Los permisos de ubicación fueron denegados.'),
      ));
      return false;
    }
  }

  if (permission == LocationPermission.deniedForever) {
    ScaffoldMessenger.of(context).showSnackBar(const SnackBar(
      content: Text('Los permisos de ubicación están permanentemente denegados. No se puede solicitar permisos.'),
    ));
    return false;
  }

  return true;
}

void _toggleLocationTracking() async {
  if (!_isLocationEnabled) {
    final hasPermission = await _handleLocationPermission();
    if (!hasPermission) return;

    setState(() {
      _isLocationEnabled = true;
    });

    // Configuración para actualización de ubicación
    const LocationSettings locationSettings = LocationSettings(
      accuracy: LocationAccuracy.high,
      distanceFilter: 5, // Actualizar cada 5 metros
    );

    _positionStreamSubscription = Geolocator.getPositionStream(
      locationSettings: locationSettings,
    ).listen(
      (Position position) {
        setState(() {
          _currentLocationMarker = Marker(
            point: LatLng(position.latitude, position.longitude),
            width: 20,
            height: 20,
            child: Container(
              decoration: BoxDecoration(
                color: Colors.blue.withOpacity(0.7),
                shape: BoxShape.circle,
                border: Border.all(color: Colors.white, width: 2),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.2),
                    blurRadius: 4,
                    spreadRadius: 2,
                  ),
                ],
              ),
              child: const Center(
                child: Icon(
                  Icons.my_location,
                  color: Colors.white,
                  size: 12,
                ),
              ),
            ),
          );
        });

        // Centrar el mapa en la ubicación actual si es la primera vez
        if (_mapController != null && _isLocationEnabled) {
          _mapController.move(
            LatLng(position.latitude, position.longitude),
            18.0,
          );
        }
      },
      onError: (error) {
        print("Error obteniendo ubicación: $error");
        setState(() {
          _isLocationEnabled = false;
        });
      },
    );
  } else {
    _positionStreamSubscription?.cancel();
    setState(() {
      _isLocationEnabled = false;
      _currentLocationMarker = null;
    });
  }
}

  Future<void> _getCurrentLocation() async {
    _toggleLocationTracking();
  }

  void _addCurrentLocationMarker(Position position) {
    setState(() {
      _currentLocationMarker = Marker(
        point: LatLng(position.latitude, position.longitude),
        width: 20,
        height: 20,
        child: const Icon(
          Icons.circle,
          color: Colors.orange,
          size: 10,
        ),
      );
    });
  }

  Future<void> _saveToHistory() async {
  if (_startNode == null || _endNode == null || 
      widget.selectedBuilding == null || widget.selectedFloor == null) {
    return;
  }

  try {
    final prefs = await SharedPreferences.getInstance();
    final searchHistory = SearchHistory(
      building: widget.selectedBuilding!,
      floor: widget.selectedFloor!,
      startPoint: _startNode!,
      endPoint: _endNode!,
      timestamp: DateFormat('dd/MM/yyyy HH:mm').format(DateTime.now()),
    );

    // Obtener historial existente
    List<String> history = prefs.getStringList('search_history') ?? [];
    
    // Limitar el historial a 20 elementos
    if (history.length >= 20) {
      history.removeLast();
    }
    
    // Agregar nueva búsqueda al inicio
    history.insert(0, jsonEncode(searchHistory.toJson()));
    
    // Guardar el historial actualizado
    await prefs.setStringList('search_history', history);
    
  } catch (e) {
    print('Error al guardar en el historial: $e');
  }
}

  List<Map<String, dynamic>> _filterRooms() {
    // Asegurarse de que un piso esté seleccionado
    if (widget.selectedFloor == null) {
      return []; // Si no hay piso seleccionado, no devolver habitaciones
    }

    // Filtrar habitaciones según el edificio y el piso seleccionados
    return habitaciones.where((habitacion) {
      return (widget.selectedBuilding == null ||
              habitacion['edificio'] == widget.selectedBuilding) &&
          habitacion['piso'] == widget.selectedFloor;
    }).toList();
  }

void _calculateShortestPath() {
  if (_startNode != null && _endNode != null) {
    final path = nodosManager.calcularCaminoMasCorto(_startNode!, _endNode!);

    if (path.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('No se encontró un camino')),
      );
    } else {
      // Primero actualiza _pathCoordinates
      _pathCoordinates = path
          .map((id) => nodosManager.nodos[id]!['pos'] as LatLng)
          .toList();
      
      // Limpia los puntos animados
      setState(() {
        _animatedPathPoints = [];
      });
      
      // Ajusta la vista del mapa para mostrar toda la ruta
      _fitPathBounds();

      _saveToHistory();
      
      // Espera un momento antes de iniciar la animación para que el mapa se ajuste
      Future.delayed(const Duration(milliseconds: 300), () {
        // Reinicia y comienza la animación
        _animationController.reset();
        _animationController.forward();
      });
    }
  } else {
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(content: Text('Selecciona ambos nodos: inicio y fin')),
    );
  }
}

  void _fitPathBounds() {
    if (_pathCoordinates.isNotEmpty) {
      final bounds = LatLngBounds.fromPoints(_pathCoordinates);
      _mapController.fitBounds(
        bounds,
        options: const FitBoundsOptions(
          padding: EdgeInsets.all(50.0),
          maxZoom: 20.5,
        ),
      );
    }
  }

   double _calculateTotalDistance() {
    double total = 0;
    for (int i = 0; i < _pathCoordinates.length - 1; i++) {
      total += _calculateDistance(_pathCoordinates[i], _pathCoordinates[i + 1]);
    }
    return total;
  }

  // Función para calcular la distancia entre dos puntos
  double _calculateDistance(LatLng start, LatLng end) {
    const Distance distance = Distance();
    return distance.as(LengthUnit.Meter, start, end);
  }

  // Función para interpolar puntos basada en la distancia recorrida
  List<LatLng> _interpolatePoints(double targetDistance) {
    if (_pathCoordinates.isEmpty) return [];
    
    List<LatLng> result = [_pathCoordinates.first];
    double coveredDistance = 0;
    
    for (int i = 0; i < _pathCoordinates.length - 1; i++) {
      final start = _pathCoordinates[i];
      final end = _pathCoordinates[i + 1];
      final segmentDistance = _calculateDistance(start, end);
      
      if (coveredDistance + segmentDistance <= targetDistance) {
        result.add(end);
        coveredDistance += segmentDistance;
      } else {
        final remainingDistance = targetDistance - coveredDistance;
        final fraction = remainingDistance / segmentDistance;
        
        final interpolatedPoint = LatLng(
          start.latitude + (end.latitude - start.latitude) * fraction,
          start.longitude + (end.longitude - start.longitude) * fraction,
        );
        
        result.add(interpolatedPoint);
        break;
      }
    }
    
    return result;
  }

  @override
  Widget build(BuildContext context) {
    final filteredRooms = _filterRooms();

    // Filter nodes based on selected building and floor
    final filteredNodes =
        widget.selectedBuilding != null && widget.selectedFloor != null
            ? nodosManager.obtenerNodosPorEdificioYPiso(
                widget.selectedBuilding!, widget.selectedFloor!)
            : {};

    // Validar si el nodo de inicio y fin existen en los nodos filtrados, si no, reiniciarlos
    if (_startNode != null && !filteredNodes.containsKey(_startNode)) {
      setState(() {
        _startNode = null; // Reiniciar nodo de inicio
      });
    }
    if (_endNode != null && !filteredNodes.containsKey(_endNode)) {
      setState(() {
        _endNode = null; // Reiniciar nodo de fin
      });
    }

    // Si el edificio o el piso cambian, reiniciar también las coordenadas del path
    if (widget.selectedBuilding != previousSelectedBuilding ||
        widget.selectedFloor != previousSelectedFloor) {
      setState(() {
        _pathCoordinates = []; // Reiniciar las coordenadas del path
        _startNode = null; // Reiniciar el nodo de inicio
        _endNode = null; // Reiniciar el nodo de fin
      });
    }

    // Guardar el edificio y piso actuales para comparar en futuras actualizaciones
    previousSelectedBuilding = widget.selectedBuilding;
    previousSelectedFloor = widget.selectedFloor;

  return Scaffold(
    appBar: AppBar(
      backgroundColor: Colors.white,
      elevation: 0,
      flexibleSpace: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
        child: Row(
          children: [
            Expanded(
              child: Container(
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(15),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 2),
                    ),
                  ],
                ),
                
                child: Row(
                  children: [
                    Expanded(
                      child: Row(
                        children: [
                          Container(
                            width: 12,
                            height: 12,
                            margin: const EdgeInsets.only(left: 10, right: 8),
                            decoration: BoxDecoration(
                              color: Colors.green,
                              shape: BoxShape.circle,
                              border: Border.all(color: Colors.white, width: 2),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.1),
                                  blurRadius: 4,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                          ),
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              child: DropdownButtonHideUnderline(
                                child: DropdownButton<String>(
                                  value: _startNode,
                                  hint: Text(
                                    'Inicio',
                                    style: TextStyle(
                                      color: Colors.grey.shade600,
                                      fontFamily: 'Jost',
                                    ),
                                  ),
                                  isExpanded: true,
                                  icon: Icon(Icons.arrow_drop_down, color: Colors.blue.shade700),
                                  onChanged: (String? value) {
                                    setState(() {
                                      _startNode = value;
                                      _endNode = null;
                                      _pathCoordinates = [];
                                      _animatedPathPoints = [];
                                      _animationController.reset();
                                      // Centrar el mapa en el punto de origen si existe
                                      if (value != null && filteredNodes.containsKey(value)) {
                                        final startPosition = filteredNodes[value]!['pos'] as LatLng;
                                        _mapController.move(startPosition, 20); // El 19 es el nivel de zoom, puedes ajustarlo
                                      }
                                    });
                                  },
                                  items: filteredNodes.entries
                                      .where((entry) => entry.value['tipo'] == 'lugar')
                                      .map((entry) {
                                    return DropdownMenuItem<String>(
                                      value: entry.key,
                                      child: Container(
                                        constraints: BoxConstraints(
                                          maxWidth: MediaQuery.of(context).size.width * 0.35, // Ajusta este valor según necesites
                                        ),
                                        child: Text(
                                          entry.key,
                                          style: const TextStyle(
                                            fontFamily: 'Jost',
                                            fontSize: 14,
                                          ),
                                          overflow: TextOverflow.ellipsis, // Esto mostrará ... si el texto es muy largo
                                          maxLines: 1, // Puedes aumentar esto si quieres permitir múltiples líneas
                                        ),
                                      ),
                                    );
                                  }).toList(),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                    Container(
                      height: 24,
                      width: 1,
                      color: Colors.grey.shade300,
                    ),
                    Expanded(
                      child: Row(
                        children: [
                          Container(
                            width: 12,
                            height: 12,
                            margin: const EdgeInsets.only(left: 10, right: 8),
                            decoration: BoxDecoration(
                              color: Colors.red,
                              shape: BoxShape.circle,
                              border: Border.all(color: Colors.white, width: 2),
                              boxShadow: [
                                BoxShadow(
                                  color: Colors.black.withOpacity(0.1),
                                  blurRadius: 4,
                                  offset: const Offset(0, 2),
                                ),
                              ],
                            ),
                          ),
                          Expanded(
                            child: Container(
                              padding: const EdgeInsets.symmetric(horizontal: 12),
                              child: DropdownButtonHideUnderline(
                                child: DropdownButton<String>(
                                  value: _endNode,
                                  hint: Text(
                                    'Fin',
                                    style: TextStyle(
                                      color: Colors.grey.shade600,
                                      fontFamily: 'Jost',
                                    ),
                                  ),
                                  isExpanded: true,
                                  icon: Icon(Icons.arrow_drop_down, color: Colors.blue.shade700),
                                  onChanged: (String? value) {
                                    setState(() {
                                      _endNode = value;
                                      if (_startNode != null && value != null) {
                                        _calculateShortestPath();
                                      }
                                    });
                                  },
                                  items: filteredNodes.entries
                                      .where((entry) => entry.value['tipo'] == 'lugar')
                                      .map((entry) {
                                    return DropdownMenuItem<String>(
                                      value: entry.key,
                                      child: Container(
                                        constraints: BoxConstraints(
                                          maxWidth: MediaQuery.of(context).size.width * 0.35, // Ajusta este valor según necesites
                                        ),
                                        child: Text(
                                          entry.key,
                                          style: const TextStyle(
                                            fontFamily: 'Jost',
                                            fontSize: 14,
                                          ),
                                          overflow: TextOverflow.ellipsis, // Esto mostrará ... si el texto es muy largo
                                          maxLines: 1, // Puedes aumentar esto si quieres permitir múltiples líneas
                                        ),
                                      ),
                                    );
                                  }).toList(),
                                ),
                              ),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ),
            ),
            const SizedBox(width: 12),
            Container(
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(15),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.1),
                    blurRadius: 8,
                    offset: const Offset(0, 2),
                  ),
                ],
              ),
              child: IconButton(
                icon: Icon(Icons.search, color: Colors.blue.shade700),
                onPressed: _calculateShortestPath,
                tooltip: 'Buscar camino más corto',
              ),
            ),
          ],
        ),
      ),
    ),
    body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Container(
          decoration: BoxDecoration(
            color: Colors.white,
            borderRadius: BorderRadius.circular(20),
            boxShadow: [
              BoxShadow(
                color: Colors.black.withOpacity(0.1),
                blurRadius: 8,
                offset: const Offset(0, 2),
              ),
            ],
          ),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(20),
            child: Stack(
              children: [
                FlutterMap(
                  mapController: _mapController,
                  options: MapOptions(
                    initialCenter: LatLng(-36.830492703728666, -73.03684140759844),
                    initialZoom: 18,
                    minZoom: 5,  // Zoom mínimo permitido
                    maxZoom: 25, // Zoom máximo permitido
                    interactionOptions: const InteractionOptions(
                      flags: InteractiveFlag.all, // Habilita todas las interacciones
                      scrollWheelVelocity: 0.01, // Ajusta la velocidad del scroll (menor = más suave)
                    ),
                  ),
                  children: [
                    TileLayer(
                      urlTemplate: "https://tile.openstreetmap.org/{z}/{x}/{y}.png",
                      subdomains: const ['a', 'b', 'c'],
                    ),
                  PolygonLayer(
                    polygons: [
                      Polygon(
                        points: edificioCoords,
                        color: Colors.blue.withOpacity(0.3),
                        borderStrokeWidth: 2.0,
                        borderColor: Colors.blue,
                      ),
                    ],
                  ),
                  PolygonLayer(
                    polygons: [
                      Polygon(
                        points: edificio2Coords,
                        color: Colors.blue.withOpacity(0.3),
                        borderStrokeWidth: 2.0,
                        borderColor: Colors.blue,
                      ),
                    ],
                  ),
                  PolygonLayer(
                    polygons: filteredRooms
                        .map(
                          (hab) => Polygon(
                            points: hab['coords'],
                            color: Colors.yellow.withOpacity(0.3),
                            borderStrokeWidth: 2.0,
                            borderColor: Colors.orange,
                          ),
                        )
                        .toList(),
                  ),
                  if (_pathCoordinates.isNotEmpty) // Cambia la condición
                        PolylineLayer(
                          polylines: [
                            // Primero dibuja la línea fantasma
                            Polyline(
                              points: _pathCoordinates,
                              color: Colors.grey.withOpacity(0.5),
                              strokeWidth: 6.0,
                            ),
                            // Luego dibuja la línea animada encima
                            if (_animatedPathPoints.isNotEmpty)
                              Polyline(
                                points: _animatedPathPoints,
                                color: Colors.blue,
                                strokeWidth: 4.0,
                              ),
                          ],
                        ),
                    CircleLayer(
                      circles: filteredNodes.entries.map((entry) {
                        final LatLng posicion = entry.value['pos'];
                        final bool isStart = entry.key == _startNode;
                        final bool isEnd = entry.key == _endNode;

                        // Puntos especiales para inicio y fin
                        if (isStart || isEnd) {
                          return CircleMarker(
                            point: posicion,
                            radius: 8, // Más grande
                            color: isStart ? Colors.green.withOpacity(0.7) : Colors.red.withOpacity(0.7),
                            borderStrokeWidth: 2,
                            borderColor: Colors.white,
                            useRadiusInMeter: false,
                          );
                        }

                        // Puntos normales más pequeños
                        return CircleMarker(
                          point: posicion,
                          radius: 0,
                          color: Colors.blue.withOpacity(0.5),
                          useRadiusInMeter: false,
                        );
                      }).toList(),
                    ),

                  if (_currentLocationMarker != null)
                    MarkerLayer(
                      markers: [_currentLocationMarker!],
                    ),
                ],
              ),
Positioned(
  right: 16,
  bottom: 16,
  child: Container(
    decoration: BoxDecoration(
      color: Colors.white,
      borderRadius: BorderRadius.circular(30),
      boxShadow: [
        BoxShadow(
          color: Colors.black.withOpacity(0.1),
          blurRadius: 8,
          offset: const Offset(0, 2),
        ),
      ],
    ),
    child: IconButton(
      icon: Icon(
        _isLocationEnabled ? Icons.gps_fixed : Icons.gps_off,
        color: _isLocationEnabled ? Colors.blue.shade700 : Colors.grey,
      ),
      onPressed: _getCurrentLocation,
      iconSize: 28,
      tooltip: _isLocationEnabled ? 'Desactivar ubicación' : 'Activar ubicación',
    ),
  ),
),
            ],
          ),
        ),
      ),
    ),
    );
  }
}