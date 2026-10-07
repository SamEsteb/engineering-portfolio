import 'package:flutter_dotenv/flutter_dotenv.dart';

/// Centralized API configuration for endpoints and base URLs.
class ApiConfig {
  /// Base URL for the backend API, loaded from .env or fallback
  static String get baseUrl =>
      dotenv.env['API_BASE_URL'] ?? 'LOCALHOST_EXAMPLE';

  // Endpoint builders
  static String get edificiosUrl => '$baseUrl/edificios';
  
  static String pisosUrl(String buildingId) =>
      '$baseUrl/edificios/${Uri.encodeComponent(buildingId)}/pisos';

  static String nodosUrl(String edificio, String piso) =>
      '$baseUrl/nodos/${Uri.encodeComponent(edificio)}/${Uri.encodeComponent(piso)}';

  static String habitacionesUrl(String edificio, String piso) =>
      '$baseUrl/habitaciones/${Uri.encodeComponent(edificio)}/${Uri.encodeComponent(piso)}';
}
