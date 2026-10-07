import 'package:flutter/material.dart';
import 'menu_button.dart';
import 'qr_button.dart';
import 'chatbot_button.dart';
import 'map_view.dart';

const double ratio = 0.89;

class MainMenu extends StatefulWidget {
  const MainMenu({super.key});

  @override
  _MainMenuState createState() => _MainMenuState();
}

class _MainMenuState extends State<MainMenu> {
  String? selectedBuilding;
  String? selectedFloor;
  bool isSearching = false;

  final Map<String, List<String>> buildingFloors = {
    'EDIFICIO 1': ['Piso 1', 'Piso 2', 'Piso 3'],
    'EDIFICIO 2': ['Piso 1', 'Piso 2', 'Piso 3'],
  };

  @override
  Widget build(BuildContext context) {
    final screenSize = MediaQuery.of(context).size;
    final double buttonHeight = screenSize.height * 0.06;
    final double logoSize = screenSize.width * 0.1;

    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              Colors.blue.shade50,
              Colors.white,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              // Modern App Bar
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Row(
                  children: [
                    MenuButton(
                      width: buttonHeight,
                      height: buttonHeight,
                      screenWidth: screenSize.width,
                      ratio: ratio,
                    ),
                    const SizedBox(width: 16),
                    Expanded(
                      child: Container(
                        height: buttonHeight,
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
                        child: Row(
                          children: [
                            Expanded(
                              child: TextField(
                                decoration: InputDecoration(
                                  hintText: 'Buscar edificio...',
                                  border: InputBorder.none,
                                  contentPadding: const EdgeInsets.symmetric(horizontal: 16),
                                  hintStyle: TextStyle(
                                    fontFamily: 'Jost',
                                    color: Colors.grey.shade600,
                                  ),
                                ),
                              ),
                            ),
                            IconButton(
                              icon: const Icon(Icons.search),
                              onPressed: () {},
                              color: Colors.blue.shade700,
                            ),
                          ],
                        ),
                      ),
                    ),
                    const SizedBox(width: 16),
                    Container(
                      child: Image.asset(
                        'assets/image 4.png',
                        width: logoSize,
                        height: logoSize,
                      ),
                    ),
                  ],
                ),
              ),

              // Action Buttons
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
                child: Row(
                  children: [
                    Expanded(
                      child: QRButton(
                        width: screenSize.width * 0.4,
                        height: buttonHeight,
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: ChatBotButton(
                        width: screenSize.width * 0.4,
                        height: buttonHeight,
                      ),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 16),

              // Building Selection
              Padding(
                padding: const EdgeInsets.symmetric(horizontal: 16.0),
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
                  child: _buildDropdown(
                    value: selectedBuilding,
                    hint: 'Seleccione un edificio',
                    items: buildingFloors.keys.toList(),
                    onChanged: (value) {
                      setState(() {
                        selectedBuilding = value;
                        selectedFloor = null;
                      });
                    },
                  ),
                ),
              ),

              if (selectedBuilding != null) ...[
                const SizedBox(height: 12),
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 16.0),
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
                    child: _buildDropdown(
                      value: selectedFloor,
                      hint: 'Seleccione un piso',
                      items: buildingFloors[selectedBuilding]!,
                      onChanged: (value) {
                        setState(() {
                          selectedFloor = value;
                        });
                      },
                    ),
                  ),
                ),
              ],

              // Map View
              Expanded(
                child: Padding(
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
                      child: MapView(
                        selectedBuilding: selectedBuilding,
                        selectedFloor: selectedFloor,
                      ),
                    ),
                  ),
                ),
              ),

              // Location Info
              Padding(
                padding: const EdgeInsets.all(16.0),
                child: Container(
                  padding: const EdgeInsets.all(16),
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
                  child: Row(
                    children: [
                      Container(
                        width: 48,
                        height: 48,
                        decoration: const BoxDecoration(
                          color: Colors.orange,
                          shape: BoxShape.circle,
                        ),
                        child: const Icon(
                          Icons.location_on,
                          color: Colors.white,
                        ),
                      ),
                      const SizedBox(width: 16),
                      Expanded(
                        child: Text(
                          'Se encuentra en este lugar',
                          style: TextStyle(
                            fontFamily: 'Jost',
                            fontSize: 16,
                            color: Colors.grey.shade800,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildDropdown({
    required String? value,
    required String hint,
    required List<String> items,
    required Function(String?) onChanged,
  }) {
    return DropdownButtonHideUnderline(
      child: ButtonTheme(
        alignedDropdown: true,
        child: DropdownButton<String>(
          value: value,
          hint: Text(
            hint,
            style: TextStyle(
              fontFamily: 'Jost',
              color: Colors.grey.shade600,
            ),
          ),
          isExpanded: true,
          icon: const Icon(Icons.arrow_drop_down),
          style: const TextStyle(
            fontFamily: 'Jost',
            color: Colors.black,
            fontSize: 16,
          ),
          onChanged: onChanged,
          items: items.map<DropdownMenuItem<String>>((String value) {
            return DropdownMenuItem<String>(
              value: value,
              child: Text(value),
            );
          }).toList(),
        ),
      ),
    );
  }
}