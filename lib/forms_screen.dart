import 'package:flutter/material.dart';
import 'package:optic_form_reader/create_form_screen.dart';

// FormModel ve SubjectModel'i bu dosyada tanımla
class FormModel {
  final String name;
  final List<SubjectModel> subjects;
  final DateTime createdAt;

  FormModel({
    required this.name,
    required this.subjects,
    required this.createdAt,
  });

  int get totalQuestions {
    return subjects.fold(0, (sum, subject) => sum + subject.questionCount);
  }

  double get totalPoints {
    return subjects.fold(0.0, (sum, subject) => sum + subject.totalPoints);
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
      elevation: 4,
      margin: const EdgeInsets.symmetric(vertical: 8),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Expanded(
                  child: Text(
                    form.name,
                    style: const TextStyle(
                      fontSize: 18,
                      fontWeight: FontWeight.bold,
                    ),
                    overflow: TextOverflow.ellipsis,
                  ),
                ),
                IconButton(
                  onPressed: () => _showDeleteDialog(context),
                  icon: const Icon(Icons.delete, color: Colors.red),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              'Oluşturulma: ${_formatDate(form.createdAt)}',
              style: TextStyle(
                color: Colors.grey[600],
                fontSize: 12,
              ),
            ),
            const SizedBox(height: 8),
            Wrap(
              spacing: 8,
              runSpacing: 4,
              children: [
                _buildInfoChip(
                  '${form.subjects.length} Ders',
                  Icons.subject,
                ),
                _buildInfoChip(
                  '${form.totalQuestions} Soru',
                  Icons.quiz,
                ),
                _buildInfoChip(
                  '${form.totalPoints.toStringAsFixed(0)} Puan',
                  Icons.star,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoChip(String text, IconData icon) {
    return Chip(
      label: Text(text),
      avatar: Icon(icon, size: 16),
      materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
      visualDensity: VisualDensity.compact,
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
        content: Text('"${form.name}" formunu silmek istediğinizden emin misiniz?'),
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
  final List<FormModel> _forms = [];

  void _addNewForm(FormModel newForm) {
    setState(() {
      _forms.add(newForm);
    });
  }

  void _deleteForm(int index) {
    setState(() {
      _forms.removeAt(index);
    });
    ScaffoldMessenger.of(context).showSnackBar(
      const SnackBar(
        content: Text('Form silindi'),
        backgroundColor: Colors.red,
      ),
    );
  }

  void _navigateToCreateForm() async {
    final result = await Navigator.push(
      context,
      MaterialPageRoute(builder: (context) => const CreateFormScreen()),
    );

    if (result != null && result is FormModel) {
      _addNewForm(result);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Formlarım'),
        centerTitle: true,
      ),
      body: _forms.isEmpty
          ? const Center(
              child: Column(
                mainAxisAlignment: MainAxisAlignment.center,
                children: [
                  Icon(Icons.assignment, size: 80, color: Colors.grey),
                  SizedBox(height: 20),
                  Text(
                    'Henüz form oluşturmadınız',
                    style: TextStyle(fontSize: 18, color: Colors.grey),
                  ),
                  SizedBox(height: 10),
                  Text(
                    'Aşağıdaki + butonuna tıklayarak yeni form oluşturun',
                    textAlign: TextAlign.center,
                    style: TextStyle(color: Colors.grey),
                  ),
                ],
              ),
            )
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: _forms.length,
              itemBuilder: (context, index) {
                return FormCard(
                  form: _forms[index],
                  onDelete: () => _deleteForm(index),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: _navigateToCreateForm,
        backgroundColor: Colors.deepPurple,
        child: const Icon(Icons.add, color: Colors.white),
      ),
    );
  }
}