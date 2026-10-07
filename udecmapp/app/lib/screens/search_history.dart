// search_history.dart

class SearchHistory {
  final String building;
  final String floor;
  final String startPoint;
  final String endPoint;
  final String timestamp;

  SearchHistory({
    required this.building,
    required this.floor,
    required this.startPoint,
    required this.endPoint,
    required this.timestamp,
  });

  Map<String, dynamic> toJson() {
    return {
      'building': building,
      'floor': floor,
      'startPoint': startPoint,
      'endPoint': endPoint,
      'timestamp': timestamp,
    };
  }

  factory SearchHistory.fromJson(Map<String, dynamic> json) {
    return SearchHistory(
      building: json['building'],
      floor: json['floor'],
      startPoint: json['startPoint'],
      endPoint: json['endPoint'],
      timestamp: json['timestamp'],
    );
  }
}