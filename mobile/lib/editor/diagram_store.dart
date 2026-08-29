import 'dart:async';
import 'dart:convert';
import 'dart:typed_data';
import 'dart:ui';

import 'package:file_picker/file_picker.dart';
import 'package:flutter/foundation.dart';
import 'package:shared_preferences/shared_preferences.dart';

import '../models/diagram.dart';

class DiagramStore extends ChangeNotifier {
  static const _autosaveKey = 'asteroid.autosave.v1';
  static const _darkKey = 'asteroid.dark';
  static const _languageKey = 'asteroid.language';

  final List<DiagramNode> nodes = [];
  final List<DiagramEdge> edges = [];
  final List<String> _history = [];
  int _historyIndex = -1;
  int _serial = 0;
  Timer? _autosaveTimer;

  String? selectedNodeId;
  String? selectedEdgeId;
  String? activeCanvasId;
  EdgeKind? pendingEdgeKind;
  String? pendingSourceId;
  bool validatorEnabled = true;
  bool darkMode = false;
  String language = 'en';
  String projectName = 'Untitled model';
  bool ready = false;

  DiagramNode? get selectedNode => _findNode(selectedNodeId);
  DiagramEdge? get selectedEdge {
    for (final edge in edges) {
      if (edge.id == selectedEdgeId) return edge;
    }
    return null;
  }
  bool get canUndo => _historyIndex > 0;
  bool get canRedo => _historyIndex >= 0 && _historyIndex < _history.length - 1;
  DiagramNode? get activeCanvas => _findNode(activeCanvasId);

  Future<void> initialize() async {
    final prefs = await SharedPreferences.getInstance();
    darkMode = prefs.getBool(_darkKey) ?? false;
    language = prefs.getString(_languageKey) ?? 'en';
    final saved = prefs.getString(_autosaveKey);
    if (saved != null) {
      try {
        _loadJson(saved, resetHistory: true);
      } catch (_) {
        _createStarterModel();
      }
    } else {
      _createStarterModel();
    }
    ready = true;
    notifyListeners();
  }

  void _createStarterModel() {
    nodes
      ..clear()
      ..addAll([
        DiagramNode(id: _id('node'), kind: NodeKind.actor, position: const Offset(480, 420), label: 'Customer', showSubcanvas: true),
        DiagramNode(id: _id('node'), kind: NodeKind.agent, position: const Offset(1000, 420), label: 'Service', showSubcanvas: true),
        DiagramNode(id: _id('node'), kind: NodeKind.hardGoal, position: const Offset(430, 650), label: 'Complete request'),
        DiagramNode(id: _id('node'), kind: NodeKind.plan, position: const Offset(970, 650), label: 'Process request'),
      ]);
    edges
      ..clear()
      ..add(DiagramEdge(id: _id('edge'), kind: EdgeKind.dependency, sourceId: nodes[2].id, targetId: nodes[3].id));
    projectName = 'Untitled model';
    _resetHistory();
  }

  void addNode(NodeKind kind, {Offset? position}) {
    final canvas = activeCanvas;
    if (canvas != null && kind.isEntity) {
      throw DiagramValidationException('validation.entityInsideEntity');
    }
    _recordBeforeChange();
    final spread = (nodes.length % 5) * 34.0;
    final canvasCenter = canvas == null ? null : canvas.position + canvas.subcanvasOffset;
    nodes.add(DiagramNode(
      id: _id('node'),
      kind: kind,
      position: position ??
          (canvasCenter == null
              ? Offset(680 + spread, 480 + spread)
              : canvasCenter + Offset((spread % 70) - 35, (spread % 50) - 25)),
      label: _defaultNodeLabel(kind),
      showSubcanvas: kind.isEntity,
      radius: canvas == null ? 52 : 30,
      parentId: canvas?.id,
    ));
    selectedNodeId = nodes.last.id;
    selectedEdgeId = null;
    _finishChange();
  }

  void selectNode(String? id) {
    selectedNodeId = id;
    selectedEdgeId = null;
    if (id != null && pendingEdgeKind != null) _handleConnectionTap(id);
    notifyListeners();
  }

  void enterCanvas(String id) {
    final node = _findNode(id);
    if (node == null || !node.kind.isEntity) return;
    _recordBeforeChange();
    node.showSubcanvas = true;
    activeCanvasId = id;
    selectedNodeId = id;
    selectedEdgeId = null;
    _finishChange();
  }

