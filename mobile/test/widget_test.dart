import 'package:flutter_test/flutter_test.dart';

import 'package:asteroid_mobile/main.dart';

void main() {
  test('Asteroid app can be constructed', () {
    const app = AsteroidApp();

    expect(app, isA<AsteroidApp>());
  });
}
