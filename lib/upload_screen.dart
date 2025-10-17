import 'dart:io';
import 'dart:convert';
import 'package:flutter/material.dart';
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;

class UploadScreen extends StatefulWidget {
  const UploadScreen({super.key});

  @override
  State<UploadScreen> createState() => _UploadScreenState();
}

class _UploadScreenState extends State<UploadScreen> {
  File? _image;
  bool _loading = false;
  String? _resultText;
  final ImagePicker _picker = ImagePicker();

  Future<void> _pickImage(ImageSource source) async {
    final picked = await _picker.pickImage(source: source);
    if (picked != null) {
      setState(() {
        _image = File(picked.path);
        _resultText = null;
      });
    }
  }

  Future<void> _sendImage() async {
    if (_image == null) {
      _showSnackBar('Lütfen önce bir fotoğraf seçin');
      return;
    }
    
    setState(() => _loading = true);

    try {
      final request = http.MultipartRequest(
        'POST',
        Uri.parse('http://127.0.0.1:5000/read_optic_form'),
      );
      request.files.add(await http.MultipartFile.fromPath('file', _image!.path));
      final response = await request.send();

      if (response.statusCode == 200) {
        final responseBody = await response.stream.bytesToString();
        try {
          final jsonResponse = json.decode(responseBody);
          setState(() {
            _resultText = _formatResults(jsonResponse);
          });
          _showSnackBar('Analiz başarılı!');
        } catch (e) {
          setState(() {
            _resultText = responseBody;
          });
        }
      } else {
        setState(() {
          _resultText = 'Sunucu hatası (${response.statusCode})';
        });
        _showSnackBar('Bir hata oluştu');
      }
    } catch (e) {
      setState(() {
        _resultText = 'Bağlantı hatası: $e';
      });
      _showSnackBar('Bağlantı hatası');
    } finally {
      setState(() => _loading = false);
    }
  }

  String _formatResults(Map<String, dynamic> jsonResponse) {
    if (jsonResponse['success'] == true) {
      return '''
ÖĞRENCİ BİLGİLERİ:
📝 Adı: ${jsonResponse['student_name'] ?? 'Bilinmiyor'}
🔢 Numarası: ${jsonResponse['student_number'] ?? 'Bilinmiyor'}

📊 SINAV SONUÇLARI:
${jsonResponse['answers'] is Map ? 
  jsonResponse['answers'].entries.map((e) => '📖 ${e.key}: ${e.value}').join('\n') : 
  'Sonuçlar yükleniyor...'}

🎯 TOPLAM: ${jsonResponse['total_score'] ?? 'Hesaplanıyor...'}
⭐ Başarı Oranı: ${jsonResponse['success_rate'] ?? 'Hesaplanıyor...'}%

${jsonResponse['details'] ?? 'Analiz tamamlandı'}
      ''';
    } else {
      return 'Hata: ${jsonResponse['error'] ?? 'Bilinmeyen hata'}';
    }
  }

