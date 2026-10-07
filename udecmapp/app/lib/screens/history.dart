import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';
import 'dart:convert';
import 'search_history.dart';

class HistoryScreen extends StatefulWidget {
  const HistoryScreen({super.key});

  @override
  _HistoryScreenState createState() => _HistoryScreenState();
}

class _HistoryScreenState extends State<HistoryScreen> {
  List<SearchHistory> _searchHistory = [];

  @override
  void initState() {
    super.initState();
    _loadSearchHistory();
  }

  Future<void> _loadSearchHistory() async {
    try {
      final prefs = await SharedPreferences.getInstance();
      final historyJson = prefs.getStringList('search_history') ?? [];
      setState(() {
        _searchHistory = historyJson
            .map((item) => SearchHistory.fromJson(json.decode(item)))
            .toList();
      });
    } catch (e) {
      print('Error al cargar el historial: $e');
    }
  }

  Future<void> _clearHistory() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove('search_history');
    setState(() {
      _searchHistory = [];
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Historial de Búsqueda',
          style: TextStyle(
            fontFamily: 'Jost',
            color: Colors.black,
          ),
        ),
        backgroundColor: const Color(0xFFD9E6FF),
        iconTheme: const IconThemeData(color: Colors.black),
        actions: [
          if (_searchHistory.isNotEmpty)
            IconButton(
              icon: const Icon(Icons.delete_outline),
              onPressed: () {
                showDialog(
                  context: context,
                  builder: (context) => AlertDialog(
                    title: const Text('Limpiar historial'),
                    content: const Text('¿Estás seguro de que deseas eliminar todo el historial?'),
                    actions: [
                      TextButton(
                        onPressed: () => Navigator.pop(context),
                        child: const Text('Cancelar'),
                      ),
                      TextButton(
                        onPressed: () {
                          _clearHistory();
                          Navigator.pop(context);
                        },
                        child: const Text('Eliminar'),
                      ),
                    ],
                  ),
                );
              },
              tooltip: 'Limpiar historial',
            ),
        ],
      ),
      body: _searchHistory.isEmpty
          ? Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(
                    Icons.history,
                    size: 64,
                    color: Colors.grey[400],
                  ),
                  const SizedBox(height: 16),
                  Text(
                    'No hay historial de búsqueda',
                    style: TextStyle(
                      fontFamily: 'Jost',
                      fontSize: 16,
                      color: Colors.grey[600],
                    ),
                  ),
                ],
              ),
            )
          : ListView.builder(
              itemCount: _searchHistory.length,
              itemBuilder: (context, index) {
                final search = _searchHistory[index];
                return Container(
                  margin: const EdgeInsets.symmetric(
                    horizontal: 16,
                    vertical: 8,
                  ),
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
                  child: ListTile(
                    leading: Container(
                      padding: const EdgeInsets.all(8),
                      decoration: BoxDecoration(
                        color: const Color(0xFFD9E6FF),
                        borderRadius: BorderRadius.circular(10),
                      ),
                      child: const Icon(
                        Icons.location_on_outlined,
                        color: Colors.black,
                      ),
                    ),
                    title: Text(
                      '${search.building} - ${search.floor}',
                      style: const TextStyle(
                        fontFamily: 'Jost',
                        fontWeight: FontWeight.w500,
                      ),
                    ),
                    subtitle: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          'De: ${search.startPoint}',
                          style: TextStyle(
                            fontFamily: 'Jost',
                            color: Colors.grey[600],
                          ),
                        ),
                        Text(
                          'A: ${search.endPoint}',
                          style: TextStyle(
                            fontFamily: 'Jost',
                            color: Colors.grey[600],
                          ),
                        ),
                        Text(
                          search.timestamp,
                          style: TextStyle(
                            fontFamily: 'Jost',
                            color: Colors.grey[500],
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                    trailing: Icon(
                      Icons.arrow_forward_ios,
                      size: 16,
                      color: Colors.grey[400],
                    ),
                    onTap: () {
                      // Aquí puedes implementar la navegación a la ruta guardada
                      Navigator.pop(context, {
                        'building': search.building,
                        'floor': search.floor,
                        'startPoint': search.startPoint,
                        'endPoint': search.endPoint,
                      });
                    },
                  ),
                );
              },
            ),
    );
  }
}