  void exitCanvas() {
    activeCanvasId = null;
    notifyListeners();
  }

  void selectEdge(String? id) {
    selectedEdgeId = id;
    selectedNodeId = null;
    notifyListeners();
  }

  void clearSelection() {
    selectedNodeId = null;
    selectedEdgeId = null;
    notifyListeners();
  }

  void startConnection(EdgeKind kind) {
    pendingEdgeKind = kind;
    pendingSourceId = null;
    selectedNodeId = null;
    selectedEdgeId = null;
    notifyListeners();
  }

  void cancelConnection() {
    pendingEdgeKind = null;
    pendingSourceId = null;
    notifyListeners();
  }

  void _handleConnectionTap(String id) {
    final tapped = _findNode(id);
    if (activeCanvasId != null && tapped?.parentId != activeCanvasId) {
      pendingSourceId = null;
      notifyListeners();
      throw DiagramValidationException('validation.canvasScope');
    }
    if (pendingSourceId == null) {
      pendingSourceId = id;
      return;
    }
    if (pendingSourceId == id) return;
    final source = _findNode(pendingSourceId)!;
    final target = _findNode(id)!;
    if (validatorEnabled && source.kind.isEntity && target.kind.isEntity) {
      pendingSourceId = null;
      notifyListeners();
      throw DiagramValidationException(
        'validation.entityLink',
        {'relationship': pendingEdgeKind!.key},
      );
    }
    _recordBeforeChange();
    edges.add(DiagramEdge(
      id: _id('edge'),
      kind: pendingEdgeKind!,
      sourceId: source.id,
      targetId: target.id,
    ));
    pendingEdgeKind = null;
    pendingSourceId = null;
    selectedNodeId = null;
    _finishChange();
  }

  void beginNodeMove() => _recordBeforeChange();

  void moveNode(String id, Offset delta, double scale) {
    final node = _findNode(id);
    if (node == null) return;
    final adjusted = delta / scale;
    node.position += adjusted;
    if (node.kind.isEntity) {
      for (final child in nodes.where((item) => item.parentId == node.id)) {
        child.position += adjusted;
      }
    }
    notifyListeners();
  }

  void endNodeMove(String id) {
    final node = _findNode(id);
    if (node != null) {
      node.parentId = null;
      for (final parent in nodes.where((item) => item.kind.isEntity && item.showSubcanvas && item.id != id)) {
        final center = parent.position + parent.subcanvasOffset;
        if ((center - node.position).distance < parent.subcanvasRadius) {
          if (!node.kind.isEntity) node.parentId = parent.id;
          break;
        }
      }
    }
    _finishChange();
  }

  void shiftDiagram(Offset delta) {
    if (delta == Offset.zero) return;
    for (final node in nodes) {
      node.position += delta;
    }
    notifyListeners();
  }

  void updateSelectedNode({
    String? label,
    double? radius,
    double? fontSize,
    int? fillColor,
    int? borderColor,
    int? textColor,
    bool? showSubcanvas,
    double? subcanvasRadius,
    Offset? subcanvasOffset,
  }) {
    final node = selectedNode;
    if (node == null) return;
    _recordBeforeChange();
    if (label != null && label.trim().isNotEmpty) node.label = label.trim();
    if (radius != null) node.radius = radius;
    if (fontSize != null) node.fontSize = fontSize;
    if (fillColor != null) node.fillColor = fillColor;
    if (borderColor != null) node.borderColor = borderColor;
    if (textColor != null) node.textColor = textColor;
    if (showSubcanvas != null) node.showSubcanvas = showSubcanvas;
    if (subcanvasRadius != null) node.subcanvasRadius = subcanvasRadius;
    if (subcanvasOffset != null) {
      final delta = subcanvasOffset - node.subcanvasOffset;
      node.subcanvasOffset = subcanvasOffset;
      for (final child in nodes.where((item) => item.parentId == node.id)) {
        child.position += delta;
      }
    }
    _finishChange();
  }

  void updateSelectedEdge({EdgeKind? kind, bool reverse = false}) {
    final edge = selectedEdge;
    if (edge == null) return;
    _recordBeforeChange();
    if (kind != null) edge.kind = kind;
    if (reverse) {
      final source = edge.sourceId;
      edge.sourceId = edge.targetId;
      edge.targetId = source;
    }
    _finishChange();
  }