  void _showSnackBar(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(
        content: Text(message),
        backgroundColor: Colors.deepPurple,
        behavior: SnackBarBehavior.floating,
      ),
    );
  }

  void _clearImage() {
    setState(() {
      _image = null;
      _resultText = null;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Theme.of(context).colorScheme.background,
      appBar: AppBar(
        title: const Text('Optik Form Analiz'),
        centerTitle: true,
        elevation: 0,
        actions: [
          if (_image != null)
            IconButton(
              onPressed: _clearImage,
              icon: const Icon(Icons.clear),
              tooltip: 'Temizle',
            ),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(20.0),
        child: Center(
          child: SingleChildScrollView(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                _buildHeaderSection(),
                const SizedBox(height: 30),
                _buildImagePreview(),
                const SizedBox(height: 30),
                _buildActionButtons(),
                const SizedBox(height: 30),
                if (_resultText != null) _buildResultSection(),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _buildHeaderSection() {
    return Column(
      children: [
        Container(
          padding: const EdgeInsets.all(20),
          decoration: BoxDecoration(
            color: Theme.of(context).colorScheme.primaryContainer,
            borderRadius: BorderRadius.circular(20),
          ),
          child: const Icon(
            Icons.analytics,
            size: 80,
            color: Colors.deepPurple,
          ),
        ),
        const SizedBox(height: 20),
        Text(
          'Optik Form Analiz Uygulaması',
          style: TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Theme.of(context).colorScheme.onBackground,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: 10),
        Text(
          'Fotoğraf yükleyin veya çekin, otomatik olarak analiz edelim',
          style: TextStyle(
            fontSize: 16,
            color: Theme.of(context).colorScheme.onBackground.withOpacity(0.7),
          ),
          textAlign: TextAlign.center,
        ),
      ],
    );
  }

  Widget _buildImagePreview() {
    return Container(
      width: double.infinity,
      height: 250,
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.surface,
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.1),
            blurRadius: 10,
            offset: const Offset(0, 5),
          ),
        ],
      ),
      child: _image == null
          ? Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  Icons.photo_library,
                  size: 60,
                  color: Theme.of(context).colorScheme.onSurface.withOpacity(0.3),
                ),
                const SizedBox(height: 10),
                Text(
                  'Fotoğraf seçilmedi',
                  style: TextStyle(
                    color: Theme.of(context).colorScheme.onSurface.withOpacity(0.5),
                  ),
                ),
              ],
            )
          : ClipRRect(
              borderRadius: BorderRadius.circular(20),
              child: Stack(
                children: [
                  Image.file(
                    _image!,
                    width: double.infinity,
                    height: double.infinity,
                    fit: BoxFit.cover,
                  ),
                  Positioned(
                    top: 10,
                    right: 10,
                    child: Container(
                      padding: const EdgeInsets.all(6),
                      decoration: BoxDecoration(
                        color: Colors.black54,
                        borderRadius: BorderRadius.circular(20),
                      ),
                      child: IconButton(
                        onPressed: _clearImage,
                        icon: const Icon(Icons.close, color: Colors.white, size: 20),
                      ),
                    ),
                  ),
                ],
              ),
            ),
    );
  }

  Widget _buildActionButtons() {
    return Column(
      children: [
        Row(
          children: [
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _loading ? null : () => _pickImage(ImageSource.gallery),
                icon: const Icon(Icons.photo_library),
                label: const Text('Galeriden Seç'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 15),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
              ),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: ElevatedButton.icon(
                onPressed: _loading ? null : () => _pickImage(ImageSource.camera),
                icon: const Icon(Icons.camera_alt),
                label: const Text('Fotoğraf Çek'),
                style: ElevatedButton.styleFrom(
                  padding: const EdgeInsets.symmetric(vertical: 15),
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(15),
                  ),
                ),
              ),
            ),
          ],
        ),
        const SizedBox(height: 15),
        SizedBox(
          width: double.infinity,
          child: ElevatedButton.icon(
            onPressed: _loading ? null : _sendImage,
            icon: _loading
                ? SizedBox(
                    height: 20,
                    width: 20,
                    child: CircularProgressIndicator(
                      strokeWidth: 2,
                      color: Theme.of(context).colorScheme.onPrimary,
                    ),
                  )
                : const Icon(Icons.analytics),
            label: _loading
                ? const Text('Analiz Yapılıyor...')
                : const Text('Analiz Et'),
            style: ElevatedButton.styleFrom(
              padding: const EdgeInsets.symmetric(vertical: 18),
              backgroundColor: Colors.deepPurple,
              foregroundColor: Colors.white,
              shape: RoundedRectangleBorder(
                borderRadius: BorderRadius.circular(15),
              ),
              elevation: 3,
            ),
          ),
        ),
      ],
    );
  }

  Widget _buildResultSection() {
    return Container(
      width: double.infinity,
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        color: Theme.of(context).colorScheme.primaryContainer,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(
                Icons.fact_check,
                color: Theme.of(context).colorScheme.primary,
              ),
              const SizedBox(width: 10),
              Text(
                'Analiz Sonuçları',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Theme.of(context).colorScheme.primary,
                ),
              ),
            ],
          ),
          const SizedBox(height: 15),
          Container(
            padding: const EdgeInsets.all(16),
            decoration: BoxDecoration(
              color: Theme.of(context).colorScheme.background,
              borderRadius: BorderRadius.circular(12),
            ),
            child: Text(
              _resultText!,
              style: TextStyle(
                fontSize: 16,
                height: 1.5,
                color: Theme.of(context).colorScheme.onBackground,
              ),
            ),
          ),
        ],
      ),
    );
  }
}