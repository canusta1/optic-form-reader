import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'auth_service.dart';
import 'form_service.dart';

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  XFile? _image;
  Uint8List? _imageBytes;
  bool _loading = false;
  Map<String, dynamic>? _result;
  final ImagePicker _picker = ImagePicker();

  List<dynamic> _answerKeys = [];
  int? _selectedAnswerKeyId;
  bool _loadingAnswerKeys = false;

  @override
  void initState() {
    super.initState();
    _loadAnswerKeys();
  }

  Future<void> _loadAnswerKeys() async {
    setState(() => _loadingAnswerKeys = true);
    try {
      final keys = await FormService.getAnswerKeys();
      setState(() {
        _answerKeys = keys;
        _loadingAnswerKeys = false;
      });
    } catch (e) {
      if (mounted) {
        setState(() => _loadingAnswerKeys = false);
      }
    }
  }

  Future<void> _pickImage(ImageSource source) async {
    final picked = await _picker.pickImage(source: source, imageQuality: 85);
    if (picked != null) {
      final bytes = await picked.readAsBytes();
      setState(() {
        _image = picked;
        _imageBytes = bytes;
        _result = null;
      });
    }
  }

  Future<void> _analyzeForm() async {
    if (_image == null) {
      _showSnackBar('Lütfen önce bir fotoğraf seçin', Colors.orange);
      return;
    }

    if (_selectedAnswerKeyId == null) {
      _showSnackBar('Lütfen bir cevap anahtarı seçin', Colors.orange);
      return;
    }

    setState(() => _loading = true);
    print('📤 Form analizi başlatılıyor...');
    print('🖼️ Dosya: ${_image!.path}');
    print('🔑 Cevap Anahtarı ID: $_selectedAnswerKeyId');

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('http://127.0.0.1:5000/read-optic-form'),
      );

      // Token ve dosya ekle
      request.headers.addAll(AuthService.getAuthHeaders());
      request.fields['answer_key_id'] = _selectedAnswerKeyId.toString();

      // Web için bytes, mobil için path kullan
      if (_imageBytes != null) {
        request.files.add(http.MultipartFile.fromBytes(
          'file',
          _imageBytes!,
          filename: _image!.name,
        ));
      } else {
        request.files
            .add(await http.MultipartFile.fromPath('file', _image!.path));
      }

      print('📡 İstek gönderiliyor...');
      final response = await request.send();
      final responseBody = await response.stream.bytesToString();
      print('📥 Yanıt alındı: ${response.statusCode}');
      print('📄 Yanıt: $responseBody');

      if (response.statusCode == 200) {
        final jsonResponse = json.decode(responseBody);
        setState(() {
          _result = jsonResponse;
        });
        print('✅ Analiz başarılı!');
        _showSnackBar('✅ Analiz başarıyla tamamlandı!', Colors.green);
      } else {
        print('❌ Hata yanıtı: $responseBody');
        try {
          final error = json.decode(responseBody);
          _showSnackBar('❌ Hata: ${error['error']}', Colors.red);
        } catch (e) {
          _showSnackBar('❌ Backend hatası: $responseBody', Colors.red);
        }
      }
    } catch (e) {
      print('❌ İstek hatası: $e');
      String errorMsg = '❌ Bağlantı hatası: $e';

      if (e.toString().contains('Connection refused') ||
          e.toString().contains('SocketException')) {
        errorMsg =
            '❌ Backend çalışmıyor! start_backend.bat dosyasını çalıştırın.';
      }

      _showSnackBar(errorMsg, Colors.red);
    } finally {
      setState(() => _loading = false);
    }
  }

  void _showSnackBar(String message, Color color) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: color,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _clearImage() {
    setState(() {
      _image = null;
      _imageBytes = null;
      _result = null;
    });
  }

  void _showImageSourceDialog() {
    showModalBottomSheet(
      context: context,
      builder: (context) => SafeArea(
        child: Wrap(
          children: [
            ListTile(
              leading: const Icon(Icons.camera_alt, color: Colors.deepPurple),
              title: const Text('Kamera ile Çek'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.camera);
              },
            ),
            ListTile(
              leading:
                  const Icon(Icons.photo_library, color: Colors.deepPurple),
              title: const Text('Galeriden Seç'),
              onTap: () {
                Navigator.pop(context);
                _pickImage(ImageSource.gallery);
              },
            ),
          ],
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Başlık
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                gradient: LinearGradient(
                  colors: [Colors.deepPurple.shade300, Colors.purple.shade600],
                ),
                borderRadius: BorderRadius.circular(16),
              ),
              child: Column(
                children: [
                  Icon(Icons.document_scanner, size: 60, color: Colors.white),
                  const SizedBox(height: 12),
                  Text(
                    'Optik Form Okuyucu',
                    style: TextStyle(
                      fontSize: 24,
                      fontWeight: FontWeight.bold,
                      color: Colors.white,
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Formu çekin veya yükleyin, otomatik analiz edelim',
                    style: TextStyle(
                      fontSize: 14,
                      color: Colors.white70,
                    ),
                    textAlign: TextAlign.center,
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Cevap Anahtarı Seçimi
            Card(
              elevation: 3,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Icon(Icons.key, color: Colors.deepPurple),
                        const SizedBox(width: 8),
                        Text(
                          'Cevap Anahtarı Seç',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                      ],
                    ),
                    const SizedBox(height: 12),
                    _loadingAnswerKeys
                        ? Center(child: CircularProgressIndicator())
                        : _answerKeys.isEmpty
                            ? Text(
                                'Henüz cevap anahtarı yok. Formlarım sekmesinden oluşturun.',
                                style: TextStyle(color: Colors.grey),
                              )
                            : DropdownButtonFormField<int>(
                                decoration: InputDecoration(
                                  border: OutlineInputBorder(),
                                  contentPadding: EdgeInsets.symmetric(
                                      horizontal: 12, vertical: 8),
                                ),
                                hint: Text('Bir cevap anahtarı seçin'),
                                value: _selectedAnswerKeyId,
                                items: _answerKeys.map((key) {
                                  return DropdownMenuItem<int>(
                                    value: key['id'],
                                    child: Text(
                                      key['exam_name'],
                                      overflow: TextOverflow.ellipsis,
                                    ),
                                  );
                                }).toList(),
                                onChanged: (value) {
                                  setState(() {
                                    _selectedAnswerKeyId = value;
                                  });
                                },
                              ),
                  ],
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Görüntü Önizleme
            Card(
              elevation: 3,
              child: Container(
                height: 300,
                decoration: BoxDecoration(
                  borderRadius: BorderRadius.circular(12),
                  color: Colors.grey[100],
                ),
                child: _image == null
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(Icons.add_photo_alternate,
                                size: 80, color: Colors.grey),
                            const SizedBox(height: 16),
                            Text(
                              'Henüz fotoğraf seçilmedi',
                              style:
                                  TextStyle(color: Colors.grey, fontSize: 16),
                            ),
                          ],
                        ),
                      )
                    : ClipRRect(
                        borderRadius: BorderRadius.circular(12),
                        child: _imageBytes != null
                            ? Image.memory(
                                _imageBytes!,
                                fit: BoxFit.contain,
                              )
                            : const Center(
                                child: CircularProgressIndicator(),
                              ),
                      ),
              ),
            ),

            const SizedBox(height: 16),

            // Butonlar
            Row(
              children: [
                Expanded(
                  child: ElevatedButton.icon(
                    onPressed: _showImageSourceDialog,
                    icon: Icon(Icons.add_a_photo),
                    label: Text(_image == null ? 'Fotoğraf Ekle' : 'Değiştir'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.deepPurple,
                      foregroundColor: Colors.white,
                      padding: EdgeInsets.symmetric(vertical: 16),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ),
                if (_image != null) ...[
                  const SizedBox(width: 12),
                  ElevatedButton.icon(
                    onPressed: _clearImage,
                    icon: Icon(Icons.clear),
                    label: Text('Temizle'),
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.grey,
                      foregroundColor: Colors.white,
                      padding:
                          EdgeInsets.symmetric(vertical: 16, horizontal: 20),
                      shape: RoundedRectangleBorder(
                        borderRadius: BorderRadius.circular(12),
                      ),
                    ),
                  ),
                ],
              ],
            ),

            const SizedBox(height: 16),

            // Analiz Butonu
            SizedBox(
              height: 56,
              child: ElevatedButton.icon(
                onPressed: _loading ? null : _analyzeForm,
                icon: _loading
                    ? SizedBox(
                        width: 20,
                        height: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : Icon(Icons.analytics, size: 24),
                label: Text(
                  _loading ? 'Analiz Ediliyor...' : 'Formu Analiz Et',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(12),
                  ),
                ),
              ),
            ),

            const SizedBox(height: 24),

            // Sonuçlar
            if (_result != null && _result!['success'] == true)
              Card(
                elevation: 4,
                child: Padding(
                  padding: const EdgeInsets.all(16.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.check_circle,
                              color: Colors.green, size: 28),
                          const SizedBox(width: 12),
                          Text(
                            'Analiz Tamamlandı',
                            style: TextStyle(
                              fontSize: 20,
                              fontWeight: FontWeight.bold,
                              color: Colors.green,
                            ),
                          ),
                        ],
                      ),
                      Divider(height: 24),
                      _buildResultRow('👤 Öğrenci Adı',
                          _result!['student_name'] ?? 'Bilinmiyor'),
                      _buildResultRow('🔢 Öğrenci No',
                          _result!['student_number'] ?? 'Bilinmiyor'),
                      Divider(height: 24),
                      _buildResultRow(
                          '📊 Toplam Puan', '${_result!['total_score']}',
                          valueColor: Colors.green, isBold: true),
                      _buildResultRow(
                          '✅ Başarı Oranı', '%${_result!['success_rate']}',
                          valueColor: Colors.blue, isBold: true),
                      _buildResultRow('ℹ️ Detay', _result!['details'] ?? ''),
                      if (_result!['subject_scores'] != null) ...[
                        Divider(height: 24),
                        Text(
                          'Ders Bazlı Sonuçlar:',
                          style: TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                          ),
                        ),
                        const SizedBox(height: 12),
                        ...(_result!['subject_scores'] as Map)
                            .entries
                            .map((entry) {
                          final subjectName = entry.key;
                          final scores = entry.value;
                          return Padding(
                            padding: const EdgeInsets.symmetric(vertical: 4.0),
                            child: Row(
                              mainAxisAlignment: MainAxisAlignment.spaceBetween,
                              children: [
                                Expanded(
                                  child: Text(
                                    '📖 $subjectName',
                                    style: TextStyle(fontSize: 14),
                                  ),
                                ),
                                Text(
                                  '${scores['correct']}/${scores['total']} (${scores['score']} puan)',
                                  style: TextStyle(
                                    fontWeight: FontWeight.bold,
                                    color: Colors.deepPurple,
                                  ),
                                ),
                              ],
                            ),
                          );
                        }).toList(),
                      ],
                    ],
                  ),
                ),
              ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultRow(String label, String value,
      {Color? valueColor, bool isBold = false}) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Expanded(
            flex: 2,
            child: Text(
              label,
              style: TextStyle(
                fontSize: 14,
                color: Colors.grey[700],
              ),
            ),
          ),
          Expanded(
            flex: 3,
            child: Text(
              value,
              style: TextStyle(
                fontSize: 14,
                fontWeight: isBold ? FontWeight.bold : FontWeight.normal,
                color: valueColor ?? Colors.black87,
              ),
            ),
          ),
        ],
      ),
    );
  }
}
