import 'dart:io';
import 'dart:convert';
import 'package:flutter/foundation.dart' show kIsWeb;
import 'package:flutter/material.dart' hide SearchBar;
import 'package:image_picker/image_picker.dart';
import 'package:http/http.dart' as http;
import 'search_bar.dart';
import 'product_grid.dart';

class HomePage extends StatefulWidget {
  const HomePage({super.key});

  @override
  HomePageState createState() => HomePageState();
}

class HomePageState extends State<HomePage> {
  String searchTerm = '';
  File? _image;
  final List<Map<String, String>> chatMessages = [
    {
      'sender': 'bot',
      'message':
          'Hello! I can help you find products. What are you looking for?',
    },
  ];
  final TextEditingController chatController = TextEditingController();

  Future<void> _pickImage(ImageSource source) async {
    final picker = ImagePicker();
    final pickedFile = await picker.pickImage(source: source);
    if (pickedFile != null) {
      setState(() {
        _image = File(pickedFile.path);
      });
    }
  }

  void _showImageSourceDialog() {
    showDialog(
      context: context,
      builder:
          (context) => AlertDialog(
            title: const Text('Select Image Source'),
            content: Column(
              mainAxisSize: MainAxisSize.min,
              children: [
                ListTile(
                  leading: const Icon(Icons.camera_alt),
                  title: const Text('Camera'),
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(ImageSource.camera);
                  },
                ),
                ListTile(
                  leading: const Icon(Icons.photo_library),
                  title: const Text('Gallery'),
                  onTap: () {
                    Navigator.pop(context);
                    _pickImage(ImageSource.gallery);
                  },
                ),
              ],
            ),
          ),
    );
  }

  void onSearch(String term) {
    setState(() {
      searchTerm = term;
    });
  }

  void _sendChatMessage(String message) async {
    if (message.trim().isEmpty) return;

    setState(() {
      chatMessages.add({'sender': 'user', 'message': message});
      chatMessages.add({'sender': 'bot', 'message': 'Thinking...'});
    });
    chatController.clear();

    final String chatUrl =
        kIsWeb ? 'http://localhost:3001/chat' : 'http://10.0.2.2:3001/chat';

    try {
      final response = await http.post(
        Uri.parse(chatUrl),
        headers: {'Content-Type': 'application/json'},
        body: json.encode({'message': message}),
      );

      if (response.statusCode == 200) {
        final data = json.decode(response.body);
        final botMessage =
            data['response'] ?? 'Sorry, I couldn’t understand that.';
        final searchQuery = data['searchQuery'];

        setState(() {
          chatMessages.removeLast(); // Remove "Thinking..." message
          chatMessages.add({'sender': 'bot', 'message': botMessage});
          if (searchQuery != null) {
            searchTerm = searchQuery;
            onSearch(searchQuery);
          }
        });
      } else {
        setState(() {
          chatMessages.removeLast();
          chatMessages.add({
            'sender': 'bot',
            'message':
                'Error: Could not connect to the server. Status: ${response.statusCode}',
          });
        });
      }
    } catch (e) {
      setState(() {
        chatMessages.removeLast();
        chatMessages.add({'sender': 'bot', 'message': 'Error: $e'});
      });
    }
  }

  void _showChatBot() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) {
        return Padding(
          padding: EdgeInsets.only(
            bottom: MediaQuery.of(context).viewInsets.bottom,
          ),
          child: Container(
            height: MediaQuery.of(context).size.height * 0.5,
            padding: const EdgeInsets.all(16.0),
            child: Column(
              children: [
                const Text(
                  'Chat with Artifex Bot',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 10),
                Expanded(
                  child: ListView.builder(
                    itemCount: chatMessages.length,
                    itemBuilder: (context, index) {
                      final message = chatMessages[index];
                      final isUser = message['sender'] == 'user';
                      return Align(
                        alignment:
                            isUser
                                ? Alignment.centerRight
                                : Alignment.centerLeft,
                        child: Container(
                          margin: const EdgeInsets.symmetric(vertical: 5),
                          padding: const EdgeInsets.all(10),
                          decoration: BoxDecoration(
                            color: isUser ? Colors.cyan : Colors.grey[300],
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            message['message']!,
                            style: TextStyle(
                              color: isUser ? Colors.white : Colors.black,
                            ),
                          ),
                        ),
                      );
                    },
                  ),
                ),
                Row(
                  children: [
                    Expanded(
                      child: TextField(
                        controller: chatController,
                        decoration: const InputDecoration(
                          hintText: 'Type your requirements...',
                          border: OutlineInputBorder(),
                        ),
                      ),
                    ),
                    IconButton(
                      icon: const Icon(Icons.send),
                      onPressed: () {
                        _sendChatMessage(chatController.text);
                      },
                    ),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Artifex'),
        backgroundColor: Colors.black.withValues(alpha: 0.9),
        elevation: 4,
        shadowColor: Colors.cyan.withValues(alpha: 0.5),
      ),
      body: Container(
        decoration: const BoxDecoration(
          gradient: LinearGradient(
            colors: [Color(0xFF4881BA), Colors.black],
            begin: Alignment.topLeft,
            end: Alignment.bottomRight,
          ),
        ),
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(20.0),
              child: Column(
                children: [
                  if (!kIsWeb) // Hide image picker on web
                    ElevatedButton(
                      onPressed: _showImageSourceDialog,
                      child: const Text('Pick Room Image'),
                    ),
                  if (_image != null) // Display the selected image
                    Padding(
                      padding: const EdgeInsets.symmetric(vertical: 10),
                      child: Image.file(
                        _image!,
                        height: 100,
                        width: 100,
                        fit: BoxFit.cover,
                      ),
                    ),
                  const SizedBox(height: 10),
                  SearchBar(onSearch: onSearch),
                ],
              ),
            ),
            Expanded(child: ProductGrid(searchTerm: searchTerm, image: _image)),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: _showChatBot,
        backgroundColor: Colors.cyan,
        child: const Icon(Icons.chat),
      ),
    );
  }
}
