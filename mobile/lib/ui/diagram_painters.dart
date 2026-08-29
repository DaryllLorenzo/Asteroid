import 'dart:math' as math;

import 'package:flutter/material.dart';

import '../models/diagram.dart';

class EdgeLayerPainter extends CustomPainter {
  EdgeLayerPainter({required this.nodes, required this.edges, required this.selectedEdgeId, required this.dark});

  final List<DiagramNode> nodes;
  final List<DiagramEdge> edges;
  final String? selectedEdgeId;
  final bool dark;

  @override
  void paint(Canvas canvas, Size size) {
    final nodeMap = {for (final node in nodes) node.id: node};
    for (final node in nodes.where((node) => node.kind.isEntity && node.showSubcanvas)) {
      final center = node.position + node.subcanvasOffset;
      canvas.drawCircle(
        center,
        node.subcanvasRadius,
        Paint()..color = (dark ? Colors.white : const Color(0xff2b3a4f)).withValues(alpha: .08),
      );
      canvas.drawCircle(
        center,
        node.subcanvasRadius,
        Paint()
          ..color = (dark ? Colors.white : const Color(0xff455468)).withValues(alpha: .30)
          ..style = PaintingStyle.stroke
          ..strokeWidth = 1.5,
      );
    }
    for (final edge in edges) {
      final source = nodeMap[edge.sourceId];
      final target = nodeMap[edge.targetId];
      if (source == null || target == null) continue;
      final vector = target.position - source.position;
      if (vector.distance < 1) continue;
      final direction = vector / vector.distance;
      final start = source.position + direction * _nodeExtent(source);
      final end = target.position - direction * _nodeExtent(target);
      final selected = edge.id == selectedEdgeId;
      final color = selected ? const Color(0xff18a999) : (dark ? const Color(0xffa9b4c7) : const Color(0xff455468));
      final paint = Paint()
        ..color = color
        ..strokeWidth = selected ? 3.5 : 2.1
        ..style = PaintingStyle.stroke
        ..strokeCap = StrokeCap.round;

      if (edge.kind == EdgeKind.dependency || edge.kind == EdgeKind.contribution) {
        _drawDashed(canvas, start, end, paint);
      } else {
        canvas.drawLine(start, end, paint);
      }
      _drawArrowHead(canvas, start, end, paint);
      _drawEdgeBadge(canvas, edge, Offset.lerp(start, end, .5)!, color);
    }
  }

  double _nodeExtent(DiagramNode node) => node.kind.isEntity ? node.radius : node.radius * .88;

  void _drawDashed(Canvas canvas, Offset start, Offset end, Paint paint) {
    final distance = (end - start).distance;
    final direction = (end - start) / distance;
    for (double value = 0; value < distance; value += 13) {
      canvas.drawLine(start + direction * value, start + direction * math.min(value + 7, distance), paint);
    }
  }

  void _drawArrowHead(Canvas canvas, Offset start, Offset end, Paint paint) {
    final angle = math.atan2(end.dy - start.dy, end.dx - start.dx);
    const length = 12.0;
    final a = end - Offset(math.cos(angle - .52), math.sin(angle - .52)) * length;
    final b = end - Offset(math.cos(angle + .52), math.sin(angle + .52)) * length;
    canvas.drawPath(Path()..moveTo(a.dx, a.dy)..lineTo(end.dx, end.dy)..lineTo(b.dx, b.dy), paint);
  }

