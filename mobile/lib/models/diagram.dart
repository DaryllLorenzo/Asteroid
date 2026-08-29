import 'dart:ui';

enum NodeKind { actor, agent, hardGoal, softGoal, plan, resource }

enum EdgeKind { dependency, why, meansEnd, orDecomposition, andDecomposition, contribution }

extension NodeKindInfo on NodeKind {
  String get key => switch (this) {
        NodeKind.actor => 'actor',
        NodeKind.agent => 'agent',
        NodeKind.hardGoal => 'hard_goal',
        NodeKind.softGoal => 'soft_goal',
        NodeKind.plan => 'plan',
        NodeKind.resource => 'resource',
      };

  String get label => switch (this) {
        NodeKind.actor => 'Actor',
        NodeKind.agent => 'Agent',
        NodeKind.hardGoal => 'Hard Goal',
        NodeKind.softGoal => 'Soft Goal',
        NodeKind.plan => 'Plan',
        NodeKind.resource => 'Resource',
      };

  bool get isEntity => this == NodeKind.actor || this == NodeKind.agent;

  int get fill => switch (this) {
        NodeKind.actor => 0xff6496fa,
        NodeKind.agent => 0xfffa9664,
        NodeKind.hardGoal => 0xff65a86a,
        NodeKind.softGoal => 0xffdcdcb4,
        NodeKind.plan => 0xff7599e8,
        NodeKind.resource => 0xffa978d4,
      };

  static NodeKind parse(String value) => NodeKind.values.firstWhere(
        (kind) => kind.key == value,
        orElse: () => NodeKind.hardGoal,
      );
}

extension EdgeKindInfo on EdgeKind {
  String get key => switch (this) {
        EdgeKind.dependency => 'dependency_link',
        EdgeKind.why => 'why_link',
        EdgeKind.meansEnd => 'means_end',
        EdgeKind.orDecomposition => 'or_decomposition',
        EdgeKind.andDecomposition => 'and_decomposition',
        EdgeKind.contribution => 'contribution',
      };

  String get label => switch (this) {
        EdgeKind.dependency => 'Dependency',
        EdgeKind.why => 'Why',
        EdgeKind.meansEnd => 'Means-End',
        EdgeKind.orDecomposition => 'OR',
        EdgeKind.andDecomposition => 'AND',
        EdgeKind.contribution => 'Contribution',
      };

  static EdgeKind parse(String value) {
    if (value == 'dependency' || value == 'simple' || value == 'dashed') {
      return EdgeKind.dependency;
    }
    if (value == 'why') return EdgeKind.why;
    return EdgeKind.values.firstWhere(
      (kind) => kind.key == value,
      orElse: () => EdgeKind.dependency,
    );
  }
}

class DiagramNode {
  DiagramNode({
    required this.id,
    required this.kind,
    required this.position,
    required this.label,
    this.radius = 52,
    int? fillColor,
    this.borderColor = 0xff172033,
    int? textColor,
    this.fontSize = 13,
    this.showSubcanvas = false,
    this.subcanvasRadius = 130,
    this.subcanvasOffset = Offset.zero,
    this.parentId,
  })  : fillColor = fillColor ?? kind.fill,
        textColor = textColor ?? (kind == NodeKind.softGoal ? 0xff111827 : 0xffffffff);

  final String id;
  NodeKind kind;
  Offset position;
  String label;
  double radius;
  int fillColor;
  int borderColor;
  int textColor;
  double fontSize;
  bool showSubcanvas;
  double subcanvasRadius;
  Offset subcanvasOffset;
  String? parentId;

  DiagramNode copy() => DiagramNode(
        id: id,
        kind: kind,
        position: position,
        label: label,
        radius: radius,
        fillColor: fillColor,
        borderColor: borderColor,
        textColor: textColor,
        fontSize: fontSize,
        showSubcanvas: showSubcanvas,
        subcanvasRadius: subcanvasRadius,
        subcanvasOffset: subcanvasOffset,
        parentId: parentId,
      );

