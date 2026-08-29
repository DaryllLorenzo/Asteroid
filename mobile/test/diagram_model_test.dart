import 'package:asteroid_mobile/models/diagram.dart';
import 'package:flutter_test/flutter_test.dart';

void main() {
  test('node round trips through desktop astr shape', () {
    final node = DiagramNode(
      id: 'customer',
      kind: NodeKind.actor,
      position: const Offset(120, 240),
      label: 'Customer',
      showSubcanvas: true,
    );

    final json = node.toAstr(0, const {'customer': 0});
    final restored = DiagramNode.fromAstr(Map<String, dynamic>.from(json));

    expect(restored.kind, NodeKind.actor);
    expect(restored.label, 'Customer');
    expect(restored.position, const Offset(120, 240));
    expect(restored.showSubcanvas, isTrue);
  });

  test('relationship keys match Asteroid desktop format', () {
    expect(EdgeKind.dependency.key, 'dependency_link');
    expect(EdgeKind.why.key, 'why_link');
    expect(EdgeKindInfo.parse('dependency_link'), EdgeKind.dependency);
    expect(EdgeKindInfo.parse('why_link'), EdgeKind.why);
  });
}

