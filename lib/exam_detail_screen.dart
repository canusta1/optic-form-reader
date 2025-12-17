import 'package:flutter/material.dart';
import 'package:pdf/pdf.dart';
import 'package:pdf/widgets.dart' as pw;
import 'package:printing/printing.dart';
import 'package:intl/intl.dart';
import 'form_service.dart';
import 'student_result_detail_screen.dart';

class ExamDetailScreen extends StatefulWidget {
  final int answerKeyId;
  final String examName;

  const ExamDetailScreen({
    super.key,
    required this.answerKeyId,
    required this.examName,
  });

  @override
  State<ExamDetailScreen> createState() => _ExamDetailScreenState();
}

class _ExamDetailScreenState extends State<ExamDetailScreen> {
  List<dynamic> _results = [];
  bool _isLoading = true;
  Map<String, dynamic>? _answerKeyDetail;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  Future<void> _loadData() async {
    setState(() => _isLoading = true);
    try {
      final results = await FormService.getResults(widget.answerKeyId);
      final keyDetail =
          await FormService.getAnswerKeyDetail(widget.answerKeyId);

      // Başarı sırasına göre sırala (Yüksekten düşüğe)
      results.sort((a, b) {
        final scoreA = (a['success_rate'] as num?)?.toDouble() ?? 0;
        final scoreB = (b['success_rate'] as num?)?.toDouble() ?? 0;
        return scoreB.compareTo(scoreA);
      });

      if (mounted) {
        setState(() {
          _results = results;
          _answerKeyDetail = keyDetail;
          _isLoading = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoading = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Veriler yüklenemedi: $e')),
        );
      }
    }
  }

  Future<void> _generatePdf() async {
    final doc = pw.Document();
    final font = await PdfGoogleFonts.robotoRegular();
    final boldFont = await PdfGoogleFonts.robotoBold();

    doc.addPage(
      pw.MultiPage(
        pageFormat: PdfPageFormat.a4,
        build: (pw.Context context) {
          return [
            pw.Header(
              level: 0,
              child: pw.Row(
                mainAxisAlignment: pw.MainAxisAlignment.spaceBetween,
                children: [
                  pw.Text(widget.examName,
                      style: pw.TextStyle(font: boldFont, fontSize: 24)),
                  pw.Text(DateFormat('dd/MM/yyyy').format(DateTime.now()),
                      style: pw.TextStyle(font: font)),
                ],
              ),
            ),
            pw.SizedBox(height: 20),
            pw.Table.fromTextArray(
              context: context,
              headerStyle:
                  pw.TextStyle(font: boldFont, fontWeight: pw.FontWeight.bold),
              cellStyle: pw.TextStyle(font: font),
              headers: ['Sıra', 'Öğrenci Adı', 'Numara', 'Puan', 'Başarı (%)'],
              data: List<List<dynamic>>.generate(
                _results.length,
                (index) {
                  final result = _results[index];
                  return [
                    (index + 1).toString(),
                    result['student_name'] ?? 'İsimsiz',
                    result['student_number']?.toString() ?? '-',
                    result['total_score']?.toStringAsFixed(2) ?? '0',
                    '%${result['success_rate']?.toStringAsFixed(1) ?? '0'}',
                  ];
                },
              ),
            ),
          ];
        },
      ),
    );

    await Printing.layoutPdf(
      onLayout: (PdfPageFormat format) async => doc.save(),
      name: '${widget.examName}_sonuclar.pdf',
    );
  }

  void _showAnswerKeyDialog() {
    if (_answerKeyDetail == null) return;

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: Text('${widget.examName} - Cevap Anahtarı'),
        content: SizedBox(
          width: double.maxFinite,
          child: ListView.builder(
            shrinkWrap: true,
            itemCount: (_answerKeyDetail!['subjects'] as List).length,
            itemBuilder: (context, index) {
              final subject = _answerKeyDetail!['subjects'][index];
              final answers = List<String>.from(subject['answers']);

              return Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8.0),
                    child: Text(
                      subject['subject_name'],
                      style: const TextStyle(
                          fontWeight: FontWeight.bold, fontSize: 16),
                    ),
                  ),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: List.generate(answers.length, (i) {
                      return Container(
                        padding: const EdgeInsets.symmetric(
                            horizontal: 8, vertical: 4),
                        decoration: BoxDecoration(
                          color: Colors.grey[200],
                          borderRadius: BorderRadius.circular(4),
                          border: Border.all(color: Colors.grey[400]!),
                        ),
                        child: Text(
                          '${i + 1}. ${answers[i]}',
                          style: const TextStyle(fontWeight: FontWeight.w500),
                        ),
                      );
                    }),
                  ),
                  const Divider(),
                ],
              );
            },
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Kapat'),
          ),
        ],
      ),
    );
  }

  Color _getScoreColor(double? successRate) {
    if (successRate == null) return Colors.grey;
    if (successRate >= 85) return const Color(0xFF00E676);
    if (successRate >= 70) return const Color(0xFF2979FF);
    if (successRate >= 50) return const Color(0xFFFF9100);
    return const Color(0xFFFF1744);
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: const Color(0xFFF5F7FA),
      appBar: AppBar(
        title: Text(widget.examName,
            style: const TextStyle(color: Colors.black87)),
        backgroundColor: Colors.white,
        elevation: 0,
        iconTheme: const IconThemeData(color: Colors.black87),
        actions: [
          IconButton(
            icon: const Icon(Icons.key_rounded),
            tooltip: 'Cevap Anahtarı',
            onPressed: _showAnswerKeyDialog,
          ),
          IconButton(
            icon: const Icon(Icons.picture_as_pdf_rounded),
            tooltip: 'PDF İndir',
            onPressed: _results.isEmpty ? null : _generatePdf,
          ),
        ],
      ),
      body: _isLoading
          ? const Center(child: CircularProgressIndicator())
          : _results.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.assignment_outlined,
                          size: 64, color: Colors.grey[400]),
                      const SizedBox(height: 16),
                      Text(
                        'Henüz bu sınav için sonuç yok',
                        style: TextStyle(color: Colors.grey[600], fontSize: 16),
                      ),
                    ],
                  ),
                )
              : ListView.builder(
                  padding: const EdgeInsets.all(16),
                  itemCount: _results.length,
                  itemBuilder: (context, index) {
                    final result = _results[index];
                    final studentName = result['student_name'] ?? 'İsimsiz';
                    final studentNumber = result['student_number'] ?? '-';
                    final successRate =
                        (result['success_rate'] as num?)?.toDouble();
                    final totalScore =
                        (result['total_score'] as num?)?.toDouble();
                    final resultId = result['id'] as int?;

                    return Card(
                      margin: const EdgeInsets.only(bottom: 12),
                      elevation: 2,
                      shape: RoundedRectangleBorder(
                          borderRadius: BorderRadius.circular(12)),
                      child: InkWell(
                        onTap: resultId != null
                            ? () {
                                Navigator.push(
                                  context,
                                  MaterialPageRoute(
                                    builder: (context) =>
                                        StudentResultDetailScreen(
                                      resultId: resultId,
                                      studentName: studentName,
                                    ),
                                  ),
                                );
                              }
                            : null,
                        borderRadius: BorderRadius.circular(12),
                        child: ListTile(
                          contentPadding: const EdgeInsets.all(16),
                          leading: CircleAvatar(
                            backgroundColor:
                                _getScoreColor(successRate).withOpacity(0.1),
                            child: Text(
                              '${index + 1}',
                              style: TextStyle(
                                color: _getScoreColor(successRate),
                                fontWeight: FontWeight.bold,
                              ),
                            ),
                          ),
                          title: Text(
                            studentName,
                            style: const TextStyle(
                                fontWeight: FontWeight.bold, fontSize: 16),
                          ),
                          subtitle: Text('No: $studentNumber'),
                          trailing: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            crossAxisAlignment: CrossAxisAlignment.end,
                            children: [
                              Text(
                                '%${successRate?.toStringAsFixed(1) ?? "0"}',
                                style: TextStyle(
                                  color: _getScoreColor(successRate),
                                  fontWeight: FontWeight.bold,
                                  fontSize: 18,
                                ),
                              ),
                              Text(
                                '${totalScore?.toStringAsFixed(1) ?? "0"} Puan',
                                style: TextStyle(
                                  color: Colors.grey[600],
                                  fontSize: 12,
                                ),
                              ),
                            ],
                          ),
                        ),
                      ),
                    );
                  },
                ),
    );
  }
}
