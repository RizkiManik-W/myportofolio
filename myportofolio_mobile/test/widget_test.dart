import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:myportofolio_mobile/main.dart';
import 'package:myportofolio_mobile/menu.dart';

void main() {
  testWidgets('Home shows profile information and the three menu cards', (
    tester,
  ) async {
    await tester.pumpWidget(const MyApp());

    expect(find.text('MyPortfolio'), findsOneWidget);
    expect(find.text('2406000001'), findsOneWidget);
    expect(find.text('Burhan'), findsOneWidget);
    expect(find.text('PBP A'), findsOneWidget);
    expect(find.byType(InfoCard), findsNWidgets(3));
    expect(find.byType(ItemCard), findsNWidgets(3));
    expect(find.text('Selamat datang di MyPortfolio Mobile!'), findsOneWidget);
  });

  for (final label in ['Lihat Proyek', 'Tambah Proyek', 'Logout']) {
    testWidgets('$label shows its own SnackBar message', (tester) async {
      await tester.pumpWidget(const MyApp());
      await tester.tap(find.text(label));
      await tester.pumpAndSettle();

      expect(find.text('Kamu telah menekan tombol $label!'), findsOneWidget);
    });
  }

  for (final size in [const Size(320, 568), const Size(568, 320)]) {
    testWidgets('Home fits a ${size.width} x ${size.height} screen', (
      tester,
    ) async {
      tester.view.devicePixelRatio = 1;
      tester.view.physicalSize = size;
      addTearDown(tester.view.resetDevicePixelRatio);
      addTearDown(tester.view.resetPhysicalSize);
      await tester.pumpWidget(const MyApp());
      await tester.ensureVisible(find.text('Logout'));
      await tester.tap(find.text('Logout'));
      await tester.pumpAndSettle();

      expect(tester.takeException(), isNull);
      expect(find.text('Kamu telah menekan tombol Logout!'), findsOneWidget);
    });
  }
}
