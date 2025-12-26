import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:shared_preferences/shared_preferences.dart';

class ApiConfig {

  static String _baseUrl = 'http://localhost:5000'; // Varsayılan
  static const String _savedIpKey = 'saved_server_ip';

  static String get baseUrl => _baseUrl;

  // Başlangıçta çağrılmalı - uygulamayı hangi platform'da çalıştığını kontrol et
  static Future<void> initializeBaseUrl({String? customUrl}) async {
    if (customUrl != null) {
      _baseUrl = customUrl;
      return;
    }

    // Kaydedilmiş IP var mı kontrol et
    final savedIp = await getSavedIp();
    if (savedIp != null && savedIp.isNotEmpty) {
      _baseUrl = 'http://$savedIp:5000';
      return;
    }

    // Platform kontrolü
    if (kIsWeb) {
      // Web (Chrome, Firefox vb.)
      _baseUrl = 'http://localhost:5000';
    } else if (Platform.isAndroid) {
      // Android emülatörü
      _baseUrl = 'http://10.0.2.2:5000';
    } else if (Platform.isIOS) {
      // iOS cihaz - aşağıdaki IP adresleri manuel ayarlanmalı
      _baseUrl = 'http://192.168.1.100:5000'; // iOS cihaz için
    } else {
      _baseUrl = 'http://localhost:5000';
    }
  }


  static void setCustomUrl(String url) {
    _baseUrl = url;
  }


  static Future<void> saveIp(String ip) async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_savedIpKey, ip);
    _baseUrl = 'http://$ip:5000';
  }


  static Future<String?> getSavedIp() async {
    final prefs = await SharedPreferences.getInstance();
    return prefs.getString(_savedIpKey);
  }


  static Future<void> clearSavedIp() async {
    final prefs = await SharedPreferences.getInstance();
    await prefs.remove(_savedIpKey);
  }


  static void printConfig() {
    print('🔌 API Base URL: $_baseUrl');
    print('🌐 Is Web: $kIsWeb');
    if (!kIsWeb) {
      print('📱 Platform: ${Platform.operatingSystem}');
    }
  }
}
