import 'package:flutter/material.dart';
import 'package:udecmapp/screens/history.dart';
import 'package:udecmapp/screens/contacts.dart';

class MenuButton extends StatefulWidget {
  final double width;
  final double height;
  final double screenWidth;
  final double ratio;

  const MenuButton({
    super.key,
    required this.width,
    required this.height,
    required this.screenWidth,
    required this.ratio,
  });

  @override
  _MenuButtonState createState() => _MenuButtonState();
}

class _MenuButtonState extends State<MenuButton> {
  late OverlayEntry _overlayEntry;
  bool _isMenuOpen = false;

  @override
  void dispose() {
    if (_isMenuOpen) {
      _overlayEntry.remove();
    }
    super.dispose();
  }

  void _showMenu(BuildContext context) {
    _overlayEntry = _createOverlayEntry(context);
    Overlay.of(context).insert(_overlayEntry);
    setState(() {
      _isMenuOpen = true;
    });
  }

  void _closeMenu(BuildContext context) {
    _overlayEntry.remove();
    setState(() {
      _isMenuOpen = false;
    });
  }

  void _navigateToScreen(BuildContext context, Widget screen) {
    _closeMenu(context);
    Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => screen),
    );
  }

  OverlayEntry _createOverlayEntry(BuildContext context) {
    final renderBox = context.findRenderObject() as RenderBox;
    final buttonPosition = renderBox.localToGlobal(Offset.zero);
    final buttonSize = renderBox.size;

    return OverlayEntry(
      builder: (context) => Stack(
        children: [
          Positioned.fill(
            child: GestureDetector(
              onTap: () => _closeMenu(context),
              child: Container(
                color: Colors.black12.withOpacity(0.1),
              ),
            ),
          ),
          Positioned(
            top: buttonPosition.dy + buttonSize.height + 8,
            left: buttonPosition.dx,
            child: Material(
              color: Colors.transparent,
              child: Container(
                width: widget.screenWidth * 0.85,
                decoration: BoxDecoration(
                  color: Colors.white,
                  borderRadius: BorderRadius.circular(15),
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 8,
                      offset: const Offset(0, 4),
                    ),
                  ],
                ),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    _buildMenuOption(
                      Icons.history,
                      'Historial',
                      context,
                      () => _navigateToScreen(context, const HistoryScreen()),
                    ),
                    const Divider(height: 1),
                    _buildMenuOption(
                      Icons.person,
                      'Contacto',
                      context,
                      () => _navigateToScreen(context, const ContactScreen()),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildMenuOption(
    IconData icon,
    String text,
    BuildContext context,
    VoidCallback onTap,
  ) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            Icon(
              icon,
              color: Colors.blue.shade700,
              size: 24,
            ),
            const SizedBox(width: 12),
            Text(
              text,
              style: TextStyle(
                fontFamily: 'Jost',
                fontSize: 16,
                color: Colors.grey.shade800,
              ),
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: widget.width,
      height: widget.height,
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
      child: Material(
        color: Colors.transparent,
        child: InkWell(
          borderRadius: BorderRadius.circular(15),
          onTap: () {
            _isMenuOpen ? _closeMenu(context) : _showMenu(context);
          },
          child: Icon(
            _isMenuOpen ? Icons.close : Icons.menu,
            color: Colors.blue.shade700,
            size: 24,
          ),
        ),
      ),
    );
  }
}