import 'package:flutter/material.dart';

import 'editor/diagram_store.dart';
import 'ui/editor_screen.dart';

void main() {
  WidgetsFlutterBinding.ensureInitialized();
  runApp(const AsteroidApp());
}

class AsteroidApp extends StatefulWidget {
  const AsteroidApp({super.key});

  @override
  State<AsteroidApp> createState() => _AsteroidAppState();
}

class _AsteroidAppState extends State<AsteroidApp> {
  final DiagramStore _store = DiagramStore();

  @override
  void initState() {
    super.initState();
    _store.addListener(_refresh);
    _store.initialize();
  }

  @override
  void dispose() {
    _store.removeListener(_refresh);
    _store.dispose();
    super.dispose();
  }

  void _refresh() {
    if (mounted) setState(() {});
  }

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Asteroid',
      debugShowCheckedModeBanner: false,
      themeMode: _store.darkMode ? ThemeMode.dark : ThemeMode.light,
      theme: _theme(Brightness.light),
      darkTheme: _theme(Brightness.dark),
      home: _store.ready
          ? EditorScreen(store: _store)
          : const Scaffold(body: Center(child: CircularProgressIndicator())),
    );
  }

  ThemeData _theme(Brightness brightness) {
    final dark = brightness == Brightness.dark;
    final scheme = ColorScheme.fromSeed(
      seedColor: const Color(0xff18a999),
      brightness: brightness,
      surface: dark ? const Color(0xff19212e) : const Color(0xfffbfcfd),
    );
    return ThemeData(
      useMaterial3: true,
      colorScheme: scheme,
      scaffoldBackgroundColor: dark ? const Color(0xff111722) : const Color(0xffeef1f4),
      appBarTheme: AppBarTheme(
        elevation: 0,
        scrolledUnderElevation: 1,
        backgroundColor: scheme.surface,
        foregroundColor: scheme.onSurface,
      ),
      bottomSheetTheme: BottomSheetThemeData(
        backgroundColor: scheme.surface,
        showDragHandle: true,
        shape: const RoundedRectangleBorder(borderRadius: BorderRadius.vertical(top: Radius.circular(8))),
      ),
      inputDecorationTheme: const InputDecorationTheme(border: OutlineInputBorder()),
      cardTheme: const CardThemeData(shape: RoundedRectangleBorder(borderRadius: BorderRadius.all(Radius.circular(8)))),
    );
  }
}

