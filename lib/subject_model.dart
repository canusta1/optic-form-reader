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

  Map<String, dynamic> toJson() {
    return {
      'name': name,
      'questionCount': questionCount,
      'answers': answers,
      'points': points,
    };
  }

  factory SubjectModel.fromJson(Map<String, dynamic> json) {
    return SubjectModel(
      name: json['name'],
      questionCount: json['questionCount'],
      answers: List<String>.from(json['answers']),
      points: List<double>.from(json['points'].map((x) => x.toDouble())),
    );
  }

  double get totalPoints {
    return points.fold(0.0, (sum, point) => sum + point);
  }
}