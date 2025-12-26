import 'dart:convert';
import 'package:http/http.dart' as http;
import 'auth_service.dart';
import 'api_config.dart';

class FormService {
  static String get baseUrl => ApiConfig.baseUrl;

  static Future<List<Map<String, dynamic>>> getFormTemplates() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/form-templates'),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return List<Map<String, dynamic>>.from(data['templates'] ?? []);
      }
      return [];
    } catch (e) {
      print('Form şablonları yüklenemedi: $e');
      return [];
    }
  }

  static Future<Map<String, dynamic>> createAnswerKey(
    String examName,
    String schoolType,
    List<Map<String, dynamic>> subjects, {
    String formTemplate = 'simple',
  }) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/answer-keys'),
        headers: AuthService.getAuthHeaders(),
        body: json.encode({
          'exam_name': examName,
          'school_type': schoolType,
          'form_template': formTemplate,
          'subjects': subjects,
        }),
      );

      if (response.statusCode == 201) {
        return json.decode(response.body);
      } else {
        final error = json.decode(response.body);
        return {'success': false, 'error': error['error']};
      }
    } catch (e) {
      return {'success': false, 'error': 'Bağlantı hatası: $e'};
    }
  }

  static Future<List<dynamic>> getAnswerKeys() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/answer-keys'),
        headers: AuthService.getAuthHeaders(),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['answer_keys'] ?? [];
      }
      return [];
    } catch (e) {
      print('Error fetching answer keys: $e');
      return [];
    }
  }

  static Future<Map<String, dynamic>?> getAnswerKeyDetail(
      int answerKeyId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/answer-keys/$answerKeyId'),
        headers: AuthService.getAuthHeaders(),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['answer_key'];
      }
      return null;
    } catch (e) {
      print('Error fetching answer key detail: $e');
      return null;
    }
  }

  static Future<List<dynamic>> getResults(int answerKeyId) async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/results/$answerKeyId'),
        headers: AuthService.getAuthHeaders(),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['results'] ?? [];
      }
      return [];
    } catch (e) {
      print('Error fetching results: $e');
      return [];
    }
  }

  static Future<List<dynamic>> getAllResults() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/all-results'),
        headers: AuthService.getAuthHeaders(),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        return data['results'] ?? [];
      }
      return [];
    } catch (e) {
      print('Error fetching all results: $e');
      return [];
    }
  }
}
