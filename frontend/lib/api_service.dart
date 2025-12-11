import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  final String baseUrl = 'http://127.0.0.1:14300';

  Future<bool> checkHealth() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/health'));
      if (response.statusCode == 200) {
        return true;
      }
    } catch (e) {
      // Ignore connection errors, server might be starting
    }
    return false;
  }

  Future<Map<String, dynamic>> checkGrammar(String text) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/check'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({'text': text}),
      );

      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      } else {
        throw Exception('Failed to check grammar: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Connection error: $e');
    }
  }
}