  Map<String, Object?> toAstr(int numericId, Map<String, int> idMap) => {
        'id': numericId,
        'type': kind.key,
        'position': {'x': position.dx, 'y': position.dy},
        'properties': {
          'radius': radius,
          'label': label,
          'color': colorHex(fillColor),
          'border_color': colorHex(borderColor),
          'text_color': colorHex(textColor),
          'font_size': fontSize,
          'content_offset_x': subcanvasOffset.dx,
          'content_offset_y': subcanvasOffset.dy,
          'text_width': radius * 2,
          'text_align': 'center',
        },
        'model_properties': {
          'show_subcanvas': showSubcanvas,
          'x': position.dx,
          'y': position.dy,
          'radius': radius,
          'label': label,
          'color': colorHex(fillColor),
          'border_color': colorHex(borderColor),
          'text_color': colorHex(textColor),
          'font_size': fontSize,
          'content_offset_x': subcanvasOffset.dx,
          'content_offset_y': subcanvasOffset.dy,
          'text_width': radius * 2,
          'text_align': 'center',
        },
        'parent_id': parentId == null ? null : idMap[parentId],
        if (kind.isEntity)
          'subcanvas': {
            'visible': showSubcanvas,
            'radius': subcanvasRadius,
            'original_radius': subcanvasRadius,
          },
      };

  static DiagramNode fromAstr(Map<String, dynamic> json) {
    final properties = Map<String, dynamic>.from(
      (json['model_properties'] ?? json['properties'] ?? const {}) as Map,
    );
    final position = Map<String, dynamic>.from(
      (json['position'] ?? const {'x': 0, 'y': 0}) as Map,
    );
    final kind = NodeKindInfo.parse('${json['type'] ?? 'hard_goal'}');
    return DiagramNode(
      id: '${json['id']}',
      kind: kind,
      position: Offset(_number(position['x']), _number(position['y'])),
      label: '${properties['label'] ?? kind.label}',
      radius: _number(properties['radius'], 52),
      fillColor: parseColor(properties['color'], kind.fill),
      borderColor: parseColor(properties['border_color'], 0xff172033),
      textColor: parseColor(
        properties['text_color'],
        kind == NodeKind.softGoal ? 0xff111827 : 0xffffffff,
      ),
      fontSize: _number(properties['font_size'], 13),
      showSubcanvas: properties['show_subcanvas'] == true ||
          (json['subcanvas'] is Map && (json['subcanvas'] as Map)['visible'] == true),
      subcanvasRadius: json['subcanvas'] is Map
          ? _number((json['subcanvas'] as Map)['radius'], 130)
          : 130,
      subcanvasOffset: Offset(
        _number(properties['content_offset_x']),
        _number(properties['content_offset_y']),
      ),
      parentId: json['parent_id']?.toString(),
    );
  }
}

class DiagramEdge {
  DiagramEdge({required this.id, required this.kind, required this.sourceId, required this.targetId});

  final String id;
  EdgeKind kind;
  String sourceId;
  String targetId;

  Map<String, Object?> toAstr(Map<String, int> idMap) => {
        'type': kind.key,
        'source_id': idMap[sourceId],
        'target_id': idMap[targetId],
        'properties': <String, Object?>{},
        'parent_id': null,
        'control_points': <Object>[],
      };

  static DiagramEdge fromAstr(Map<String, dynamic> json, int index) => DiagramEdge(
        id: 'edge_$index',
        kind: EdgeKindInfo.parse('${json['type'] ?? 'dependency'}'),
        sourceId: '${json['source_id']}',
        targetId: '${json['target_id']}',
      );
}

double _number(Object? value, [double fallback = 0]) => value is num ? value.toDouble() : fallback;

String colorHex(int value) => '#${(value & 0x00ffffff).toRadixString(16).padLeft(6, '0')}';

int parseColor(Object? value, int fallback) {
  if (value is int) return value;
  if (value is String) {
    final clean = value.replaceFirst('#', '');
    final parsed = int.tryParse(clean, radix: 16);
    if (parsed != null) return 0xff000000 | parsed;
  }
  return fallback;
}
