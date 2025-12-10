import 'package:flutter/material.dart';
import 'form_model.dart';
import 'form_service.dart';

class CreateFormScreen extends StatefulWidget {
  const CreateFormScreen({super.key});

  @override
  State<CreateFormScreen> createState() => _CreateFormScreenState();
}

class _CreateFormScreenState extends State<CreateFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final TextEditingController _formNameController = TextEditingController();
  bool _isSaving = false;

  int _subjectCount = 1;
  final List<SubjectModel> _subjects = [];
  String _selectedSchoolType = 'Ortaokul';
  String _selectedFormTemplate = 'simple';
  List<Map<String, dynamic>> _formTemplates = [];

  final Map<String, List<String>> _schoolSubjects = {
    'Ortaokul': [
      'Türkçe',
      'Matematik',
      'Fen Bilimleri',
      'Sosyal Bilgiler',
      'T.C. İnkılâp Tarihi ve Atatürkçülük',
      'Yabancı Dil',
      'Din Kültürü ve Ahlak Bilgisi',
      'Beden Eğitimi',
      'Müzik',
      'Resim'
    ],
    'Lise': [
      'TÜRK DİLİ VE EDEBİYATI',
      'DİN KÜLTÜRÜ VE AHLAK BİLGİSİ',
      'TARİH',
      'T.C. İNKILAP TARİHİ VE ATATÜRKÇÜLÜK',
      'COĞRAFYA',
      'MATEMATİK',
      'FİZİK',
      'KİMYA',
      'BİYOLOJİ',
      'FELSEFE',
      'BİRİNCİ YABANCI DİL',
      'İKİNCİ YABANCI DİL',
      'BEDEN EĞİTİMİ',
      'GÖRSEL SANATLAR',
      'MÜZİK'
    ],
  };

  @override
  void initState() {
    super.initState();
    _initializeSubjects();
    _loadFormTemplates();
  }

  Future<void> _loadFormTemplates() async {
    try {
      final templates = await FormService.getFormTemplates();
      setState(() {
        _formTemplates = templates;
      });
    } catch (e) {
      print('Form şablonları yüklenemedi: $e');
    }
  }

  void _initializeSubjects() {
    _subjects.clear();
    final availableSubjects = _schoolSubjects[_selectedSchoolType]!;
    for (int i = 0; i < _subjectCount; i++) {
      _subjects.add(SubjectModel(
        name: availableSubjects[i % availableSubjects.length],
        questionCount: 20,
        answers: List.filled(20, 'A'),
        points: List.filled(20, 1.0),
      ));
    }
  }

  void _updateSubjectCount(int newCount) {
    setState(() {
      if (newCount > _subjectCount) {
        final availableSubjects = _schoolSubjects[_selectedSchoolType]!;
        for (int i = _subjectCount; i < newCount; i++) {
          _subjects.add(SubjectModel(
            name: availableSubjects[i % availableSubjects.length],
            questionCount: 20,
            answers: List.filled(20, 'A'),
            points: List.filled(20, 1.0),
          ));
        }
      } else {
        _subjects.removeRange(newCount, _subjectCount);
      }
      _subjectCount = newCount;
    });
  }

  void _onSchoolTypeChanged(String? newValue) {
    if (newValue != null) {
      setState(() {
        _selectedSchoolType = newValue;
        _subjectCount = 1;
        _initializeSubjects();
      });
    }
  }

  Future<void> _saveForm() async {
    if (!_formKey.currentState!.validate()) return;

    setState(() => _isSaving = true);

    try {
      // Backend için veri hazırla
      final subjectsData = _subjects
          .map((subject) => {
                'name': subject.name,
                'question_count': subject.questionCount,
                'points_per_question':
                    subject.points.isNotEmpty ? subject.points[0] : 1.0,
                'answers': subject.answers,
                'points': subject.points,
              })
          .toList();

      // Backend'e gönder
      final result = await FormService.createAnswerKey(
        _formNameController.text,
        _selectedSchoolType,
        subjectsData,
        formTemplate: _selectedFormTemplate,
      );

      if (!mounted) return;

      if (result['success'] == true) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(
            content: Text('Cevap anahtarı başarıyla kaydedildi!'),
            backgroundColor: Colors.green,
          ),
        );
        Navigator.pop(context, true); // true = kaydedildi
      } else {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Hata: ${result['error']}'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('Bağlantı hatası: $e'),
            backgroundColor: Colors.red,
          ),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  // YENİ: Kompakt Cevap Grid'i
  Widget _buildCompactAnswerGrid(SubjectModel subject, int subjectIndex) {
    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Başlık
            Row(
              children: [
                Icon(Icons.quiz, color: Colors.deepPurple, size: 18),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    '${subject.name} - Cevap Anahtarı',
                    style: const TextStyle(
                      fontSize: 14,
                      fontWeight: FontWeight.bold,
                      color: Colors.deepPurple,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.deepPurple.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    '${subject.questionCount} Soru',
                    style: const TextStyle(
                      fontSize: 12,
                      fontWeight: FontWeight.w600,
                      color: Colors.deepPurple,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Kompakt Soru Listesi
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.grey[50],
                borderRadius: BorderRadius.circular(8),
              ),
              child: Column(
                children: [
                  // Başlık Satırı
                  const Row(
                    children: [
                      Expanded(
                        flex: 2,
                        child: Text(
                          'Soru',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey,
                          ),
                        ),
                      ),
                      Expanded(
                        child: Text(
                          'Cevap',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                      Expanded(
                        child: Text(
                          'Puan',
                          style: TextStyle(
                            fontSize: 12,
                            fontWeight: FontWeight.bold,
                            color: Colors.grey,
                          ),
                          textAlign: TextAlign.center,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 8),

                  // Soru Listesi
                  ListView.separated(
                    shrinkWrap: true,
                    physics: const NeverScrollableScrollPhysics(),
                    itemCount: subject.questionCount,
                    separatorBuilder: (context, index) =>
                        const Divider(height: 8),
                    itemBuilder: (context, questionIndex) {
                      return _buildQuestionRow(
                        questionIndex,
                        subject,
                        subjectIndex,
                      );
                    },
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  // YENİ: Tekil Soru Satırı
  Widget _buildQuestionRow(
      int questionIndex, SubjectModel subject, int subjectIndex) {
    return Container(
      padding: const EdgeInsets.symmetric(vertical: 6, horizontal: 4),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(6),
      ),
      child: Row(
        children: [
          // Soru Numarası
          Expanded(
            flex: 2,
            child: Container(
              padding: const EdgeInsets.symmetric(vertical: 4),
              decoration: BoxDecoration(
                color: Colors.deepPurple.withOpacity(0.1),
                borderRadius: BorderRadius.circular(4),
              ),
              child: Text(
                'Soru ${questionIndex + 1}',
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.w600,
                  color: Colors.deepPurple,
                ),
                textAlign: TextAlign.center,
              ),
            ),
          ),
          const SizedBox(width: 8),

          // Cevap Seçimi
          Expanded(
            child: Container(
              height: 32,
              decoration: BoxDecoration(
                color: _getAnswerColor(subject.answers[questionIndex]),
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: Colors.grey.shade400),
              ),
              child: Center(
                child: DropdownButton<String>(
                  value: subject.answers[questionIndex],
                  underline: const SizedBox(),
                  icon: const Icon(Icons.arrow_drop_down,
                      size: 16, color: Colors.white),
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                    color: Colors.white,
                  ),
                  dropdownColor: Colors.grey[850],
                  items: ['A', 'B', 'C', 'D', 'E']
                      .map((option) => DropdownMenuItem(
                            value: option,
                            child: Padding(
                              padding:
                                  const EdgeInsets.symmetric(horizontal: 8),
                              child: Text(
                                option,
                                style: const TextStyle(
                                  fontSize: 12,
                                  fontWeight: FontWeight.bold,
                                  color: Colors.white,
                                ),
                              ),
                            ),
                          ))
                      .toList(),
                  onChanged: (value) {
                    setState(() {
                      final newAnswers =
                          List<String>.from(_subjects[subjectIndex].answers);
                      newAnswers[questionIndex] = value!;
                      _subjects[subjectIndex] =
                          _subjects[subjectIndex].copyWith(answers: newAnswers);
                    });
                  },
                ),
              ),
            ),
          ),
          const SizedBox(width: 8),

          // Puan Girişi
          Expanded(
            child: Container(
              height: 32,
              decoration: BoxDecoration(
                color: Colors.white,
                borderRadius: BorderRadius.circular(6),
                border: Border.all(color: Colors.grey.shade400),
              ),
              child: TextFormField(
                initialValue: subject.points[questionIndex].toStringAsFixed(1),
                textAlign: TextAlign.center,
                style: const TextStyle(
                  fontSize: 12,
                  fontWeight: FontWeight.bold,
                  color: Colors.green,
                ),
                keyboardType: TextInputType.number,
                decoration: const InputDecoration(
                  hintText: '1.0',
                  hintStyle: TextStyle(fontSize: 10, color: Colors.grey),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.all(4),
                  isDense: true,
                ),
                onChanged: (value) {
                  final point = double.tryParse(value) ?? 1.0;
                  setState(() {
                    final newPoints =
                        List<double>.from(_subjects[subjectIndex].points);
                    newPoints[questionIndex] = point;
                    _subjects[subjectIndex] =
                        _subjects[subjectIndex].copyWith(points: newPoints);
                  });
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Color _getAnswerColor(String answer) {
    switch (answer) {
      case 'A':
        return Colors.red.shade600;
      case 'B':
        return Colors.blue.shade600;
      case 'C':
        return Colors.green.shade600;
      case 'D':
        return Colors.orange.shade600;
      case 'E':
        return Colors.purple.shade600;
      default:
        return Colors.grey.shade600;
    }
  }

  Widget _buildSubjectCard(int index) {
    final availableSubjects = _schoolSubjects[_selectedSchoolType]!;

    return Card(
      elevation: 2,
      margin: const EdgeInsets.symmetric(vertical: 8),
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: Colors.grey.shade300),
      ),
      child: Padding(
        padding: const EdgeInsets.all(12.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.subject, color: Colors.deepPurple, size: 18),
                const SizedBox(width: 6),
                Text(
                  'Ders ${index + 1}',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.deepPurple,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),

            // Ders Adı Seçimi
            DropdownButtonFormField<String>(
              value: _subjects[index].name,
              decoration: InputDecoration(
                labelText: 'Ders Adı',
                labelStyle: const TextStyle(color: Colors.deepPurple),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                isDense: true,
              ),
              style: const TextStyle(fontSize: 14),
              items: availableSubjects
                  .map((subject) => DropdownMenuItem(
                        value: subject,
                        child: Text(
                          subject,
                          style: const TextStyle(fontSize: 14),
                          overflow: TextOverflow.ellipsis,
                        ),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  _subjects[index] = _subjects[index].copyWith(name: value!);
                });
              },
            ),
            const SizedBox(height: 12),

            // Soru Sayısı
            TextFormField(
              initialValue: _subjects[index].questionCount.toString(),
              style: const TextStyle(fontSize: 14),
              decoration: InputDecoration(
                labelText: 'Soru Sayısı',
                labelStyle: const TextStyle(color: Colors.deepPurple),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8),
                ),
                contentPadding:
                    const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                isDense: true,
              ),
              keyboardType: TextInputType.number,
              onChanged: (value) {
                final questionCount = int.tryParse(value) ?? 20;
                setState(() {
                  _subjects[index] = _subjects[index].copyWith(
                    questionCount: questionCount,
                    answers: List.filled(questionCount, 'A'),
                    points: List.filled(questionCount, 1.0),
                  );
                });
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
      appBar: AppBar(
        title: const Text(
          'Yeni Form Oluştur',
          style: TextStyle(fontWeight: FontWeight.bold),
        ),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
        actions: [
          IconButton(
            onPressed: _saveForm,
            icon: const Icon(Icons.save),
          ),
        ],
      ),
      body: Form(
        key: _formKey,
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: ListView(
            children: [
              // Form Adı
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.description,
                              color: Colors.deepPurple, size: 18),
                          const SizedBox(width: 6),
                          const Text(
                            'Form Adı',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.deepPurple,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      TextFormField(
                        controller: _formNameController,
                        decoration: const InputDecoration(
                          hintText: 'Form adını giriniz...',
                          border: OutlineInputBorder(),
                          contentPadding:
                              EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          isDense: true,
                        ),
                        validator: (value) {
                          if (value == null || value.isEmpty) {
                            return 'Lütfen form adı giriniz';
                          }
                          return null;
                        },
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Form Şablonu
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.article_outlined,
                              color: Colors.deepPurple, size: 18),
                          const SizedBox(width: 6),
                          const Text(
                            'Form Şablonu',
                            style: TextStyle(
                              fontWeight: FontWeight.bold,
                              fontSize: 14,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        value: _selectedFormTemplate,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          contentPadding:
                              EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          isDense: true,
                        ),
                        items: [
                          const DropdownMenuItem(
                            value: 'simple',
                            child: Text('Basit Optik Form (Genel Amaçlı)'),
                          ),
                          ..._formTemplates
                              .where((template) => template['id'] != 'simple')
                              .map((template) {
                            return DropdownMenuItem(
                              value: template['id'] as String,
                              child: Text(
                                '${template['name']} - ${template['description']}',
                                style: const TextStyle(fontSize: 14),
                              ),
                            );
                          }).toList(),
                        ],
                        onChanged: (value) {
                          setState(() {
                            _selectedFormTemplate = value!;
                          });
                        },
                      ),
                      const SizedBox(height: 4),
                      Text(
                        _selectedFormTemplate == 'lgs_20_20'
                            ? '⚠️ LGS formları özel yapıya sahiptir. Öğrenci bilgileri ve bölüm bazlı cevaplar otomatik okunur.'
                            : 'ℹ️ Standart optik form şablonu. Tüm soruları manuel tanımlayın.',
                        style: TextStyle(
                          fontSize: 11,
                          color: Colors.grey[600],
                          fontStyle: FontStyle.italic,
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Okul Türü
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.school,
                              color: Colors.deepPurple, size: 18),
                          const SizedBox(width: 6),
                          const Text(
                            'Okul Türü',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.deepPurple,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 8),
                      DropdownButtonFormField<String>(
                        value: _selectedSchoolType,
                        decoration: const InputDecoration(
                          border: OutlineInputBorder(),
                          contentPadding:
                              EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                          isDense: true,
                        ),
                        items: ['Ortaokul', 'Lise']
                            .map((schoolType) => DropdownMenuItem(
                                  value: schoolType,
                                  child: Text(schoolType),
                                ))
                            .toList(),
                        onChanged: _onSchoolTypeChanged,
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 12),

              // Ders Sayısı
              Card(
                elevation: 2,
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Row(
                        children: [
                          Icon(Icons.library_books,
                              color: Colors.deepPurple, size: 18),
                          const SizedBox(width: 6),
                          const Text(
                            'Ders Sayısı',
                            style: TextStyle(
                              fontSize: 16,
                              fontWeight: FontWeight.bold,
                              color: Colors.deepPurple,
                            ),
                          ),
                        ],
                      ),
                      const SizedBox(height: 12),
                      Slider(
                        value: _subjectCount.toDouble(),
                        min: 1,
                        max: _schoolSubjects[_selectedSchoolType]!
                            .length
                            .toDouble(),
                        divisions:
                            _schoolSubjects[_selectedSchoolType]!.length - 1,
                        label: _subjectCount.toString(),
                        onChanged: (value) {
                          _updateSubjectCount(value.toInt());
                        },
                      ),
                      Center(
                        child: Text(
                          '$_subjectCount Ders',
                          style: const TextStyle(
                            fontSize: 16,
                            fontWeight: FontWeight.bold,
                            color: Colors.deepPurple,
                          ),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 16),

              // Ders Ayarları
              const Text(
                'Ders Ayarları',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.deepPurple,
                ),
              ),
              const SizedBox(height: 8),
              ...List.generate(
                  _subjectCount, (index) => _buildSubjectCard(index)),

              const SizedBox(height: 16),

              // Cevap Anahtarları
              const Text(
                'Cevap Anahtarları',
                style: TextStyle(
                  fontSize: 18,
                  fontWeight: FontWeight.bold,
                  color: Colors.deepPurple,
                ),
              ),
              const SizedBox(height: 8),
              ...List.generate(_subjectCount,
                  (index) => _buildCompactAnswerGrid(_subjects[index], index)),

              const SizedBox(height: 16),

              // Kaydet Butonu
              ElevatedButton(
                onPressed: _isSaving ? null : _saveForm,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  foregroundColor: Colors.white,
                  shape: RoundedRectangleBorder(
                    borderRadius: BorderRadius.circular(8),
                  ),
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
                child: _isSaving
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(
                          color: Colors.white,
                          strokeWidth: 2,
                        ),
                      )
                    : const Text(
                        'FORMU KAYDET',
                        style: TextStyle(
                            fontSize: 16, fontWeight: FontWeight.bold),
                      ),
              ),
              const SizedBox(height: 20),
            ],
          ),
        ),
      ),
    );
  }
}