  void _drawEdgeBadge(Canvas canvas, DiagramEdge edge, Offset center, Color color) {
    final label = switch (edge.kind) {
      EdgeKind.why => 'WHY',
      EdgeKind.meansEnd => 'ME',
      EdgeKind.orDecomposition => 'OR',
      EdgeKind.andDecomposition => 'AND',
      EdgeKind.contribution => '+',
      EdgeKind.dependency => 'D',
    };
    final background = Paint()..color = dark ? const Color(0xff202938) : Colors.white;
    canvas.drawCircle(center, 12, background);
    canvas.drawCircle(
      center,
      12,
      Paint()
        ..color = color
        ..style = PaintingStyle.stroke
        ..strokeWidth = 1.5,
    );
    final text = TextPainter(
      text: TextSpan(text: label, style: TextStyle(color: color, fontSize: label.length > 2 ? 7 : 9, fontWeight: FontWeight.w800)),
      textDirection: TextDirection.ltr,
    )..layout();
    text.paint(canvas, center - Offset(text.width / 2, text.height / 2));
  }

  @override
  bool shouldRepaint(covariant EdgeLayerPainter oldDelegate) => true;
}

class NodeShapePainter extends CustomPainter {
  NodeShapePainter({required this.node, required this.selected, required this.connectionSource, required this.dark});

  final DiagramNode node;
  final bool selected;
  final bool connectionSource;
  final bool dark;

  @override
  void paint(Canvas canvas, Size size) {
    final center = size.center(Offset.zero);
    final fill = Paint()..color = Color(node.fillColor);
    final border = Paint()
      ..color = connectionSource ? const Color(0xfff2b134) : (selected ? const Color(0xff18a999) : Color(node.borderColor))
      ..style = PaintingStyle.stroke
      ..strokeWidth = selected || connectionSource ? 4 : 2;
    final shape = _pathFor(node.kind, size);

    canvas.drawShadow(shape, Colors.black.withValues(alpha: .25), selected ? 8 : 4, true);
    canvas.drawPath(shape, fill);
    canvas.drawPath(shape, border);
  }

  Path _pathFor(NodeKind kind, Size size) {
    final center = size.center(Offset.zero);
    final r = node.radius;
    switch (kind) {
      case NodeKind.actor:
      case NodeKind.agent:
        return Path()..addOval(Rect.fromCircle(center: center, radius: r));
      case NodeKind.hardGoal:
        return Path()..addRRect(RRect.fromRectAndRadius(Rect.fromCenter(center: center, width: r * 1.85, height: r * 1.25), const Radius.circular(18)));
      case NodeKind.resource:
        return Path()..addRRect(RRect.fromRectAndRadius(Rect.fromCenter(center: center, width: r * 1.65, height: r * 1.35), const Radius.circular(3)));
      case NodeKind.plan:
        return Path()
          ..moveTo(center.dx - r, center.dy)
          ..quadraticBezierTo(center.dx, center.dy - r * .72, center.dx + r, center.dy)
          ..quadraticBezierTo(center.dx, center.dy + r * .72, center.dx - r, center.dy)
          ..close();
      case NodeKind.softGoal:
        final path = Path();
        const points = 18;
        for (var i = 0; i <= points; i++) {
          final angle = i * math.pi * 2 / points;
          final wave = i.isEven ? 1.0 : .82;
          final point = center + Offset(math.cos(angle) * r * wave, math.sin(angle) * r * .72 * wave);
          if (i == 0) path.moveTo(point.dx, point.dy); else path.lineTo(point.dx, point.dy);
        }
        return path..close();
    }
  }

  @override
  bool shouldRepaint(covariant NodeShapePainter oldDelegate) => true;
}

class GridPainter extends CustomPainter {
  GridPainter(this.dark);
  final bool dark;

  @override
  void paint(Canvas canvas, Size size) {
    final paint = Paint()..color = dark ? const Color(0xff273244) : const Color(0xffdce2e8);
    for (double x = 0; x < size.width; x += 32) canvas.drawCircle(Offset(x, 0), 1, paint);
    for (double y = 0; y < size.height; y += 32) {
      for (double x = 0; x < size.width; x += 32) canvas.drawCircle(Offset(x, y), 1, paint);
    }
  }

  @override
  bool shouldRepaint(covariant GridPainter oldDelegate) => oldDelegate.dark != dark;
}
