import 'dart:convert';
import 'package:http/http.dart' as http;
import 'api_config.dart';

class AuthService {
  static String get baseUrl => ApiConfig.baseUrl;
  static String? _token;
  static Map<String, dynamic>? _currentUser;

  static String? get token => _token;
  static Map<String, dynamic>? get currentUser => _currentUser;
  static bool get isLoggedIn => _token != null;

  // Login işlemi
  static Future<Map<String, dynamic>> login(
      String username, String password) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/login'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'password': password,
        }),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        _token = data['token'];
        _currentUser = data['user'];
        return {'success': true, 'message': 'Giriş başarılı'};
      } else {
        final error = json.decode(response.body);
        return {
          'success': false,
          'message': error['error'] ?? 'Giriş başarısız'
        };
      }
    } catch (e) {
      return {'success': false, 'message': 'Bağlantı hatası: $e'};
    }
  }

  // Kayıt işlemi
  static Future<Map<String, dynamic>> register(
    String username,
    String email,
    String password,
    String fullName,
  ) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/register'),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({
          'username': username,
          'email': email,
          'password': password,
          'full_name': fullName,
        }),
      );

      if (response.statusCode == 201) {
        return {'success': true, 'message': 'Kayıt başarılı'};
      } else {
        final error = json.decode(response.body);
        return {
          'success': false,
          'message': error['error'] ?? 'Kayıt başarısız'
        };
      }
    } catch (e) {
      return {'success': false, 'message': 'Bağlantı hatası: $e'};
    }
  }

  // Çıkış işlemi
  static void logout() {
    _token = null;
    _currentUser = null;
  }

  // Auth header'ı için
  static Map<String, String> getAuthHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': 'Bearer $_token',
    };
  }
}
