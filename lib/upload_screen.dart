import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'package:http_parser/http_parser.dart';
import 'auth_service.dart';
import 'form_service.dart';
import 'api_config.dart';

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
    // Kalite kaybını önlemek için imageQuality: 100 (sıkıştırma yok)
    // maxWidth/maxHeight belirtilmezse orijinal boyut korunur
    final picked = await _picker.pickImage(
      source: source,
      imageQuality: 100, // Sıkıştırma yok
      // maxWidth: null,  // Orijinal boyut
      // maxHeight: null, // Orijinal boyut
    );
    if (picked != null) {
      final bytes = await picked.readAsBytes();
      print('📸 Görüntü seçildi: ${bytes.length} bytes');
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
        Uri.parse('${ApiConfig.baseUrl}/read-optic-form'),
      );

      // Token ve dosya ekle
      request.headers.addAll(AuthService.getAuthHeaders());
      request.fields['answer_key_id'] = _selectedAnswerKeyId.toString();

      // Web için bytes, mobil için path kullan
      if (_imageBytes != null) {
        // Dosya uzantısına göre content type belirle
        String contentType = 'image/jpeg';
        String filename = _image!.name.toLowerCase();
        if (filename.endsWith('.png')) {
          contentType = 'image/png';
        } else if (filename.endsWith('.jpg') || filename.endsWith('.jpeg')) {
          contentType = 'image/jpeg';
        }

        request.files.add(http.MultipartFile.fromBytes(
          'file',
          _imageBytes!,
          filename: _image!.name,
          contentType: MediaType.parse(contentType),
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
      backgroundColor: Colors.transparent,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(20.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            // Başlık Kartı
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 20,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                children: [
                  const Icon(Icons.document_scanner_rounded,
                      size: 48, color: Color(0xFF2979FF)),
                  const SizedBox(height: 12),
                  const Text(
                    'Optik Form Analizi',
                    style: TextStyle(
                      fontSize: 22,
                      fontWeight: FontWeight.bold,
                      color: Color(0xFF1A237E),
                    ),
                  ),
                  const SizedBox(height: 8),
                  Text(
                    'Form fotoğrafını yükleyin ve anında analiz edin',
                    textAlign: TextAlign.center,
                    style: TextStyle(
                      color: Colors.grey[600],
                      fontSize: 14,
                    ),
                  ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Cevap Anahtarı Seçimi
            Container(
              padding: const EdgeInsets.all(20),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: Colors.black.withOpacity(0.05),
                    blurRadius: 20,
                    offset: const Offset(0, 5),
                  ),
                ],
              ),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    children: [
                      Container(
                        padding: const EdgeInsets.all(8),
                        decoration: BoxDecoration(
                          color: const Color(0xFFE3F2FD),
                          borderRadius: BorderRadius.circular(8),
                        ),
                        child: const Icon(Icons.key_rounded,
                            color: Color(0xFF1565C0), size: 20),
                      ),
                      const SizedBox(width: 12),
                      const Text(
                        'Cevap Anahtarı',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1A237E),
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 16),
                  _loadingAnswerKeys
                      ? const Center(child: CircularProgressIndicator())
                      : _answerKeys.isEmpty
                          ? Container(
                              padding: const EdgeInsets.all(12),
                              decoration: BoxDecoration(
                                color: Colors.orange.shade50,
                                borderRadius: BorderRadius.circular(12),
                                border:
                                    Border.all(color: Colors.orange.shade200),
                              ),
                              child: Row(
                                children: [
                                  Icon(Icons.warning_amber_rounded,
                                      color: Colors.orange.shade700),
                                  const SizedBox(width: 12),
                                  Expanded(
                                    child: Text(
                                      'Henüz cevap anahtarı yok. Formlarım sekmesinden oluşturun.',
                                      style: TextStyle(
                                          color: Colors.orange.shade900,
                                          fontSize: 13),
                                    ),
                                  ),
                                ],
                              ),
                            )
                          : Container(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 16),
                              decoration: BoxDecoration(
                                color: Colors.grey.shade50,
                                borderRadius: BorderRadius.circular(12),
                                border: Border.all(color: Colors.grey.shade200),
                              ),
                              child: DropdownButtonHideUnderline(
                                child: DropdownButton<int>(
                                  value: _selectedAnswerKeyId,
                                  hint: const Text('Sınav şablonu seçin'),
                                  isExpanded: true,
                                  icon: const Icon(
                                      Icons.keyboard_arrow_down_rounded),
                                  items: _answerKeys
                                      .map<DropdownMenuItem<int>>((key) {
                                    return DropdownMenuItem<int>(
                                      value: key['id'],
                                      child: Text(
                                        key['exam_name'],
                                        style: const TextStyle(
                                            fontWeight: FontWeight.w500),
                                      ),
                                    );
                                  }).toList(),
                                  onChanged: (value) {
                                    setState(() {
                                      _selectedAnswerKeyId = value;
                                    });
                                  },
                                ),
                              ),
                            ),
                ],
              ),
            ),

            const SizedBox(height: 24),

            // Fotoğraf Seçimi
            GestureDetector(
              onTap: () => _showImageSourceDialog(),
              child: Container(
                height: 250,
                decoration: BoxDecoration(
                  color: _image == null ? Colors.white : Colors.black,
                  borderRadius: BorderRadius.circular(24),
                  border: _image == null
                      ? Border.all(
                          color: const Color(0xFF2979FF).withOpacity(0.3),
                          width: 2,
                          style: BorderStyle.solid)
                      : null,
                  boxShadow: [
                    BoxShadow(
                      color: Colors.black.withOpacity(0.1),
                      blurRadius: 20,
                      offset: const Offset(0, 10),
                    ),
                  ],
                  image: _image != null
                      ? DecorationImage(
                          image: MemoryImage(_imageBytes!),
                          fit: BoxFit.contain,
                        )
                      : null,
                ),
                child: _image == null
                    ? Column(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          Container(
                            padding: const EdgeInsets.all(20),
                            decoration: const BoxDecoration(
                              color: Color(0xFFE3F2FD),
                              shape: BoxShape.circle,
                            ),
                            child: const Icon(
                              Icons.add_a_photo_rounded,
                              size: 40,
                              color: Color(0xFF2979FF),
                            ),
                          ),
                          const SizedBox(height: 16),
                          const Text(
                            'Fotoğraf Yükle',
                            style: TextStyle(
                              fontSize: 18,
                              fontWeight: FontWeight.bold,
                              color: Color(0xFF2979FF),
                            ),
                          ),
                          const SizedBox(height: 8),
                          Text(
                            'Kamera veya Galeri',
                            style: TextStyle(
                              color: Colors.grey[500],
                              fontSize: 14,
                            ),
                          ),
                        ],
                      )
                    : Stack(
                        children: [
                          Positioned(
                            top: 16,
                            right: 16,
                            child: GestureDetector(
                              onTap: () {
                                setState(() {
                                  _image = null;
                                  _imageBytes = null;
                                  _result = null;
                                });
                              },
                              child: Container(
                                padding: const EdgeInsets.all(8),
                                decoration: BoxDecoration(
                                  color: Colors.black.withOpacity(0.6),
                                  shape: BoxShape.circle,
                                ),
                                child: const Icon(Icons.close,
                                    color: Colors.white, size: 20),
                              ),
                            ),
                          ),
                        ],
                      ),
              ),
            ),

            const SizedBox(height: 32),

            // Analiz Butonu
            SizedBox(
              height: 56,
              child: ElevatedButton(
                onPressed: _loading ? null : _analyzeForm,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.transparent,
                  shadowColor: Colors.transparent,
                  padding: EdgeInsets.zero,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(16),
                  ),
                ),
                child: Ink(
                  decoration: BoxDecoration(
                    gradient: const LinearGradient(
                      colors: [Color(0xFF2979FF), Color(0xFF00E5FF)],
                      begin: Alignment.centerLeft,
                      end: Alignment.centerRight,
                    ),
                    borderRadius: BorderRadius.circular(16),
                    boxShadow: [
                      BoxShadow(
                        color: const Color(0xFF2979FF).withOpacity(0.4),
                        blurRadius: 12,
                        offset: const Offset(0, 6),
                      ),
                    ],
                  ),
                  child: Container(
                    alignment: Alignment.center,
                    child: _loading
                        ? const SizedBox(
                            width: 24,
                            height: 24,
                            child: CircularProgressIndicator(
                              color: Colors.white,
                              strokeWidth: 2,
                            ),
                          )
                        : Row(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: const [
                              Icon(Icons.analytics_outlined,
                                  color: Colors.white),
                              SizedBox(width: 12),
                              Text(
                                'ANALİZ ET',
                                style: TextStyle(
                                  fontSize: 16,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                  letterSpacing: 1,
                                ),
                              ),
                            ],
                          ),
                  ),
                ),
              ),
            ),
            if (_result != null) ...[
              const SizedBox(height: 32),
              _buildResultCard(),
            ],

            const SizedBox(height: 40),
          ],
        ),
      ),
    );
  }

  Widget _buildResultCard() {
    final studentName = _result!['student_name'] ?? 'Bilinmiyor';
    final studentNumber = _result!['student_number'] ?? '';
    final successRate = _result!['success_rate'];
    final totalScore = _result!['total_score'];
    final subjectScores =
        _result!['subject_scores'] as Map<String, dynamic>? ?? {};

    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(24),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 30,
            offset: const Offset(0, 15),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: const Color(0xFFE8F5E9),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: const Icon(Icons.check_circle_outline_rounded,
                    color: Color(0xFF2E7D32), size: 28),
              ),
              const SizedBox(width: 16),
              const Text(
                'Analiz Sonucu',
                style: TextStyle(
                  fontSize: 20,
                  fontWeight: FontWeight.bold,
                  color: Color(0xFF1A237E),
                ),
              ),
            ],
          ),
          const SizedBox(height: 24),

          // Öğrenci Bilgileri
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: const Color(0xFFF5F7FA),
              borderRadius: BorderRadius.circular(16),
            ),
            child: Row(
              children: [
                CircleAvatar(
                  backgroundColor: const Color(0xFF2979FF),
                  radius: 24,
                  child: Text(
                    studentName.isNotEmpty ? studentName.substring(0, 1) : '?',
                    style: const TextStyle(
                        color: Colors.white,
                        fontWeight: FontWeight.bold,
                        fontSize: 20),
                  ),
                ),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        studentName,
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1A237E),
                        ),
                      ),
                      Text(
                        'No: $studentNumber',
                        style: TextStyle(
                          color: Colors.grey[600],
                          fontSize: 14,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ),
          ),

          const SizedBox(height: 24),

          // Skor Kartları
          Row(
            children: [
              Expanded(
                child: _buildScoreCard(
                  'Başarı',
                  '%${successRate?.toStringAsFixed(1) ?? "0"}',
                  const Color(0xFFE3F2FD),
                  const Color(0xFF1565C0),
                ),
              ),
              const SizedBox(width: 16),
              Expanded(
                child: _buildScoreCard(
                  'Puan',
                  totalScore?.toStringAsFixed(1) ?? "0",
                  const Color(0xFFFFF8E1),
                  const Color(0xFFF9A825),
                ),
              ),
            ],
          ),

          const SizedBox(height: 24),
          const Text(
            'Ders Detayları',
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: Color(0xFF1A237E),
            ),
          ),
          const SizedBox(height: 16),

          // Ders Listesi
          ...subjectScores.entries.map((entry) {
            final scoreData = entry.value as Map<String, dynamic>;
            return Padding(
              padding: const EdgeInsets.only(bottom: 12),
              child: Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  border: Border.all(color: Colors.grey.shade200),
                  borderRadius: BorderRadius.circular(12),
                ),
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text(
                      entry.key.toUpperCase(),
                      style: const TextStyle(
                        fontWeight: FontWeight.w600,
                        color: Color(0xFF455A64),
                      ),
                    ),
                    Text(
                      '${scoreData['correct']}/${scoreData['total']} D',
                      style: const TextStyle(
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF2E7D32),
                      ),
                    ),
                  ],
                ),
              ),
            );
          }).toList(),
        ],
      ),
    );
  }

  Widget _buildScoreCard(
      String label, String value, Color bgColor, Color textColor) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 20, horizontal: 16),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        children: [
          Text(
            value,
            style: TextStyle(
              fontSize: 24,
              fontWeight: FontWeight.bold,
              color: textColor,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            label,
            style: TextStyle(
              fontSize: 14,
              fontWeight: FontWeight.w500,
              color: textColor.withOpacity(0.8),
            ),
          ),
        ],
      ),
    );
  }
}
