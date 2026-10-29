import 'package:flutter_test/flutter_test.dart';
import 'package:mobile/main.dart';

void main() {
  testWidgets('ConvertApp smoke test', (WidgetTester tester) async {
    await tester.pumpWidget(const ConvertApp(initialDarkMode: true));
    expect(find.text('Convert'), findsWidgets);
  });
}
