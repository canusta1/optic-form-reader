import 'package:flutter/material.dart';
import 'package:optic_form_reader/create_form_screen.dart';
import 'form_service.dart';

// FormModel ve SubjectModel'i bu dosyada tanımla
class FormModel {
  final int? id;
  final String name;
  final List<SubjectModel> subjects;
  final DateTime createdAt;
  final int? studentCount;
  final String? schoolType;
  final int? cachedTotalQuestions;
  final double? cachedTotalPoints;
  final int? cachedSubjectCount;

  FormModel({
    this.id,
    required this.name,
    required this.subjects,
    required this.createdAt,
    this.studentCount,
    this.schoolType,
    this.cachedTotalQuestions,
    this.cachedTotalPoints,
    this.cachedSubjectCount,
  });

  int get totalQuestions {
    if (subjects.isNotEmpty) {
      return subjects.fold(0, (sum, subject) => sum + subject.questionCount);
    }
    return cachedTotalQuestions ?? 0;
  }

  double get totalPoints {
    if (subjects.isNotEmpty) {
      return subjects.fold(0.0, (sum, subject) => sum + subject.totalPoints);
    }
    return cachedTotalPoints ?? 0.0;
  }

  int get subjectCount {
    if (subjects.isNotEmpty) {
      return subjects.length;
    }
    return cachedSubjectCount ?? 0;
  }
}

class SubjectModel {
  String name;
  int questionCount;
  List<String> answers;
  List<double> points;

  SubjectModel({
    required this.name,
    required this.questionCount,
    required this.answers,
    required this.points,
  });

  double get totalPoints {
    return points.fold(0.0, (sum, point) => sum + point);
  }
}

// FormCard'ı bu dosyada tanımla
class FormCard extends StatelessWidget {
  final FormModel form;
  final VoidCallback onDelete;

  const FormCard({
    super.key,
    required this.form,
    required this.onDelete,
  });

  @override
  Widget build(BuildContext context) {
    return Card(
      elevation: 8,
      shadowColor: Colors.black.withOpacity(0.1),
      margin: const EdgeInsets.symmetric(vertical: 10),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
      child: Container(
        decoration: BoxDecoration(
          borderRadius: BorderRadius.circular(20),
          gradient: LinearGradient(
            colors: [Colors.white, Colors.grey.shade50],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Padding(
          padding: const EdgeInsets.all(20.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          form.name,
                          style: const TextStyle(
                            fontSize: 20,
                            fontWeight: FontWeight.bold,
                            color: Color(0xFF1A237E),
                          ),
                          overflow: TextOverflow.ellipsis,
                        ),
                        const SizedBox(height: 4),
                        Text(
                          'Oluşturulma: ${_formatDate(form.createdAt)}',
                          style: TextStyle(
                            color: Colors.grey[600],
                            fontSize: 12,
                          ),
                        ),
                      ],
                    ),
                  ),
                  Container(
                    decoration: BoxDecoration(
                      color: Colors.red.withOpacity(0.1),
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: IconButton(
                      onPressed: () => _showDeleteDialog(context),
                      icon: const Icon(Icons.delete_outline_rounded,
                          color: Colors.red),
                      tooltip: 'Formu Sil',
                    ),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              const Divider(height: 1),
              const SizedBox(height: 16),
              Wrap(
                spacing: 12,
                runSpacing: 8,
                children: [
                  _buildInfoChip(
                    '${form.subjectCount} Ders',
                    Icons.subject_rounded,
                    const Color(0xFFE3F2FD),
                    const Color(0xFF1565C0),
                  ),
                  _buildInfoChip(
                    '${form.totalQuestions} Soru',
                    Icons.quiz_rounded,
                    const Color(0xFFE8F5E9),
                    const Color(0xFF2E7D32),
                  ),
                  _buildInfoChip(
                    '${form.totalPoints.toStringAsFixed(0)} Puan',
                    Icons.star_rounded,
                    const Color(0xFFFFF8E1),
                    const Color(0xFFF9A825),
                  ),
                  if (form.studentCount != null && form.studentCount! > 0)
                    _buildInfoChip(
                      '${form.studentCount} Öğrenci',
                      Icons.people_alt_rounded,
                      const Color(0xFFF3E5F5),
                      const Color(0xFF7B1FA2),
                    ),
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoChip(
      String text, IconData icon, Color bgColor, Color iconColor) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: iconColor.withOpacity(0.2)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 18, color: iconColor),
          const SizedBox(width: 8),
          Text(
            text,
            style: TextStyle(
              color: iconColor,
              fontWeight: FontWeight.w600,
              fontSize: 13,
            ),
          ),
        ],
      ),
    );
  }

  String _formatDate(DateTime date) {
    return '${date.day}/${date.month}/${date.year}';
  }

  void _showDeleteDialog(BuildContext context) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Formu Sil'),
        content:
            Text('"${form.name}" formunu silmek istediğinizden emin misiniz?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('İptal'),
          ),
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              onDelete();
            },
            child: const Text(
              'Sil',
              style: TextStyle(color: Colors.red),
            ),
          ),
        ],
      ),
    );
  }
}

