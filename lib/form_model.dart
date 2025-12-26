class FormModel {
  final String name;
  final List<SubjectModel> subjects;
  final DateTime createdAt;
  final String schoolType;

  FormModel({
    required this.name,
    required this.subjects,
    required this.createdAt,
    required this.schoolType,
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

  SubjectModel copyWith({
    String? name,
    int? questionCount,
    List<String>? answers,
    List<double>? points,
  }) {
    return SubjectModel(
      name: name ?? this.name,
      questionCount: questionCount ?? this.questionCount,
      answers: answers ?? List.from(this.answers),
      points: points ?? List.from(this.points),
    );
  }

  double get totalPoints {
    return points.fold(0.0, (sum, point) => sum + point);
  }
}