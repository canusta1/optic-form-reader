import 'dart:convert';
import 'dart:typed_data';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'api_config.dart';
import 'auth_service.dart';

class StudentResultDetailScreen extends StatefulWidget {
  final int resultId;
  final String studentName;

  const StudentResultDetailScreen({
    super.key,
    required this.resultId,
    required this.studentName,
  });

  @override
  State<StudentResultDetailScreen> createState() =>
      _StudentResultDetailScreenState();
}

class _StudentResultDetailScreenState extends State<StudentResultDetailScreen>
    with SingleTickerProviderStateMixin {
  bool _loading = true;
  Map<String, dynamic>? _resultData;
  String? _error;
  late TabController _tabController;
  Uint8List? _imageBytes;

  @override
  void initState() {
    super.initState();
    _tabController = TabController(length: 3, vsync: this);
    _loadResultDetail();
  }

  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  Future<void> _loadResultDetail() async {
    // 10 deneme yap - Android emulator network initialization
    for (int attempt = 1; attempt <= 10; attempt++) {
      if (!mounted) return;
      
      try {
        // Timeout süresini denemeye göre ayarla
        final timeout = const Duration(seconds: 15); // Kısa timeout, çok deneme
        
        debugPrint('🔄 Deneme $attempt/10 başlıyor...');
        
        final response = await http
            .get(
              Uri.parse(
                  '${ApiConfig.baseUrl}/student-result/${widget.resultId}'),
              headers: AuthService.getAuthHeaders(),
            )
            .timeout(timeout);

        debugPrint('✓ Deneme $attempt: Status ${response.statusCode}');

        if (response.statusCode == 200) {
          final data = json.decode(response.body);
          if (data['success'] == true) {
            final result = data['result'];
            debugPrint('✅ Deneme $attempt BAŞARILI - Veri alındı');

            // Base64 görseli decode et
            Uint8List? imgBytes;
            if (result['image_base64'] != null &&
                result['image_base64'].isNotEmpty) {
              try {
                imgBytes = base64Decode(result['image_base64'] as String);
                debugPrint(
                    '✅ Görsel decode başarılı: ${imgBytes.length} bytes');
              } catch (e) {
                debugPrint('❌ Base64 decode hatası: $e');
              }
            } else {
              debugPrint('⚠️ Görsel base64 boş veya null');
            }

            if (mounted) {
              setState(() {
                _resultData = result;
                _imageBytes = imgBytes;
                _loading = false;
              });
            }
            return; // Başarılı - çık
          }
        }
        
        // Başarısız - bekle ve devam et
        debugPrint('⚠️ Deneme $attempt başarısız, bekleniyor...');
        await Future.delayed(Duration(milliseconds: 1500));
        
      } catch (e) {
        debugPrint('❌ Deneme $attempt HATA: $e');
        // Bekle ve tekrar dene
        await Future.delayed(Duration(milliseconds: 2000));
      }
    }
    
    // 10 deneme de başarısız olduysa hata göster
    if (mounted) {
      setState(() {
        _error = 'Bağlantı kurulamadı. Lütfen tekrar deneyin.';
        _loading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        title: Text(widget.studentName.isNotEmpty
            ? widget.studentName
            : 'Öğrenci Detayı'),
        centerTitle: true,
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Color(0xFF1A237E)),
        bottom: TabBar(
          controller: _tabController,
          labelColor: const Color(0xFF2979FF),
          unselectedLabelColor: Colors.grey,
          indicatorColor: const Color(0xFF2979FF),
          tabs: const [
            Tab(icon: Icon(Icons.image), text: 'Form'),
            Tab(icon: Icon(Icons.bar_chart), text: 'İstatistik'),
            Tab(icon: Icon(Icons.list_alt), text: 'Cevaplar'),
          ],
        ),
      ),
      body: _loading
          ? const Center(child: CircularProgressIndicator())
          : _error != null
              ? _buildErrorWidget()
              : TabBarView(
                  controller: _tabController,
                  children: [
                    _buildFormImageTab(),
                    _buildStatisticsTab(),
                    _buildAnswersTab(),
                  ],
                ),
    );
  }

  Widget _buildErrorWidget() {
    return Center(
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          const Icon(Icons.error_outline, size: 64, color: Colors.red),
          const SizedBox(height: 16),
          Text(_error!, style: const TextStyle(color: Colors.red)),
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              setState(() {
                _loading = true;
                _error = null;
              });
              _loadResultDetail();
            },
            child: const Text('Tekrar Dene'),
          ),
        ],
      ),
    );
  }

  // TAB 1: Optik Form Görseli
  Widget _buildFormImageTab() {
    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          // Özet Kart
          _buildSummaryCard(),
          const SizedBox(height: 16),

          // Form Görseli
          Container(
            decoration: BoxDecoration(
              color: Colors.white,
              borderRadius: BorderRadius.circular(16),
              boxShadow: [
                BoxShadow(
                  color: Colors.black.withOpacity(0.05),
                  blurRadius: 10,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Padding(
                  padding: EdgeInsets.all(16),
                  child: Row(
                    children: [
                      Icon(Icons.document_scanner,
                          color: Color(0xFF2979FF), size: 24),
                      SizedBox(width: 8),
                      Text(
                        'Taranan Optik Form',
                        style: TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                          color: Color(0xFF1A237E),
                        ),
                      ),
                    ],
                  ),
                ),
                _buildImageWidget(),
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildImageWidget() {
    if (_imageBytes != null) {
      return ClipRRect(
        borderRadius: const BorderRadius.only(
          bottomLeft: Radius.circular(16),
          bottomRight: Radius.circular(16),
        ),
        child: InteractiveViewer(
          minScale: 0.5,
          maxScale: 4.0,
          child: Image.memory(
            _imageBytes!,
            fit: BoxFit.contain,
          ),
        ),
      );
    }

    return Container(
      height: 200,
      alignment: Alignment.center,
      child: Column(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(Icons.image_not_supported, size: 64, color: Colors.grey[400]),
          const SizedBox(height: 8),
          Text('Görsel mevcut değil',
              style: TextStyle(color: Colors.grey[600])),
        ],
      ),
    );
  }

  Widget _buildSummaryCard() {
    final totalScore = _resultData?['total_score'] ?? 0;
    final successRate = _resultData?['success_rate'] ?? 0;

    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(
        gradient: const LinearGradient(
          colors: [Color(0xFF2979FF), Color(0xFF00E5FF)],
          begin: Alignment.topLeft,
          end: Alignment.bottomRight,
        ),
        borderRadius: BorderRadius.circular(20),
        boxShadow: [
          BoxShadow(
            color: const Color(0xFF2979FF).withOpacity(0.3),
            blurRadius: 15,
            offset: const Offset(0, 8),
          ),
        ],
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: [
          _buildScoreItem(
              'Toplam Puan', totalScore.toStringAsFixed(1), Icons.stars),
          Container(
            height: 50,
            width: 1,
            color: Colors.white.withOpacity(0.3),
          ),
          _buildScoreItem('Başarı Oranı', '%${successRate.toStringAsFixed(1)}',
              Icons.trending_up),
        ],
      ),
    );
  }

  Widget _buildScoreItem(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.white, size: 28),
        const SizedBox(height: 8),
        Text(
          value,
          style: const TextStyle(
            fontSize: 24,
            fontWeight: FontWeight.bold,
            color: Colors.white,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: Colors.white.withOpacity(0.8),
          ),
        ),
      ],
    );
  }

  // TAB 2: İstatistikler
  Widget _buildStatisticsTab() {
    final subjectsStats =
        _resultData?['subjects_stats'] as List<dynamic>? ?? [];

    return SingleChildScrollView(
      padding: const EdgeInsets.all(16),
      child: Column(
        children: [
          _buildSummaryCard(),
          const SizedBox(height: 20),

          // Ders Bazlı İstatistikler
          ...subjectsStats.map((subject) => _buildSubjectStatCard(subject)),
        ],
      ),
    );
  }

  Widget _buildSubjectStatCard(Map<String, dynamic> subject) {
    final subjectName = subject['subject_name'] ?? 'Ders';
    final correct = subject['correct_count'] ?? 0;
    final wrong = subject['wrong_count'] ?? 0;
    final empty = subject['empty_count'] ?? 0;
    final total = subject['total_questions'] ?? 40;
    final pointsEarned = subject['points_earned'] ?? 0;
    final totalPoints = subject['total_points'] ?? 100;

    final correctPercent = total > 0 ? (correct / total * 100) : 0;

    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Başlık
          Row(
            children: [
              Container(
                padding: const EdgeInsets.all(10),
                decoration: BoxDecoration(
                  color: _getSubjectColor(subjectName).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(10),
                ),
                child: Icon(
                  _getSubjectIcon(subjectName),
                  color: _getSubjectColor(subjectName),
                  size: 24,
                ),
              ),
              const SizedBox(width: 12),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      subjectName,
                      style: const TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.bold,
                        color: Color(0xFF1A237E),
                      ),
                    ),
                    Text(
                      '$pointsEarned / $totalPoints puan',
                      style: TextStyle(
                        fontSize: 12,
                        color: Colors.grey[600],
                      ),
                    ),
                  ],
                ),
              ),
              Container(
                padding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                decoration: BoxDecoration(
                  color: _getPercentColor(correctPercent).withOpacity(0.1),
                  borderRadius: BorderRadius.circular(20),
                ),
                child: Text(
                  '%${correctPercent.toStringAsFixed(0)}',
                  style: TextStyle(
                    fontWeight: FontWeight.bold,
                    color: _getPercentColor(correctPercent),
                  ),
                ),
              ),
            ],
          ),

          const SizedBox(height: 16),

          // Progress Bar
          ClipRRect(
            borderRadius: BorderRadius.circular(8),
            child: LinearProgressIndicator(
              value: correctPercent / 100,
              backgroundColor: Colors.grey[200],
              valueColor:
                  AlwaysStoppedAnimation(_getPercentColor(correctPercent)),
              minHeight: 8,
            ),
          ),

          const SizedBox(height: 16),

          // İstatistik Satırı
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceAround,
            children: [
              _buildStatItem('Doğru', correct.toString(), Colors.green),
              _buildStatItem('Yanlış', wrong.toString(), Colors.red),
              _buildStatItem('Boş', empty.toString(), Colors.grey),
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildStatItem(String label, String value, Color color) {
    return Column(
      children: [
        Container(
          width: 40,
          height: 40,
          decoration: BoxDecoration(
            color: color.withOpacity(0.1),
            shape: BoxShape.circle,
          ),
          alignment: Alignment.center,
          child: Text(
            value,
            style: TextStyle(
              fontSize: 16,
              fontWeight: FontWeight.bold,
              color: color,
            ),
          ),
        ),
        const SizedBox(height: 4),
        Text(
          label,
          style: TextStyle(
            fontSize: 11,
            color: Colors.grey[600],
          ),
        ),
      ],
    );
  }

  Color _getSubjectColor(String name) {
    final lower = name.toLowerCase();
    if (lower.contains('türkçe')) return Colors.blue;
    if (lower.contains('matematik')) return Colors.orange;
    if (lower.contains('fen')) return Colors.green;
    if (lower.contains('sosyal')) return Colors.purple;
    return Colors.teal;
  }

  IconData _getSubjectIcon(String name) {
    final lower = name.toLowerCase();
    if (lower.contains('türkçe')) return Icons.menu_book;
    if (lower.contains('matematik')) return Icons.calculate;
    if (lower.contains('fen')) return Icons.science;
    if (lower.contains('sosyal')) return Icons.public;
    return Icons.school;
  }

  Color _getPercentColor(num percent) {
    if (percent >= 80) return Colors.green;
    if (percent >= 60) return Colors.orange;
    if (percent >= 40) return Colors.amber;
    return Colors.red;
  }

  // TAB 3: Cevap Karşılaştırması
  Widget _buildAnswersTab() {
    final answers = _resultData?['answers'] as List<dynamic>? ?? [];
    final subjectsStats =
        _resultData?['subjects_stats'] as List<dynamic>? ?? [];

    // Cevapları derse göre grupla
    Map<String, List<Map<String, dynamic>>> groupedAnswers = {};
    for (var answer in answers) {
      final subjectName = answer['subject_name'] ?? 'Bilinmeyen';
      if (!groupedAnswers.containsKey(subjectName)) {
        groupedAnswers[subjectName] = [];
      }
      groupedAnswers[subjectName]!.add(Map<String, dynamic>.from(answer));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: groupedAnswers.keys.length,
      itemBuilder: (context, index) {
        final subjectName = groupedAnswers.keys.elementAt(index);
        final subjectAnswers = groupedAnswers[subjectName]!;

        return _buildSubjectAnswersCard(subjectName, subjectAnswers);
      },
    );
  }

  Widget _buildSubjectAnswersCard(
      String subjectName, List<Map<String, dynamic>> answers) {
    return Container(
      margin: const EdgeInsets.only(bottom: 16),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(16),
        boxShadow: [
          BoxShadow(
            color: Colors.black.withOpacity(0.05),
            blurRadius: 10,
            offset: const Offset(0, 4),
          ),
        ],
      ),
      child: ExpansionTile(
        initiallyExpanded: true,
        leading: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: _getSubjectColor(subjectName).withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            _getSubjectIcon(subjectName),
            color: _getSubjectColor(subjectName),
          ),
        ),
        title: Text(
          subjectName,
          style: const TextStyle(
            fontWeight: FontWeight.bold,
            color: Color(0xFF1A237E),
          ),
        ),
        subtitle: Text('${answers.length} soru'),
        children: [
          // Başlık Satırı
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
            color: Colors.grey[100],
            child: const Row(
              children: [
                Expanded(
                    flex: 1,
                    child: Text('No',
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 12))),
                Expanded(
                    flex: 2,
                    child: Text('Öğrenci',
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 12),
                        textAlign: TextAlign.center)),
                Expanded(
                    flex: 2,
                    child: Text('Doğru',
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 12),
                        textAlign: TextAlign.center)),
                Expanded(
                    flex: 1,
                    child: Text('Sonuç',
                        style: TextStyle(
                            fontWeight: FontWeight.bold, fontSize: 12),
                        textAlign: TextAlign.center)),
              ],
            ),
          ),

          // Cevap Satırları
          ...answers.map((answer) => _buildAnswerRow(answer)),

          const SizedBox(height: 8),
        ],
      ),
    );
  }

  Widget _buildAnswerRow(Map<String, dynamic> answer) {
    final questionNo = answer['question_number'] ?? 0;
    final studentAnswer = answer['student_answer'] ?? '';
    final correctAnswer = answer['correct_answer'] ?? '';
    final isCorrect = answer['is_correct'] == 1 || answer['is_correct'] == true;
    final isEmpty = studentAnswer.isEmpty || studentAnswer == 'BOŞ';

    Color bgColor;
    Color textColor;
    IconData icon;

    if (isEmpty) {
      bgColor = Colors.amber.withOpacity(0.1);
      textColor = Colors.amber[800]!;
      icon = Icons.remove_circle_outline;
    } else if (isCorrect) {
      bgColor = Colors.green.withOpacity(0.1);
      textColor = Colors.green[800]!;
      icon = Icons.check_circle;
    } else {
      bgColor = Colors.red.withOpacity(0.1);
      textColor = Colors.red[800]!;
      icon = Icons.cancel;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
      decoration: BoxDecoration(
        color: bgColor,
        border: Border(
          bottom: BorderSide(color: Colors.grey[200]!, width: 1),
        ),
      ),
      child: Row(
        children: [
          // Soru No
          Expanded(
            flex: 1,
            child: Container(
              padding: const EdgeInsets.all(6),
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                '$questionNo',
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 12,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),

          // Öğrenci Cevabı
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
              margin: const EdgeInsets.symmetric(horizontal: 4),
              decoration: BoxDecoration(
                color: isEmpty
                    ? Colors.grey[300]
                    : (isCorrect ? Colors.green : Colors.red),
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                isEmpty ? 'BOŞ' : studentAnswer,
                style: TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                  color: isEmpty ? Colors.grey[700] : Colors.white,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),

          // Doğru Cevap
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 12),
              margin: const EdgeInsets.symmetric(horizontal: 4),
              decoration: BoxDecoration(
                color: Colors.blue,
                borderRadius: BorderRadius.circular(6),
              ),
              child: Text(
                correctAnswer,
                style: const TextStyle(
                  fontWeight: FontWeight.bold,
                  fontSize: 14,
                  color: Colors.white,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),

          // Sonuç İkonu
          Expanded(
            flex: 1,
            child: Icon(icon, color: textColor, size: 24),
          ),
        ],
      ),
    );
  }
}
