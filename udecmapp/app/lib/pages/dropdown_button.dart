import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import '../config/api_config.dart';

class DropDownButton extends StatefulWidget {
  final Size screenSize;
  final double ratio;

  const DropDownButton(
      {super.key, required this.screenSize, required this.ratio});

  @override
  _DropDownButtonState createState() => _DropDownButtonState();
}

class _DropDownButtonState extends State<DropDownButton> {
  String? selectedBuilding;
  String? selectedFloor;
  List<String> buildingOptions = ['Seleccionar Edificio'];
  List<String> floorOptions = [];

  @override
  void initState() {
    super.initState();
    fetchBuildings();
  }

  Future<void> fetchBuildings() async {
    try {
      final url = ApiConfig.edificiosUrl;
      print('Intentando obtener edificios desde: $url');
      
      final response = await http.get(Uri.parse(url));
      print('Respuesta edificios - Status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        List<dynamic> buildings = jsonDecode(response.body);
        print('Edificios recibidos: ${buildings.length}');
        
        setState(() {
          buildingOptions = ['Seleccionar Edificio'] +
              buildings
                  .map((building) => building['nombre'] as String)
                  .toList();
        });
        print('Edificios disponibles: $buildingOptions');
      } else {
        print('Error al obtener edificios: ${response.statusCode}');
        print('Respuesta: ${response.body}');
      }
    } catch (e) {
      print('Error al conectar con el servidor: $e');
      print('Stack trace: ${StackTrace.current}');
    }
  }

  Future<void> fetchFloors(String buildingId) async {
    try {
      final url = ApiConfig.pisosUrl(buildingId);
      print('Intentando obtener pisos desde: $url');
      
      final response = await http.get(Uri.parse(url));
      print('Respuesta pisos - Status: ${response.statusCode}');
      
      if (response.statusCode == 200) {
        List<dynamic> floors = jsonDecode(response.body);
        print('Pisos recibidos: ${floors.length}');
        
        setState(() {
          floorOptions = floors.isNotEmpty
              ? floors.map((floor) => floor['numero_piso'] as String).toList()
              : ['No hay pisos'];
        });
        print('Pisos disponibles: $floorOptions');
      } else {
        print('Error al obtener pisos: ${response.statusCode}');
        print('Respuesta: ${response.body}');
      }
    } catch (e) {
      print('Error al conectar con el servidor: $e');
      print('Stack trace: ${StackTrace.current}');
    }
  }


  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Primera lista desplegable: Seleccionar Edificio
        Container(
          padding: EdgeInsets.symmetric(
            horizontal: widget.screenSize.width * 0.07 * widget.ratio,
            vertical: widget.screenSize.height * 0.02 * widget.ratio,
          ),
          decoration: BoxDecoration(
            color: const Color(0xFFD9E6FF),
            borderRadius: BorderRadius.circular(18),
            boxShadow: const [
              BoxShadow(
                color: Colors.black38,
                blurRadius: 6,
                offset: Offset(0, 3),
              ),
            ],
            border: Border.all(color: Colors.black),
          ),
          child: DropdownButtonHideUnderline(
            child: DropdownButton<String>(
              value: selectedBuilding,
              hint: Text(
                "Seleccionar Edificio",
                style: TextStyle(
                  fontFamily: 'Jost',
                  fontSize: widget.screenSize.width * 0.06 * widget.ratio,
                  color: Colors.black,
                ),
              ),
              isExpanded: true,
              icon: Icon(
                Icons.keyboard_arrow_down,
                size: widget.screenSize.width * 0.08 * widget.ratio,
                color: Colors.black54,
              ),
              style: TextStyle(
                fontFamily: 'Jost',
                fontSize: widget.screenSize.width * 0.06 * widget.ratio,
                color: Colors.black,
              ),
              dropdownColor: const Color(0xFFD9E6FF),
              alignment: Alignment.centerLeft,
              menuMaxHeight: widget.screenSize.height * 0.3,
              onChanged: (String? newValue) {
                if (newValue != 'Seleccionar Edificio') {
                  setState(() {
                    selectedBuilding = newValue;
                    selectedFloor = null; // Resetear piso seleccionado
                  });
                  // Pasar directamente el nombre del edificio
                  fetchFloors(newValue!);
                }
              },
              items:
                  buildingOptions.map<DropdownMenuItem<String>>((String value) {
                return DropdownMenuItem<String>(
                  value: value,
                  alignment: Alignment.centerLeft,
                  child: Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8.0),
                    child: Text(value),
                  ),
                );
              }).toList(),
            ),
          ),
        ),

        const SizedBox(height: 16),

        // Segunda lista desplegable: Seleccionar Piso
        if (selectedBuilding != null &&
            selectedBuilding != 'Seleccionar Edificio')
          Container(
            padding: EdgeInsets.symmetric(
              horizontal: widget.screenSize.width * 0.07 * widget.ratio,
              vertical: widget.screenSize.height * 0.02 * widget.ratio,
            ),
            decoration: BoxDecoration(
              color: const Color(0xFFD9E6FF),
              borderRadius: BorderRadius.circular(18),
              boxShadow: const [
                BoxShadow(
                  color: Colors.black38,
                  blurRadius: 6,
                  offset: Offset(0, 3),
                ),
              ],
              border: Border.all(color: Colors.black),
            ),
            child: DropdownButtonHideUnderline(
              child: DropdownButton<String>(
                value: selectedFloor,
                hint: Text(
                  "Seleccionar Piso",
                  style: TextStyle(
                    fontFamily: 'Jost',
                    fontSize: widget.screenSize.width * 0.06 * widget.ratio,
                    color: Colors.black,
                  ),
                ),
                isExpanded: true,
                icon: Icon(
                  Icons.keyboard_arrow_down,
                  size: widget.screenSize.width * 0.08 * widget.ratio,
                  color: Colors.black54,
                ),
                style: TextStyle(
                  fontFamily: 'Jost',
                  fontSize: widget.screenSize.width * 0.06 * widget.ratio,
                  color: Colors.black,
                ),
                dropdownColor: const Color(0xFFD9E6FF),
                alignment: Alignment.centerLeft,
                menuMaxHeight: widget.screenSize.height * 0.3,
                onChanged: (String? newValue) {
                  setState(() {
                    selectedFloor = newValue;
                  });
                },
                items:
                    floorOptions.map<DropdownMenuItem<String>>((String value) {
                  return DropdownMenuItem<String>(
                    value: value,
                    alignment: Alignment.centerLeft,
                    child: Padding(
                      padding: const EdgeInsets.symmetric(vertical: 8.0),
                      child: Text(value),
                    ),
                  );
                }).toList(),
              ),
            ),
          ),
      ],
    );
  }
}
  