class FormsScreen extends StatefulWidget {
  const FormsScreen({super.key});

  @override
  State<FormsScreen> createState() => _FormsScreenState();
}

class _FormsScreenState extends State<FormsScreen> {
  List<FormModel> _forms = [];
  bool _isLoading = true;

  @override
  void initState() {
    super.initState();
    _loadForms();
  }

  Future<void> _loadForms() async {
    setState(() => _isLoading = true);

    try {
      final answerKeys = await FormService.getAnswerKeys();

      setState(() {
        _forms = answerKeys.map((key) {
          return FormModel(
            id: key['id'],
            name: key['exam_name'],
            subjects: [], // Detayları lazım olduğunda çekilir
            createdAt: DateTime.parse(key['created_at']),
            studentCount: key['student_count'] ?? 0,
            schoolType: key['school_type'],
            cachedTotalQuestions: key['total_questions'],
            cachedTotalPoints: (key['total_points'] as num?)?.toDouble(),
            cachedSubjectCount: key['subject_count'],
          );
        }).toList();
        _isLoading = false;
      });
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Formlar yüklenemedi: $e')),
        );
      }
    }
  }

  void _navigateToCreateForm() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CreateFormScreen()),
    );

    if (result == true) {
      // Yeniden yükle
      _loadForms();
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: Colors.transparent,
      appBar: AppBar(
        title: const Text('Formlarım'),
        centerTitle: true,
        backgroundColor: Colors.transparent,
        elevation: 0,
        actions: [
          IconButton(
            icon: const Icon(Icons.refresh_rounded),
            onPressed: _loadForms,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _forms.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Container(
                        padding: const EdgeInsets.all(30),
                        decoration: BoxDecoration(
                          color: Colors.white,
                          shape: BoxShape.circle,
                          boxShadow: [
                            BoxShadow(
                              color: Colors.grey.withOpacity(0.2),
                              blurRadius: 20,
                              spreadRadius: 5,
                            ),
                          ],
                        ),
                        child: Icon(Icons.assignment_outlined,
                            size: 80, color: Colors.grey.shade400),
                      ),
                      const SizedBox(height: 24),
                      Text(
                        'Henüz form oluşturmadınız',
                        style: TextStyle(
                          fontSize: 20,
                          fontWeight: FontWeight.bold,
                          color: Colors.grey.shade700,
                        ),
                      ),
                      const SizedBox(height: 12),
                      Text(
                        'Aşağıdaki + butonuna tıklayarak\nyeni bir optik form şablonu oluşturun',
                        textAlign: TextAlign.center,
                        style:
                            TextStyle(color: Colors.grey.shade600, height: 1.5),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.fromLTRB(16, 8, 16, 80),
                  itemCount: _forms.length,
                  itemBuilder: (context, index) {
                    return FormCard(
                      form: _forms[index],
                      onDelete: () {
                        // Silme işlemi - şimdilik sadece refresh
                        _loadForms();
                      },
                    );
                  },
                ),
      floatingActionButton: Padding(
        padding: const EdgeInsets.only(bottom: 80.0),
        child: Container(
          decoration: BoxDecoration(
            gradient: const LinearGradient(
              colors: [Color(0xFF2979FF), Color(0xFF00E5FF)],
              begin: Alignment.topLeft,
              end: Alignment.bottomRight,
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
          child: FloatingActionButton(
            onPressed: _navigateToCreateForm,
            backgroundColor: Colors.transparent,
            elevation: 0,
            shape:
                RoundedRectangleBorder(borderRadius: BorderRadius.circular(16)),
            child: const Icon(Icons.add_rounded, color: Colors.white, size: 32),
          ),
        ),
      ),
    );
  }
}