  void beginCanvasTransform() => _recordBeforeChange();

  void moveActiveCanvas(Offset delta, double scale) {
    final canvas = activeCanvas;
    if (canvas == null) return;
    final adjusted = delta / scale;
    canvas.subcanvasOffset += adjusted;
    for (final child in nodes.where((item) => item.parentId == canvas.id)) {
      child.position += adjusted;
    }
    notifyListeners();
  }

  void resizeActiveCanvas(Offset delta, double scale) {
    final canvas = activeCanvas;
    if (canvas == null) return;
    canvas.subcanvasRadius =
        (canvas.subcanvasRadius + (delta.dx + delta.dy) / (2 * scale))
            .clamp(80, 320)
            .toDouble();
    notifyListeners();
  }

  void endCanvasTransform() => _finishChange();

  void deleteSelection() {
    if (selectedNodeId == null && selectedEdgeId == null) return;
    _recordBeforeChange();
    if (selectedNodeId != null) {
      final id = selectedNodeId!;
      nodes.removeWhere((node) => node.id == id);
      edges.removeWhere((edge) => edge.sourceId == id || edge.targetId == id);
      for (final node in nodes.where((node) => node.parentId == id)) {
        node.parentId = null;
      }
      if (activeCanvasId == id) activeCanvasId = null;
    } else {
      edges.removeWhere((edge) => edge.id == selectedEdgeId);
    }
    selectedNodeId = null;
    selectedEdgeId = null;
    _finishChange();
  }

  void newProject() {
    nodes.clear();
    edges.clear();
    selectedNodeId = null;
    selectedEdgeId = null;
    pendingEdgeKind = null;
    activeCanvasId = null;
    projectName = 'Untitled model';
    _resetHistory();
    notifyListeners();
    _scheduleAutosave();
  }

  void undo() {
    if (!canUndo) return;
    _historyIndex--;
    _loadJson(_history[_historyIndex]);
    notifyListeners();
    _scheduleAutosave();
  }

  void redo() {
    if (!canRedo) return;
    _historyIndex++;
    _loadJson(_history[_historyIndex]);
    notifyListeners();
    _scheduleAutosave();
  }

  Future<String?> importProject() async {
    try {
      final result = await FilePicker.platform.pickFiles(
        type: FileType.any,
        withData: true,
        withReadStream: true,
      );
      if (result == null) return null;
      final file = result.files.single;
      var bytes = file.bytes;
      if (bytes == null && file.readStream != null) {
        final builder = BytesBuilder(copy: false);
        await for (final chunk in file.readStream!) {
          builder.add(chunk);
        }
        bytes = builder.takeBytes();
      }
      if (bytes == null) return 'error.fileUnreadable';
      try {
        var source = utf8.decode(bytes);
        if (source.startsWith('\ufeff')) source = source.substring(1);
        _loadJson(source.trim(), resetHistory: true);
        projectName = file.name.replaceFirst(
          RegExp(r'\.(astr|json)$', caseSensitive: false),
          '',
        );
        notifyListeners();
        _scheduleAutosave();
        return null;
      } catch (error) {
        return 'error.invalidFile::$error';
      }
    } catch (error) {
      return 'error.importFailed::$error';
    }
  }

  Future<String?> exportProject({String? dialogTitle}) async {
    try {
      final data = Uint8List.fromList(utf8.encode(const JsonEncoder.withIndent('  ').convert(toAstrJson())));
      final result = await FilePicker.platform.saveFile(
        dialogTitle: dialogTitle ?? 'Export Asteroid project',
        fileName: '${_safeFileName(projectName)}.astr',
        type: FileType.custom,
        allowedExtensions: const ['astr'],
        bytes: data,
      );
      return result == null ? 'exportCancelled' : null;
    } catch (error) {
      return 'error.exportFailed::$error';
    }
  }

  Map<String, Object?> toAstrJson() {
    final idMap = <String, int>{for (var index = 0; index < nodes.length; index++) nodes[index].id: index};
    return {
      'version': '1.4',
      'metadata': {
        'created_by': 'Asteroid Mobile',
        'project_name': projectName,
        'node_count': nodes.length,
        'edge_count': edges.length,
      },
      'nodes': [for (var index = 0; index < nodes.length; index++) nodes[index].toAstr(index, idMap)],
      'edges': [for (final edge in edges) edge.toAstr(idMap)],
    };
  }

