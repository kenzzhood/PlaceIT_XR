import 'package:flutter/material.dart';
import 'home_page.dart'; // Make sure this matches the file name

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Artifex',
      theme: ThemeData(
        primarySwatch: Colors.cyan,
        fontFamily: 'Poppins',
        scaffoldBackgroundColor: Colors.black,
        textTheme: const TextTheme(bodyMedium: TextStyle(color: Colors.cyan)),
      ),
      home: const HomePage(),
    );
  }
}
