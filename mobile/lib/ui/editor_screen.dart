import 'dart:math' as math;
import 'dart:ui' as ui;

import 'package:file_picker/file_picker.dart';
import 'package:flutter/material.dart';
import 'package:flutter/rendering.dart';

import '../editor/diagram_store.dart';
import '../models/diagram.dart';
import 'diagram_painters.dart';
import 'strings.dart';

class EditorScreen extends StatefulWidget {
  const EditorScreen({super.key, required this.store});
  final DiagramStore store;

  @override
  State<EditorScreen> createState() => _EditorScreenState();
}

class _EditorScreenState extends State<EditorScreen> {
  Size _workspaceSize = const Size(1800, 1400);
  final TransformationController _transform = TransformationController();
  final GlobalKey _diagramKey = GlobalKey();
  bool _exportingDiagram = false;

  DiagramStore get store => widget.store;

  @override
  void initState() {
    super.initState();
    store.addListener(_refresh);
    WidgetsBinding.instance.addPostFrameCallback((_) => _fitDiagramToView());
  }

  @override
  void dispose() {
    store.removeListener(_refresh);
    _transform.dispose();
    super.dispose();
  }

  void _refresh() {
    if (mounted) setState(() {});
  }

  void _fitDiagramToView() {
    if (!mounted) return;
    final viewport = MediaQuery.sizeOf(context);
    final bounds = _diagramBounds();
    final availableWidth = math.max(240.0, viewport.width - 32);
    final availableHeight = math.max(240.0, viewport.height - 150);
    final scale = math.min(
      availableWidth / bounds.width,
      availableHeight / bounds.height,
    ).clamp(.3, 1.6).toDouble();
    _transform.value = Matrix4.identity()
      ..translate(
        viewport.width / 2 - bounds.center.dx * scale,
        availableHeight / 2 - bounds.center.dy * scale,
      )
      ..scale(scale);
  }

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    return Scaffold(
      appBar: AppBar(
        titleSpacing: 12,
        title: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('ASTEROID', style: TextStyle(fontSize: 17, fontWeight: FontWeight.w800, letterSpacing: 0)),
            Text(store.projectName == 'Untitled model' ? tr(store.language, 'defaultProject') : store.projectName, style: TextStyle(fontSize: 11, color: colors.onSurfaceVariant), overflow: TextOverflow.ellipsis),
          ],
        ),
        leading: Padding(
          padding: const EdgeInsets.all(3),
          child: ClipRRect(
            borderRadius: BorderRadius.circular(7),
            child: Image.asset('assets/AsteroidLogo_favicons/android-chrome-192x192.png'),
          ),
        ),
        actions: [
          IconButton(tooltip: tr(store.language, 'undo'), onPressed: store.canUndo ? _undo : null, icon: const Icon(Icons.undo_rounded)),
          IconButton(tooltip: tr(store.language, 'redo'), onPressed: store.canRedo ? _redo : null, icon: const Icon(Icons.redo_rounded)),
          IconButton(tooltip: tr(store.language, 'resetView'), onPressed: _fitDiagramToView, icon: const Icon(Icons.fit_screen_rounded)),
        ],
      ),
      body: Stack(
        children: [
          Positioned.fill(
            child: ColoredBox(
              color: store.darkMode ? const Color(0xff111722) : const Color(0xffeef1f4),
              child: InteractiveViewer(
                transformationController: _transform,
                constrained: false,
                minScale: .3,
                maxScale: 2.4,
                boundaryMargin: const EdgeInsets.all(700),
                panEnabled: true,
                scaleEnabled: true,
                child: _workspace(),
              ),
            ),
          ),
          if (store.pendingEdgeKind != null) _connectionBanner(),
          if (store.activeCanvas != null && store.pendingEdgeKind == null) _activeCanvasBanner(),
          Positioned(
            left: 12,
            bottom: 18,
            child: _ModeChip(
              icon: store.validatorEnabled ? Icons.verified_outlined : Icons.rule_rounded,
              label: tr(store.language, store.validatorEnabled ? 'validatorOn' : 'validatorOff'),
              active: store.validatorEnabled,
              onTap: store.toggleValidator,
            ),
          ),
          if (store.selectedNode != null || store.selectedEdge != null)
            Positioned(
              right: 14,
              bottom: 18,
              child: Row(
                mainAxisSize: MainAxisSize.min,
                children: [
                  FloatingActionButton.small(
                    heroTag: 'properties',
                    tooltip: tr(store.language, 'properties'),
                    backgroundColor: colors.primaryContainer,
                    foregroundColor: colors.onPrimaryContainer,
                    onPressed: _showProperties,
                    child: const Icon(Icons.tune_rounded),
                  ),
                  const SizedBox(width: 10),
                  FloatingActionButton.small(
                    heroTag: 'delete',
                    tooltip: tr(store.language, 'delete'),
                    backgroundColor: colors.errorContainer,
                    foregroundColor: colors.onErrorContainer,
                    onPressed: _deleteSelection,
                    child: const Icon(Icons.delete_outline_rounded),
                  ),
                ],
              ),
            ),
        ],
      ),
      bottomNavigationBar: SafeArea(
        top: false,
        child: Container(
          height: 66,
          decoration: BoxDecoration(color: colors.surface, border: Border(top: BorderSide(color: colors.outlineVariant))),
          child: Row(
            mainAxisAlignment: MainAxisAlignment.spaceEvenly,
            children: [
              _BottomCommand(icon: Icons.add_circle_outline_rounded, label: tr(store.language, 'addElement'), onTap: _showElements),
              _BottomCommand(icon: Icons.arrow_outward_rounded, label: tr(store.language, 'connect'), onTap: _showRelationships),
              _BottomCommand(icon: Icons.menu_rounded, label: tr(store.language, 'options'), onTap: _showOptions),
            ],
          ),
        ),
      ),
    );
  }

  Widget _workspace() {
    final visibleNodes = store.nodes.where((node) {
      if (node.parentId == null) return true;
      final parent = store.nodes.where((item) => item.id == node.parentId).firstOrNull;
      return parent?.showSubcanvas ?? true;
    }).toList();
    final visibleIds = visibleNodes.map((node) => node.id).toSet();
    final visibleEdges = store.edges.where((edge) => visibleIds.contains(edge.sourceId) && visibleIds.contains(edge.targetId)).toList();
    return RepaintBoundary(
      key: _diagramKey,
      child: ColoredBox(
        color: _exportingDiagram ? Colors.white : (store.darkMode ? const Color(0xff111722) : Colors.white),
        child: GestureDetector(
          behavior: HitTestBehavior.opaque,
          onTapUp: (details) => _selectAt(details.localPosition),
          child: SizedBox.fromSize(
        size: _workspaceSize,
        child: Stack(
          clipBehavior: Clip.none,
          children: [
            if (!_exportingDiagram) Positioned.fill(child: CustomPaint(painter: GridPainter(store.darkMode))),
            Positioned.fill(
              child: CustomPaint(
                painter: EdgeLayerPainter(nodes: visibleNodes, edges: visibleEdges, selectedEdgeId: store.selectedEdgeId, dark: _exportingDiagram ? false : store.darkMode),
              ),
            ),
            for (final node in visibleNodes) _nodeWidget(node),
            if (store.activeCanvas != null) ..._canvasTransformHandles(store.activeCanvas!),
          ],
        ),
          ),
        ),
      ),
    );
  }

  Widget _nodeWidget(DiagramNode node) {
    final extent = node.radius * 2.2;
    return Positioned(
      left: node.position.dx - extent / 2,
      top: node.position.dy - extent / 2,
      width: extent,
      height: extent,
      child: Semantics(
        button: true,
        label: '${nodeKindLabel(store.language, _nodeTranslationKey(node.kind))}: ${node.label}',
        child: GestureDetector(
          behavior: HitTestBehavior.translucent,
          onTap: () => _tapNode(node.id),
          onPanStart: (_) {
            store.selectNode(node.id);
            store.beginNodeMove();
          },
          onPanUpdate: (details) => _moveNode(node, details),
          onPanEnd: (_) => _finishNodeMove(node.id),
          child: Stack(
            fit: StackFit.expand,
            children: [
              CustomPaint(
                painter: NodeShapePainter(
                  node: node,
                  selected: store.selectedNodeId == node.id,
                  connectionSource: store.pendingSourceId == node.id,
                  dark: store.darkMode,
                ),
              ),
              Padding(
                padding: EdgeInsets.all(node.radius * .35),
                child: Center(
                  child: Text(
                    node.label,
                    textAlign: TextAlign.center,
                    maxLines: 4,
                    overflow: TextOverflow.ellipsis,
                    style: TextStyle(color: Color(node.textColor), fontSize: node.fontSize, fontWeight: FontWeight.w700, letterSpacing: 0, height: 1.08),
                  ),
                ),
              ),
              Positioned(
                top: 4,
                right: 5,
                child: Icon(
                  _nodeIcon(node.kind),
                  size: 15,
                  color: (_exportingDiagram || !store.darkMode)
                      ? const Color(0xff172033)
                      : Colors.white.withValues(alpha: .88),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _moveNode(DiagramNode node, DragUpdateDetails details) {
    final scale = _transform.value.getMaxScaleOnAxis();
    store.moveNode(node.id, details.delta, scale);
    _expandWorkspaceFor(node, scale);
  }

  void _finishNodeMove(String id) {
    store.endNodeMove(id);
    _prepareWorkspaceForDocument();
  }

  void _finishCanvasTransform() {
    store.endCanvasTransform();
    _prepareWorkspaceForDocument();
  }

  void _deleteSelection() {
    store.deleteSelection();
    _prepareWorkspaceForDocument();
  }

  void _undo() {
    store.undo();
    _prepareWorkspaceForDocument();
  }

  void _redo() {
    store.redo();
    _prepareWorkspaceForDocument();
  }

  void _expandWorkspaceFor(DiagramNode node, double scale) {
    const section = 900.0;
    const margin = 120.0;
    var left = node.position.dx - node.radius * 1.3;
    var top = node.position.dy - node.radius * 1.3;
    var right = node.position.dx + node.radius * 1.3;
    var bottom = node.position.dy + node.radius * 1.3;
    if (node.kind.isEntity && node.showSubcanvas) {
      final center = node.position + node.subcanvasOffset;
      left = math.min(left, center.dx - node.subcanvasRadius);
      top = math.min(top, center.dy - node.subcanvasRadius);
      right = math.max(right, center.dx + node.subcanvasRadius);
      bottom = math.max(bottom, center.dy + node.subcanvasRadius);
    }

    var shiftX = 0.0;
    var shiftY = 0.0;
    var width = _workspaceSize.width;
    var height = _workspaceSize.height;
    if (left < margin) {
      shiftX = section;
      width += section;
    }
    if (top < margin) {
      shiftY = section;
      height += section;
    }
    while (right + shiftX > width - margin) {
      width += section;
    }
    while (bottom + shiftY > height - margin) {
      height += section;
    }
    if (shiftX != 0 || shiftY != 0) {
      store.shiftDiagram(Offset(shiftX, shiftY));
      final matrix = _transform.value.clone();
      matrix.setTranslationRaw(
        matrix.storage[12] - shiftX * scale,
        matrix.storage[13] - shiftY * scale,
        matrix.storage[14],
      );
      _transform.value = matrix;
    }
    if (width != _workspaceSize.width || height != _workspaceSize.height) {
      setState(() => _workspaceSize = Size(width, height));
    }
  }

  void _tapNode(String id) {
    try {
      final node = store.nodes.where((item) => item.id == id).firstOrNull;
      if (node != null && node.kind.isEntity && store.pendingEdgeKind == null) {
        store.enterCanvas(id);
      } else {
        store.selectNode(id);
      }
    } on DiagramValidationException catch (error) {
      final values = Map<String, Object?>.from(error.values);
      final relationship = values['relationship'];
      if (relationship is String) {
        values['relationship'] = edgeKindLabel(
          store.language,
          _edgeTranslationKey(EdgeKindInfo.parse(relationship)),
        );
      }
      _message(tr(store.language, error.key, values), error: true);
    }
  }

  List<Widget> _canvasTransformHandles(DiagramNode canvas) {
    final center = canvas.position + canvas.subcanvasOffset;
    final radius = canvas.subcanvasRadius;
    return [
      Positioned(
        left: center.dx - 21,
        top: center.dy - 21,
        width: 42,
        height: 42,
        child: GestureDetector(
          onPanStart: (_) => store.beginCanvasTransform(),
          onPanUpdate: (details) {
            final scale = _transform.value.getMaxScaleOnAxis();
            store.moveActiveCanvas(details.delta, scale);
            _expandWorkspaceFor(canvas, scale);
          },
          onPanEnd: (_) => _finishCanvasTransform(),
          child: Tooltip(
            message: tr(store.language, 'moveCanvas'),
            child: const DecoratedBox(
              decoration: BoxDecoration(color: Color(0xff18a999), shape: BoxShape.circle),
              child: Icon(Icons.open_with_rounded, color: Colors.white, size: 21),
            ),
          ),
        ),
      ),
      Positioned(
        left: center.dx + radius - 18,
        top: center.dy - 18,
        width: 36,
        height: 36,
        child: GestureDetector(
          onPanStart: (_) => store.beginCanvasTransform(),
          onPanUpdate: (details) {
            final scale = _transform.value.getMaxScaleOnAxis();
            store.resizeActiveCanvas(details.delta, scale);
            _expandWorkspaceFor(canvas, scale);
          },
          onPanEnd: (_) => _finishCanvasTransform(),
          child: Tooltip(
            message: tr(store.language, 'resizeCanvas'),
            child: const DecoratedBox(
              decoration: BoxDecoration(color: Color(0xfff2b134), shape: BoxShape.circle),
              child: Icon(Icons.unfold_more_rounded, color: Color(0xff172033), size: 20),
            ),
          ),
        ),
      ),
    ];
  }

  void _selectAt(Offset point) {
    final activeCanvas = store.activeCanvas;
    if (activeCanvas != null) {
      final center = activeCanvas.position + activeCanvas.subcanvasOffset;
      if ((point - center).distance > activeCanvas.subcanvasRadius) {
        store.exitCanvas();
        store.clearSelection();
        return;
      }
    }
    for (final edge in store.edges.reversed) {
      final source = store.nodes.where((node) => node.id == edge.sourceId).firstOrNull;
      final target = store.nodes.where((node) => node.id == edge.targetId).firstOrNull;
      if (source != null && target != null && _distanceToSegment(point, source.position, target.position) < 18) {
        store.selectEdge(edge.id);
        return;
      }
    }
    store.clearSelection();
  }

  double _distanceToSegment(Offset point, Offset a, Offset b) {
    final lengthSquared = (b - a).distanceSquared;
    if (lengthSquared == 0) return (point - a).distance;
    final t = (((point.dx - a.dx) * (b.dx - a.dx) + (point.dy - a.dy) * (b.dy - a.dy)) / lengthSquared).clamp(0.0, 1.0);
    return (point - Offset(a.dx + t * (b.dx - a.dx), a.dy + t * (b.dy - a.dy))).distance;
  }

  Widget _connectionBanner() {
    final hasSource = store.pendingSourceId != null;
    final colors = Theme.of(context).colorScheme;
    return Positioned(
      top: 12,
      left: 16,
      right: 16,
      child: SafeArea(
        child: Material(
          elevation: 4,
          color: colors.surfaceContainerHigh,
          surfaceTintColor: Colors.transparent,
          shape: RoundedRectangleBorder(
            borderRadius: BorderRadius.circular(8),
            side: BorderSide(color: colors.outlineVariant),
          ),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 9),
            child: Row(
              children: [
                Icon(
                  Icons.arrow_outward_rounded,
                  size: 19,
                  color: colors.primary,
                ),
                const SizedBox(width: 10),
                Expanded(
                  child: Text(
                    '${edgeKindLabel(store.language, _edgeTranslationKey(store.pendingEdgeKind!))}: ${tr(store.language, hasSource ? 'selectDestination' : 'selectFirst')}',
                    style: TextStyle(
                      color: colors.onSurface,
                      fontWeight: FontWeight.w600,
                    ),
                  ),
                ),
                IconButton(
                  tooltip: tr(store.language, 'cancel'),
                  onPressed: store.cancelConnection,
                  color: colors.onSurfaceVariant,
                  icon: const Icon(Icons.close_rounded),
                  visualDensity: VisualDensity.compact,
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Widget _activeCanvasBanner() {
    final canvas = store.activeCanvas!;
    return Positioned(
      top: 12,
      left: 16,
      right: 16,
      child: SafeArea(
        child: Material(
          elevation: 3,
          color: Theme.of(context).colorScheme.secondaryContainer,
          borderRadius: BorderRadius.circular(8),
          child: Padding(
            padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 7),
            child: Row(
              children: [
                const Icon(Icons.adjust_rounded, size: 19),
                const SizedBox(width: 9),
                Expanded(child: Text(tr(store.language, 'activeCanvas', {'name': canvas.label}), style: const TextStyle(fontWeight: FontWeight.w700))),
                TextButton.icon(onPressed: store.exitCanvas, icon: const Icon(Icons.arrow_back_rounded, size: 18), label: Text(tr(store.language, 'exitCanvas'))),
              ],
            ),
          ),
        ),
      ),
    );
  }

  Future<void> _handleMenu(String action) async {
    switch (action) {
      case 'new':
        if (await _confirmNew()) {
          store.newProject();
          setState(() => _workspaceSize = const Size(1800, 1400));
          _message(tr(store.language, 'projectCleared'));
        }
        return;
      case 'open':
        final error = await store.importProject();
        if (error != null) {
          _message(_operationMessage(error), error: true);
        } else {
          _prepareWorkspaceForDocument();
          WidgetsBinding.instance.addPostFrameCallback((_) => _fitDiagramToView());
          _message(tr(store.language, 'projectImported'));
        }
        return;
      case 'export':
        final error = await store.exportProject(dialogTitle: tr(store.language, 'exportTitle'));
        if (error != null && error != 'exportCancelled') {
          _message(_operationMessage(error), error: true);
        } else if (error == null) {
          _message(tr(store.language, 'projectExported'));
        }
        return;
      case 'exportDiagram':
        await _exportDiagram();
        return;
      case 'validator':
        store.toggleValidator();
        return;
      case 'theme':
        await store.toggleTheme();
        return;
      case 'language':
        await store.toggleLanguage();
        return;
      case 'help':
        _showHelp();
        return;
      case 'about':
        _showAbout();
        return;
    }
  }

  Future<bool> _confirmNew() async => await showDialog<bool>(
        context: context,
        builder: (context) => AlertDialog(
          title: Text(tr(store.language, 'newProject')),
          content: Text(tr(store.language, 'newProjectWarning')),
          actions: [
            TextButton(onPressed: () => Navigator.pop(context, false), child: Text(tr(store.language, 'cancel'))),
            FilledButton(onPressed: () => Navigator.pop(context, true), child: Text(tr(store.language, 'newProject'))),
          ],
        ),
      ) ?? false;

  void _showElements() => showModalBottomSheet<void>(
        context: context,
        showDragHandle: true,
        builder: (context) => _PickerSheet<NodeKind>(
          title: tr(store.language, 'elements'),
          items: store.activeCanvas == null ? NodeKind.values : NodeKind.values.where((kind) => !kind.isEntity).toList(),
          label: (kind) => nodeKindLabel(store.language, _nodeTranslationKey(kind)),
          icon: _nodeIcon,
          onSelected: (kind) {
            Navigator.pop(context);
            try {
              store.addNode(kind);
            } on DiagramValidationException catch (error) {
              _message(tr(store.language, error.key, error.values), error: true);
            }
          },
        ),
      );

  void _showRelationships() => showModalBottomSheet<void>(
        context: context,
        showDragHandle: true,
        builder: (context) => _PickerSheet<EdgeKind>(
          title: tr(store.language, 'relationships'),
          items: EdgeKind.values,
          label: (kind) => edgeKindLabel(store.language, _edgeTranslationKey(kind)),
          icon: (_) => Icons.arrow_outward_rounded,
          onSelected: (kind) {
            Navigator.pop(context);
            store.startConnection(kind);
          },
        ),
      );

  void _showOptions() => showModalBottomSheet<void>(
        context: context,
        showDragHandle: true,
        builder: (sheetContext) {
          void choose(String action) {
            Navigator.pop(sheetContext);
            _handleMenu(action);
          }

          return SafeArea(
            child: ListView(
              shrinkWrap: true,
              padding: const EdgeInsets.fromLTRB(12, 0, 12, 18),
              children: [
                Padding(
                  padding: const EdgeInsets.fromLTRB(8, 0, 8, 8),
                  child: Text(tr(store.language, 'options'), style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
                ),
                ListTile(leading: const Icon(Icons.note_add_outlined), title: Text(tr(store.language, 'newProject')), onTap: () => choose('new')),
                ListTile(leading: const Icon(Icons.folder_open_rounded), title: Text(tr(store.language, 'openProject')), onTap: () => choose('open')),
                ListTile(leading: const Icon(Icons.save_alt_rounded), title: Text(tr(store.language, 'exportProject')), onTap: () => choose('export')),
                ListTile(leading: const Icon(Icons.image_outlined), title: Text(tr(store.language, 'exportDiagram')), onTap: () => choose('exportDiagram')),
                const Divider(),
                SwitchListTile(secondary: const Icon(Icons.rule_rounded), title: Text(tr(store.language, store.validatorEnabled ? 'validatorOn' : 'validatorOff')), value: store.validatorEnabled, onChanged: (_) { Navigator.pop(sheetContext); store.toggleValidator(); }),
                ListTile(leading: Icon(store.darkMode ? Icons.light_mode_outlined : Icons.dark_mode_outlined), title: Text(tr(store.language, store.darkMode ? 'lightMode' : 'darkMode')), onTap: () => choose('theme')),
                ListTile(leading: const Icon(Icons.translate_rounded), title: Text(tr(store.language, store.language == 'en' ? 'languageSpanish' : 'languageEnglish')), onTap: () => choose('language')),
                ListTile(leading: const Icon(Icons.help_outline_rounded), title: Text(tr(store.language, 'help')), onTap: () => choose('help')),
                ListTile(leading: const Icon(Icons.info_outline_rounded), title: Text(tr(store.language, 'about')), onTap: () => choose('about')),
              ],
            ),
          );
        },
      );

  Future<void> _exportDiagram() async {
    try {
      setState(() => _exportingDiagram = true);
      store.exitCanvas();
      store.clearSelection();
      await WidgetsBinding.instance.endOfFrame;
      final boundary = _diagramKey.currentContext?.findRenderObject() as RenderRepaintBoundary?;
      if (boundary == null) throw StateError('Diagram surface is not available.');
      final image = await boundary.toImage(pixelRatio: 1);
      final bounds = _diagramBounds();
      final recorder = ui.PictureRecorder();
      final canvas = Canvas(recorder);
      canvas.drawImageRect(
        image,
        bounds,
        Rect.fromLTWH(0, 0, bounds.width, bounds.height),
        Paint()..filterQuality = FilterQuality.high,
      );
      final picture = recorder.endRecording();
      final cropped = await picture.toImage(
        bounds.width.ceil(),
        bounds.height.ceil(),
      );
      picture.dispose();
      image.dispose();
      final byteData = await cropped.toByteData(format: ui.ImageByteFormat.png);
      cropped.dispose();
      if (byteData == null) throw StateError('The diagram image could not be encoded.');
      final result = await FilePicker.platform.saveFile(
        dialogTitle: tr(store.language, 'exportDiagramTitle'),
        fileName: '${store.projectName == 'Untitled model' ? 'diagram' : store.projectName.replaceAll(RegExp(r'[^a-zA-Z0-9_-]+'), '_')}.png',
        type: FileType.custom,
        allowedExtensions: const ['png'],
        bytes: byteData.buffer.asUint8List(
          byteData.offsetInBytes,
          byteData.lengthInBytes,
        ),
      );
      if (result != null) _message(tr(store.language, 'diagramExported'));
    } catch (error) {
      _message(tr(store.language, 'error.diagramExport', {'details': error}), error: true);
    } finally {
      if (mounted) setState(() => _exportingDiagram = false);
    }
  }

  Rect _diagramBounds() {
    if (store.nodes.isEmpty) {
      return const Rect.fromLTWH(600, 450, 600, 500);
    }
    Rect? result;
    for (final node in store.nodes) {
      final parent = node.parentId == null
          ? null
          : store.nodes.where((item) => item.id == node.parentId).firstOrNull;
      if (parent != null && !parent.showSubcanvas) continue;
      final nodeRect = Rect.fromCircle(
        center: node.position,
        radius: node.radius * 1.2,
      );
      result = result == null ? nodeRect : result.expandToInclude(nodeRect);
      if (node.kind.isEntity && node.showSubcanvas) {
        final canvasRect = Rect.fromCircle(
          center: node.position + node.subcanvasOffset,
          radius: node.subcanvasRadius,
        );
        result = result.expandToInclude(canvasRect);
      }
    }
    final inflated = (result ?? const Rect.fromLTWH(600, 450, 600, 500)).inflate(42);
    final left = inflated.left.clamp(0, _workspaceSize.width - 1).toDouble();
    final top = inflated.top.clamp(0, _workspaceSize.height - 1).toDouble();
    final right = inflated.right.clamp(left + 1, _workspaceSize.width).toDouble();
    final bottom = inflated.bottom.clamp(top + 1, _workspaceSize.height).toDouble();
    return Rect.fromLTRB(
      left,
      top,
      right,
      bottom,
    );
  }

  void _showProperties() async {
    final node = store.selectedNode;
    final edge = store.selectedEdge;
    if (node == null && edge == null) return;
    await showModalBottomSheet<void>(
      context: context,
      isScrollControlled: true,
      showDragHandle: true,
      builder: (context) => node != null
          ? _PropertiesSheet(store: store, node: node.copy())
          : _EdgePropertiesSheet(store: store, edge: edge!),
    );
    _prepareWorkspaceForDocument();
  }

  void _prepareWorkspaceForDocument() {
    if (store.nodes.isEmpty) {
      if (mounted) setState(() => _workspaceSize = const Size(1800, 1400));
      return;
    }
    const margin = 140.0;
    var minX = double.infinity;
    var minY = double.infinity;
    var maxX = double.negativeInfinity;
    var maxY = double.negativeInfinity;
    for (final node in store.nodes) {
      minX = math.min(minX, node.position.dx - node.radius * 1.3);
      minY = math.min(minY, node.position.dy - node.radius * 1.3);
      maxX = math.max(maxX, node.position.dx + node.radius * 1.3);
      maxY = math.max(maxY, node.position.dy + node.radius * 1.3);
      if (node.kind.isEntity && node.showSubcanvas) {
        final center = node.position + node.subcanvasOffset;
        minX = math.min(minX, center.dx - node.subcanvasRadius);
        minY = math.min(minY, center.dy - node.subcanvasRadius);
        maxX = math.max(maxX, center.dx + node.subcanvasRadius);
        maxY = math.max(maxY, center.dy + node.subcanvasRadius);
      }
    }
    final shift = Offset(
      margin - minX,
      margin - minY,
    );
    if (shift != Offset.zero) {
      store.shiftDiagram(shift);
      maxX += shift.dx;
      maxY += shift.dy;
      final scale = _transform.value.getMaxScaleOnAxis();
      final matrix = _transform.value.clone();
      matrix.setTranslationRaw(
        matrix.storage[12] - shift.dx * scale,
        matrix.storage[13] - shift.dy * scale,
        matrix.storage[14],
      );
      _transform.value = matrix;
    }
    final neededWidth = math.max(1800.0, maxX + margin);
    final neededHeight = math.max(1400.0, maxY + margin);
    var width = 1800.0;
    var height = 1400.0;
    while (width < neededWidth) {
      width += 900;
    }
    while (height < neededHeight) {
      height += 900;
    }
    if (mounted) setState(() => _workspaceSize = Size(width, height));
  }

  void _showHelp() => showModalBottomSheet<void>(
        context: context,
        isScrollControlled: true,
        showDragHandle: true,
        builder: (context) => _HelpSheet(language: store.language),
      );

  void _showAbout() => showModalBottomSheet<void>(
        context: context,
        showDragHandle: true,
        builder: (context) => _AboutSheet(language: store.language),
      );

  void _message(String message, {bool error = false}) {
    if (!mounted) return;
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text(message), backgroundColor: error ? Theme.of(context).colorScheme.error : null));
  }

  String _operationMessage(String value) {
    final separator = value.indexOf('::');
    if (separator < 0) return tr(store.language, value);
    return tr(
      store.language,
      value.substring(0, separator),
      {'details': value.substring(separator + 2)},
    );
  }
}

IconData _nodeIcon(NodeKind kind) => switch (kind) {
      NodeKind.actor => Icons.person_outline_rounded,
      NodeKind.agent => Icons.smart_toy_outlined,
      NodeKind.hardGoal => Icons.flag_outlined,
      NodeKind.softGoal => Icons.cloud_outlined,
      NodeKind.plan => Icons.route_outlined,
      NodeKind.resource => Icons.inventory_2_outlined,
    };

String _nodeTranslationKey(NodeKind kind) => switch (kind) {
      NodeKind.actor => 'actor',
      NodeKind.agent => 'agent',
      NodeKind.hardGoal => 'hardGoal',
      NodeKind.softGoal => 'softGoal',
      NodeKind.plan => 'plan',
      NodeKind.resource => 'resource',
    };

String _edgeTranslationKey(EdgeKind kind) => switch (kind) {
      EdgeKind.dependency => 'dependency',
      EdgeKind.why => 'why',
      EdgeKind.meansEnd => 'meansEnd',
      EdgeKind.orDecomposition => 'or',
      EdgeKind.andDecomposition => 'and',
      EdgeKind.contribution => 'contribution',
    };

class _BottomCommand extends StatelessWidget {
  const _BottomCommand({required this.icon, required this.label, required this.onTap});
  final IconData icon;
  final String label;
  final VoidCallback? onTap;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final foreground = Theme.of(context).brightness == Brightness.light
        ? const Color(0xff172033)
        : colors.onSurface;
    return InkWell(
        onTap: onTap,
        child: SizedBox(
          width: 106,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Icon(icon, size: 22, color: foreground),
              const SizedBox(height: 3),
              Text(label, maxLines: 1, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: foreground)),
            ],
          ),
        ),
      );
  }
}

class _ModeChip extends StatelessWidget {
  const _ModeChip({required this.icon, required this.label, required this.active, required this.onTap});
  final IconData icon;
  final String label;
  final bool active;
  final VoidCallback onTap;

  @override
  Widget build(BuildContext context) {
    final colors = Theme.of(context).colorScheme;
    final foreground = Theme.of(context).brightness == Brightness.light
        ? const Color(0xff172033)
        : colors.onSurface;
    return ActionChip(
      avatar: Icon(icon, size: 17, color: foreground),
      label: Text(label, style: TextStyle(color: foreground)),
      onPressed: onTap,
      backgroundColor: active ? colors.secondaryContainer : null,
    );
  }
}

class _PickerSheet<T> extends StatelessWidget {
  const _PickerSheet({required this.title, required this.items, required this.label, required this.icon, required this.onSelected});
  final String title;
  final List<T> items;
  final String Function(T) label;
  final IconData Function(T) icon;
  final ValueChanged<T> onSelected;

  @override
  Widget build(BuildContext context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(16, 0, 16, 20),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(title, style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 14),
              GridView.count(
                shrinkWrap: true,
                crossAxisCount: 3,
                physics: const NeverScrollableScrollPhysics(),
                childAspectRatio: 1.35,
                mainAxisSpacing: 8,
                crossAxisSpacing: 8,
                children: [
                  for (final item in items)
                    InkWell(
                      borderRadius: BorderRadius.circular(8),
                      onTap: () => onSelected(item),
                      child: DecoratedBox(
                        decoration: BoxDecoration(border: Border.all(color: Theme.of(context).colorScheme.outlineVariant), borderRadius: BorderRadius.circular(8)),
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Icon(icon(item), color: Theme.of(context).brightness == Brightness.light ? const Color(0xff172033) : Theme.of(context).colorScheme.onSurface),
                            const SizedBox(height: 6),
                            Text(label(item), textAlign: TextAlign.center, style: TextStyle(fontSize: 12, fontWeight: FontWeight.w700, color: Theme.of(context).colorScheme.onSurface)),
                          ],
                        ),
                      ),
                    ),
                ],
              ),
            ],
          ),
        ),
      );
}

class _PropertiesSheet extends StatefulWidget {
  const _PropertiesSheet({required this.store, required this.node});
  final DiagramStore store;
  final DiagramNode node;

  @override
  State<_PropertiesSheet> createState() => _PropertiesSheetState();
}

class _PropertiesSheetState extends State<_PropertiesSheet> {
  late final TextEditingController _label = TextEditingController(text: widget.node.label);
  late double _radius = widget.node.radius.clamp(20, 120).toDouble();
  late double _fontSize = widget.node.fontSize.clamp(8, 28).toDouble();
  late int _fill = widget.node.fillColor;
  late int _border = widget.node.borderColor;
  late int _text = widget.node.textColor;
  late bool _subcanvas = widget.node.showSubcanvas;
  late double _canvasRadius = widget.node.subcanvasRadius.clamp(80, 320).toDouble();
  late double _canvasX = widget.node.subcanvasOffset.dx.clamp(-220, 220).toDouble();
  late double _canvasY = widget.node.subcanvasOffset.dy.clamp(-220, 220).toDouble();
  static const _colors = [0xffffffff, 0xff172033, 0xff6496fa, 0xfffa9664, 0xff65a86a, 0xffd5be54, 0xff7599e8, 0xffa978d4, 0xffe46c76, 0xff18a999];

  @override
  void dispose() {
    _label.dispose();
    super.dispose();
  }

  void _saveProperties() {
    widget.store.updateSelectedNode(
      label: _label.text,
      radius: _radius,
      fontSize: _fontSize,
      fillColor: _fill,
      borderColor: _border,
      textColor: _text,
      showSubcanvas: widget.node.kind.isEntity ? _subcanvas : null,
      subcanvasRadius: widget.node.kind.isEntity ? _canvasRadius : null,
      subcanvasOffset:
          widget.node.kind.isEntity ? Offset(_canvasX, _canvasY) : null,
    );
  }

  @override
  Widget build(BuildContext context) {
    final store = widget.store;
    return SafeArea(
      child: Padding(
        padding: EdgeInsets.fromLTRB(20, 0, 20, MediaQuery.viewInsetsOf(context).bottom + 20),
        child: SingleChildScrollView(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(tr(store.language, 'properties'), style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 16),
              TextField(controller: _label, maxLines: 2, decoration: InputDecoration(labelText: tr(store.language, 'name'), border: const OutlineInputBorder())),
              const SizedBox(height: 16),
              Text('${tr(store.language, 'size')}: ${_radius.round()}'),
              Slider(value: _radius, min: 20, max: 120, divisions: 50, onChanged: (value) => setState(() => _radius = value)),
              Text('${tr(store.language, 'textSize')}: ${_fontSize.round()}'),
              Slider(value: _fontSize, min: 8, max: 28, divisions: 20, onChanged: (value) => setState(() => _fontSize = value)),
              Text(tr(store.language, 'colors'), style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w700)),
              const SizedBox(height: 8),
              _ColorRow(label: tr(store.language, 'fillColor'), colors: _colors, value: _fill, onChanged: (value) => setState(() => _fill = value)),
              _ColorRow(label: tr(store.language, 'borderColor'), colors: _colors, value: _border, onChanged: (value) => setState(() => _border = value)),
              _ColorRow(label: tr(store.language, 'textColor'), colors: _colors, value: _text, onChanged: (value) => setState(() => _text = value)),
              if (widget.node.kind.isEntity) ...[
                const SizedBox(height: 12),
                SwitchListTile(contentPadding: EdgeInsets.zero, title: Text(tr(store.language, 'subcanvas')), subtitle: Text(tr(store.language, 'subcanvasHint')), value: _subcanvas, onChanged: (value) => setState(() => _subcanvas = value)),
                Text('${tr(store.language, 'canvasRadius')}: ${_canvasRadius.round()}'),
                Slider(value: _canvasRadius, min: 80, max: 320, divisions: 48, onChanged: (value) => setState(() => _canvasRadius = value)),
                Text('${tr(store.language, 'canvasHorizontal')}: ${_canvasX.round()}'),
                Slider(value: _canvasX, min: -220, max: 220, divisions: 44, onChanged: (value) => setState(() => _canvasX = value)),
                Text('${tr(store.language, 'canvasVertical')}: ${_canvasY.round()}'),
                Slider(value: _canvasY, min: -220, max: 220, divisions: 44, onChanged: (value) => setState(() => _canvasY = value)),
                SizedBox(
                  width: double.infinity,
                  child: OutlinedButton.icon(
                    onPressed: () {
                      _saveProperties();
                      Navigator.pop(context);
                      store.enterCanvas(widget.node.id);
                    },
                    icon: const Icon(Icons.adjust_rounded),
                    label: Text(tr(store.language, 'enterCanvas')),
                  ),
                ),
              ],
              const SizedBox(height: 16),
              SizedBox(
                width: double.infinity,
                child: FilledButton.icon(
                  onPressed: () {
                    _saveProperties();
                    Navigator.pop(context);
                  },
                  icon: const Icon(Icons.check_rounded),
                  label: Text(tr(store.language, 'apply')),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _ColorRow extends StatelessWidget {
  const _ColorRow({required this.label, required this.colors, required this.value, required this.onChanged});
  final String label;
  final List<int> colors;
  final int value;
  final ValueChanged<int> onChanged;

  @override
  Widget build(BuildContext context) => Padding(
        padding: const EdgeInsets.only(bottom: 12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600)),
            const SizedBox(height: 7),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                for (final color in colors)
                  InkWell(
                    customBorder: const CircleBorder(),
                    onTap: () => onChanged(color),
                    child: Container(
                      width: 32,
                      height: 32,
                      decoration: BoxDecoration(
                        color: Color(color),
                        shape: BoxShape.circle,
                        border: Border.all(
                          color: value == color ? Theme.of(context).colorScheme.primary : Theme.of(context).colorScheme.outlineVariant,
                          width: value == color ? 3 : 1,
                        ),
                      ),
                      child: value == color ? Icon(Icons.check_rounded, size: 17, color: color == 0xffffffff ? Colors.black : Colors.white) : null,
                    ),
                  ),
              ],
            ),
          ],
        ),
      );
}

class _EdgePropertiesSheet extends StatefulWidget {
  const _EdgePropertiesSheet({required this.store, required this.edge});
  final DiagramStore store;
  final DiagramEdge edge;

  @override
  State<_EdgePropertiesSheet> createState() => _EdgePropertiesSheetState();
}

class _EdgePropertiesSheetState extends State<_EdgePropertiesSheet> {
  late EdgeKind _kind = widget.edge.kind;

  @override
  Widget build(BuildContext context) {
    final store = widget.store;
    final source = store.nodes.where((node) => node.id == widget.edge.sourceId).firstOrNull;
    final target = store.nodes.where((node) => node.id == widget.edge.targetId).firstOrNull;
    return SafeArea(
      child: Padding(
        padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
        child: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(tr(store.language, 'properties'), style: Theme.of(context).textTheme.titleLarge?.copyWith(fontWeight: FontWeight.w800)),
            const SizedBox(height: 16),
            DropdownButtonFormField<EdgeKind>(
              initialValue: _kind,
              decoration: InputDecoration(labelText: tr(store.language, 'type')),
              items: [for (final kind in EdgeKind.values) DropdownMenuItem(value: kind, child: Text(edgeKindLabel(store.language, _edgeTranslationKey(kind))))],
              onChanged: (value) {
                if (value != null) setState(() => _kind = value);
              },
            ),
            const SizedBox(height: 14),
            ListTile(contentPadding: EdgeInsets.zero, leading: const Icon(Icons.trip_origin_rounded), title: Text(tr(store.language, 'source')), subtitle: Text(source?.label ?? '-')),
            ListTile(contentPadding: EdgeInsets.zero, leading: const Icon(Icons.flag_outlined), title: Text(tr(store.language, 'destination')), subtitle: Text(target?.label ?? '-')),
            const SizedBox(height: 8),
            Row(
              children: [
                Expanded(child: OutlinedButton.icon(onPressed: () { store.updateSelectedEdge(reverse: true); Navigator.pop(context); }, icon: const Icon(Icons.swap_horiz_rounded), label: Text(tr(store.language, 'reverseDirection')))),
                const SizedBox(width: 10),
                Expanded(child: FilledButton.icon(onPressed: () { store.updateSelectedEdge(kind: _kind); Navigator.pop(context); }, icon: const Icon(Icons.check_rounded), label: Text(tr(store.language, 'apply')))),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _HelpSheet extends StatelessWidget {
  const _HelpSheet({required this.language});
  final String language;

  @override
  Widget build(BuildContext context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
          child: SingleChildScrollView(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(tr(language, 'docs.title'), style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
                const SizedBox(height: 16),
                for (final section in const [
                  ('docs.startTitle', 'docs.startBody', Icons.touch_app_outlined),
                  ('docs.linksTitle', 'docs.linksBody', Icons.arrow_outward_rounded),
                  ('docs.propertiesTitle', 'docs.propertiesBody', Icons.tune_rounded),
                  ('docs.subcanvasTitle', 'docs.subcanvasBody', Icons.adjust_rounded),
                  ('docs.validationTitle', 'docs.validationBody', Icons.verified_outlined),
                  ('docs.filesTitle', 'docs.filesBody', Icons.folder_outlined),
                  ('docs.historyTitle', 'docs.historyBody', Icons.history_rounded),
                ])
                  Padding(
                    padding: const EdgeInsets.only(bottom: 18),
                    child: Row(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Icon(section.$3, size: 22),
                        const SizedBox(width: 12),
                        Expanded(child: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text(tr(language, section.$1), style: const TextStyle(fontWeight: FontWeight.w800)), const SizedBox(height: 4), Text(tr(language, section.$2))])),
                      ],
                    ),
                  ),
              ],
            ),
          ),
        ),
      );
}

class _AboutSheet extends StatelessWidget {
  const _AboutSheet({required this.language});
  final String language;

  @override
  Widget build(BuildContext context) => SafeArea(
        child: Padding(
          padding: const EdgeInsets.fromLTRB(20, 0, 20, 24),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(tr(language, 'about.title'), style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 4),
              Text(tr(language, 'about.version'), style: Theme.of(context).textTheme.labelLarge),
              const SizedBox(height: 14),
              Text(tr(language, 'about.body')),
              const SizedBox(height: 18),
              Text(tr(language, 'about.credits'), style: Theme.of(context).textTheme.titleMedium?.copyWith(fontWeight: FontWeight.w800)),
              const SizedBox(height: 6),
              Text('${tr(language, 'about.createdBy')} - https://github.com/AndyCG03'),
              Text('${tr(language, 'about.originalIdea')} - https://github.com/DaryllLorenzo'),
            ],
          ),
        ),
      );
}

extension _FirstOrNull<T> on Iterable<T> {
  T? get firstOrNull => isEmpty ? null : first;
}
