import 'dart:io';
import 'package:flutter/foundation.dart' show kIsWeb;

class ApiConfig {
  // Değiştirebilecek değişkenler
  static String _baseUrl = 'http://localhost:5000'; // Varsayılan

  static String get baseUrl => _baseUrl;

  // Başlangıçta çağrılmalı - uygulamayı hangi platform'da çalıştığını kontrol et
  static void initializeBaseUrl({String? customUrl}) {
    if (customUrl != null) {
      _baseUrl = customUrl;
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
      _baseUrl =
          'http://192.168.1.100:5000'; // Bu değeri cihazın IP'si ile değiştir
    } else {
      _baseUrl = 'http://localhost:5000';
    }
  }

  // iOS cihazlar için manuel IP ayarla
  static void setCustomUrl(String url) {
    _baseUrl = url;
  }

  // Geçerli IP'yi debug için yazdır
  static void printConfig() {
    print('🔌 API Base URL: $_baseUrl');
    print('🌐 Is Web: $kIsWeb');
    if (!kIsWeb) {
      print('📱 Platform: ${Platform.operatingSystem}');
    }
  }
}
