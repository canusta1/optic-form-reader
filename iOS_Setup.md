# iOS ve Emülatör Kurulumu

## Android Emülatörü
- Backend IP: `10.0.2.2:5000` (otomatik)
- Sistem tüm istekleri bu adrese yönlendirir

## iOS Cihazı

### 1. Host Makinenin IP'sini Öğren
```powershell
ipconfig
```
IPv4 Adresini bul (örn: `192.168.1.100`)

### 2. iOS Cihazın Backend'e Erişmesi
İOS cihazı Flutter uygulamayı çalıştırırken:

```bash
flutter run -d <device_id> --dart-define=API_URL=http://192.168.1.100:5000
```

Veya uygulama içinde manuel olarak ayarla:
```dart
ApiConfig.setCustomUrl('http://192.168.1.100:5000');
```

### 3. Backend'in Dinlemesini Kontrol Et
Backend'in `app.py` dosyasında bu satırı kontrol et:
```python
app.run(debug=True, host='0.0.0.0', port=5000)
```
`0.0.0.0` tüm ağ arayüzlerinde dinlediğini gösterir ✓

### 4. Firewall Kontrol
Windows Firewall'da Flask (5000 portu) için izin ver:
1. Windows Defender Firewall → İleri Güvenlik
2. Gelen Kuralları → Yeni Kural
3. Program: Python.exe seç
4. Port: 5000 açık

### 5. Test
iOS cihazda tarayıcıda test et:
```
http://<HOST_IP>:5000/form-templates
```
JSON cevabı alırsan ✓ çalışıyor

## Sorun Giderme

**Emülatörde "Connection refused":**
- Backend'in çalışıyor olduğundan emin ol
- `flutter clean && flutter pub get` çalıştır

**iOS'ta erişilemiyor:**
- Aynı WiFi'de olduğundan emin ol
- IP adresi doğru mu kontrol et
- Firewall'da izin ver

**Response'lar 0 gösteriliyor:**
- Backend'in doğru endpoint'ler dönüyor mu kontrol et
- `backend/app.py` de debug mode aktif mı bak
- Network tab'ında (Dev Tools) cevapları gözle
