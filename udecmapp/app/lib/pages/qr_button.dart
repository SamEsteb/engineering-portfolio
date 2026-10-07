import 'package:flutter/material.dart';
import 'package:barcode_scan2/barcode_scan2.dart';

class QRButton extends StatelessWidget {
  final double width;
  final double height;

  const QRButton({
    super.key,
    required this.width,
    required this.height,
  });

  Future<void> _scanQRCode(BuildContext context) async {
    try {
      var scanResult = await BarcodeScanner.scan();
      if (scanResult.rawContent.isNotEmpty) {
        // Muestra el contenido del QR o maneja la información escaneada
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('QR Content: ${scanResult.rawContent}')),
        );
      }
    } catch (e) {
      // Maneja errores
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Error al escanear QR: $e')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Container(
      width: width,
      height: height,
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
          onTap: () => _scanQRCode(context),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(Icons.qr_code_scanner, color: Colors.blue.shade700, size: 24),
              const SizedBox(width: 8),
              Text(
                'QR',
                style: TextStyle(
                  fontFamily: 'Jost',
                  fontSize: 16,
                  color: Colors.blue.shade700,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}