  void toggleValidator() {
    validatorEnabled = !validatorEnabled;
    notifyListeners();
  }

  Future<void> toggleTheme() async {
    darkMode = !darkMode;
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setBool(_darkKey, darkMode);
  }

  Future<void> toggleLanguage() async {
    language = language == 'en' ? 'es' : 'en';
    notifyListeners();
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString(_languageKey, language);
  }

  void _loadJson(String source, {bool resetHistory = false}) {
    final json = Map<String, dynamic>.from(jsonDecode(source) as Map);
    final rawNodes = json['nodes'];
    final rawEdges = json['edges'];
    if (rawNodes is! List || rawEdges is! List) {
      throw const FormatException('Missing nodes or edges list.');
    }
    final importedNodes = rawNodes
        .map((item) => DiagramNode.fromAstr(Map<String, dynamic>.from(item as Map)))
        .toList();
    final importedEdges = rawEdges.asMap().entries.map(
          (entry) => DiagramEdge.fromAstr(
            Map<String, dynamic>.from(entry.value as Map),
            entry.key,
          ),
        ).toList();
    final importedIds = importedNodes.map((node) => node.id).toSet();
    if (importedEdges.any(
      (edge) =>
          !importedIds.contains(edge.sourceId) ||
          !importedIds.contains(edge.targetId),
    )) {
      throw const FormatException('A relationship references a missing node.');
    }
    nodes
      ..clear()
      ..addAll(importedNodes);
    edges
      ..clear()
      ..addAll(importedEdges);
    final metadata = json['metadata'];
    if (metadata is Map && metadata['project_name'] is String) projectName = metadata['project_name'] as String;
    selectedNodeId = null;
    selectedEdgeId = null;
    pendingEdgeKind = null;
    pendingSourceId = null;
    activeCanvasId = null;
    if (resetHistory) _resetHistory();
  }

  void _recordBeforeChange() {
    final current = jsonEncode(toAstrJson());
    if (_history.isEmpty) {
      _history.add(current);
      _historyIndex = 0;
    }
    if (_historyIndex < _history.length - 1) _history.removeRange(_historyIndex + 1, _history.length);
  }

  void _finishChange() {
    final next = jsonEncode(toAstrJson());
    if (_history.isEmpty || _history.last != next) {
      _history.add(next);
      if (_history.length > 60) _history.removeAt(0);
      _historyIndex = _history.length - 1;
    }
    notifyListeners();
    _scheduleAutosave();
  }

  void _resetHistory() {
    _history
      ..clear()
      ..add(jsonEncode(toAstrJson()));
    _historyIndex = 0;
  }

  void _scheduleAutosave() {
    _autosaveTimer?.cancel();
    _autosaveTimer = Timer(const Duration(milliseconds: 350), () async {
      final prefs = await SharedPreferences.getInstance();
      await prefs.setString(_autosaveKey, jsonEncode(toAstrJson()));
    });
  }

  DiagramNode? _findNode(String? id) {
    if (id == null) return null;
    for (final node in nodes) {
      if (node.id == id) return node;
    }
    return null;
  }

  String _id(String prefix) => '${prefix}_${DateTime.now().microsecondsSinceEpoch}_${_serial++}';
  String _defaultNodeLabel(NodeKind kind) {
    if (language != 'es') return kind.label;
    return switch (kind) {
      NodeKind.actor => 'Actor',
      NodeKind.agent => 'Agente',
      NodeKind.hardGoal => 'Meta',
      NodeKind.softGoal => 'Meta flexible',
      NodeKind.plan => 'Plan',
      NodeKind.resource => 'Recurso',
    };
  }
  String _safeFileName(String value) => value.replaceAll(RegExp(r'[^a-zA-Z0-9_-]+'), '_').replaceAll(RegExp(r'^_+|_+$'), '').isEmpty
      ? 'asteroid_model'
      : value.replaceAll(RegExp(r'[^a-zA-Z0-9_-]+'), '_');

  @override
  void dispose() {
    _autosaveTimer?.cancel();
    super.dispose();
  }
}

class DiagramValidationException implements Exception {
  DiagramValidationException(this.key, [this.values = const {}]);
  final String key;
  final Map<String, Object?> values;
  @override
  String toString() => key;
}
