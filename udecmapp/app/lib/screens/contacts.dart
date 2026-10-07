import 'package:flutter/material.dart';
import 'package:url_launcher/url_launcher.dart';

class ContactScreen extends StatelessWidget {
  const ContactScreen({super.key});

  Future<void> _launchURL(String url) async {
    if (await canLaunchUrl(Uri.parse(url))) {
      await launchUrl(Uri.parse(url));
    } else {
      throw 'No se pudo abrir $url';
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text(
          'Contacto',
          style: TextStyle(
            fontFamily: 'Jost',
            color: Colors.black,
          ),
        ),
        backgroundColor: const Color(0xFFD9E6FF),
        iconTheme: const IconThemeData(color: Colors.black),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Información de Contacto',
              style: TextStyle(
                fontFamily: 'Jost',
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 24),
            _buildContactCard(
              icon: Icons.location_on_outlined,
              title: 'Dirección',
              subtitle: 'Av. Universidad 1234, Ciudad Universitaria',
              onTap: () => _launchURL('https://maps.google.com'),
            ),
            _buildContactCard(
              icon: Icons.phone_outlined,
              title: 'Teléfono',
              subtitle: '+56 9 1234 5678',
              onTap: () => _launchURL('tel:+56912345678'),
            ),
            _buildContactCard(
              icon: Icons.email_outlined,
              title: 'Email',
              subtitle: 'contacto@ejemplo.com',
              onTap: () => _launchURL('mailto:contacto@ejemplo.com'),
            ),
            _buildContactCard(
              icon: Icons.web_outlined,
              title: 'Sitio Web',
              subtitle: 'www.ejemplo.com',
              onTap: () => _launchURL('https://www.ejemplo.com'),
            ),
            const SizedBox(height: 32),
            const Text(
              'Redes Sociales',
              style: TextStyle(
                fontFamily: 'Jost',
                fontSize: 24,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceEvenly,
              children: [
                _buildSocialButton(
                  icon: Icons.facebook,
                  color: Colors.blue,
                  onTap: () => _launchURL('https://facebook.com/ejemplo'),
                ),
                _buildSocialButton(
                  icon: Icons.camera_alt_outlined,
                  color: Colors.purple,
                  onTap: () => _launchURL('https://instagram.com/ejemplo'),
                ),
                _buildSocialButton(
                  icon: Icons.telegram,
                  color: Colors.blue.shade700,
                  onTap: () => _launchURL('https://twitter.com/ejemplo'),
                ),
                _buildSocialButton(
                  icon: Icons.video_library_outlined,
                  color: Colors.red,
                  onTap: () => _launchURL('https://youtube.com/ejemplo'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildContactCard({
    required IconData icon,
    required String title,
    required String subtitle,
    required VoidCallback onTap,
  }) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
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
        contentPadding: const EdgeInsets.all(16),
        leading: Container(
          padding: const EdgeInsets.all(12),
          decoration: BoxDecoration(
            color: const Color(0xFFD9E6FF),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Icon(icon, color: Colors.black),
        ),
        title: Text(
          title,
          style: const TextStyle(
            fontFamily: 'Jost',
            fontWeight: FontWeight.w500,
            fontSize: 18,
          ),
        ),
        subtitle: Padding(
          padding: const EdgeInsets.only(top: 8),
          child: Text(
            subtitle,
            style: TextStyle(
              fontFamily: 'Jost',
              color: Colors.grey[600],
              fontSize: 16,
            ),
          ),
        ),
        onTap: onTap,
      ),
    );
  }

  Widget _buildSocialButton({
    required IconData icon,
    required Color color,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.all(12),
        decoration: BoxDecoration(
          color: Colors.white,
          borderRadius: BorderRadius.circular(12),
          boxShadow: [
            BoxShadow(
              color: Colors.black.withOpacity(0.1),
              blurRadius: 8,
              offset: const Offset(0, 2),
            ),
          ],
        ),
        child: Icon(
          icon,
          color: color,
          size: 32,
        ),
      ),
    );
  }
}