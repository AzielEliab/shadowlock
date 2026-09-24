import 'package:flutter/material.dart';

/// Paper / charcoal surfaces. Gold focus. Follows the system light or dark setting.
const Color kGold = Color(0xFFC9A227);
const Color kGoldInk = Color(0xFF6B5310);

ThemeData buildAppTheme(Brightness brightness) {
  final dark = brightness == Brightness.dark;
  final scheme = ColorScheme(
    brightness: brightness,
    primary: kGold,
    onPrimary: dark ? const Color(0xFF12110E) : const Color(0xFF1C1914),
    secondary: dark ? const Color(0xFFE1C56A) : kGoldInk,
    onSecondary: dark ? const Color(0xFF12110E) : const Color(0xFFFFFDF8),
    error: dark ? const Color(0xFFF0A8A2) : const Color(0xFF8F2D2D),
    onError: dark ? const Color(0xFF12110E) : const Color(0xFFFFFDF8),
    surface: dark ? const Color(0xFF1C1B17) : const Color(0xFFFFFDF8),
    onSurface: dark ? const Color(0xFFF4EFE4) : const Color(0xFF1C1914),
  );
  final fill = dark ? const Color(0xFF14130F) : const Color(0xFFF7F4EC);
  return ThemeData(
    useMaterial3: true,
    brightness: brightness,
    colorScheme: scheme,
    scaffoldBackgroundColor: dark ? const Color(0xFF12110E) : const Color(0xFFF7F4EC),
    focusColor: kGold,
    appBarTheme: AppBarTheme(
      backgroundColor: dark ? const Color(0xFF12110E) : const Color(0xFFF7F4EC),
      foregroundColor: scheme.onSurface,
      elevation: 0,
      centerTitle: false,
    ),
    cardTheme: CardThemeData(
      color: scheme.surface,
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(12),
        side: BorderSide(color: scheme.outlineVariant),
      ),
    ),
    inputDecorationTheme: InputDecorationTheme(
      filled: true,
      fillColor: fill,
      border: OutlineInputBorder(borderRadius: BorderRadius.circular(10)),
      focusedBorder: OutlineInputBorder(
        borderRadius: BorderRadius.circular(10),
        borderSide: const BorderSide(color: kGold, width: 2),
      ),
    ),
    filledButtonTheme: FilledButtonThemeData(
      style: FilledButton.styleFrom(
        backgroundColor: scheme.onSurface,
        foregroundColor: scheme.surface,
        minimumSize: const Size.fromHeight(48),
      ),
    ),
  );
}
