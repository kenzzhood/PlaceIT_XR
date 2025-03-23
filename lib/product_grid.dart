import 'dart:convert';
import 'dart:io';
import 'package:flutter/material.dart';
import 'package:http/http.dart' as http;
import 'package:cached_network_image/cached_network_image.dart';
import 'package:url_launcher/url_launcher.dart';
import 'product_detail_page.dart'; // Add this import

class ProductGrid extends StatefulWidget {
  final String searchTerm;
  final File? image;

  const ProductGrid({super.key, required this.searchTerm, this.image});

  @override
  ProductGridState createState() => ProductGridState();
}

class ProductGridState extends State<ProductGrid> {
  List<dynamic> products = [];
  bool loading = false;
  String error = '';

  @override
  void didUpdateWidget(ProductGrid oldWidget) {
    super.didUpdateWidget(oldWidget);
    if ((widget.searchTerm != oldWidget.searchTerm ||
            widget.image != oldWidget.image) &&
        widget.searchTerm.isNotEmpty) {
      fetchProducts();
    }
  }

  Future<void> fetchProducts() async {
    setState(() {
      loading = true;
      error = '';
      products = [];
    });

    try {
      var request = http.MultipartRequest(
        'POST',
        Uri.parse('http://172.20.10.2:3001/search'),
      );
      request.fields['query'] = widget.searchTerm;
      if (widget.image != null) {
        request.files.add(
          await http.MultipartFile.fromPath('image', widget.image!.path),
        );
      }
      final response = await request.send();
      final responseData = await http.Response.fromStream(response);

      if (response.statusCode == 200) {
        final data = json.decode(responseData.body);
        setState(() {
          products = data['results'] ?? [];
        });
      } else {
        setState(() {
          error = 'Failed to load products: ${response.statusCode}';
        });
      }
    } catch (e) {
      setState(() {
        error = 'Error: $e';
      });
    } finally {
      setState(() {
        loading = false;
      });
    }
  }

  Future<void> _launchURL(String url) async {
    final Uri uri = Uri.parse(url);
    if (await canLaunchUrl(uri)) {
      await launchUrl(uri, mode: LaunchMode.externalApplication);
    } else {
      throw 'Could not launch $url';
    }
  }

  @override
  Widget build(BuildContext context) {
    if (loading) {
      return const Center(child: CircularProgressIndicator());
    }
    if (error.isNotEmpty) {
      return Center(
        child: Text(error, style: const TextStyle(color: Colors.red)),
      );
    }
    if (widget.searchTerm.isEmpty) {
      return const Center(
        child: Text(
          'Enter a search term to see products',
          style: TextStyle(color: Colors.white),
        ),
      );
    }
    if (products.isEmpty) {
      return const Center(
        child: Text('No products found', style: TextStyle(color: Colors.white)),
      );
    }

    return GridView.builder(
      padding: const EdgeInsets.all(16),
      gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
        crossAxisCount: 2,
        childAspectRatio: 0.55,
        crossAxisSpacing: 16,
        mainAxisSpacing: 16,
      ),
      itemCount: products.length,
      itemBuilder: (context, index) {
        final product = products[index];
        final imageUrl =
            product['image_path'] != null
                ? 'http://172.20.10.2:3001/images/${product['image_path'].split('/').last}'
                : (product['image_url'] != null
                    ? 'http://192.168.202.244:3001/proxy-image?url=${Uri.encodeQueryComponent(product['image_url'])}'
                    : null);

        return GestureDetector(
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => ProductDetailPage(product: product),
              ),
            );
          },
          child: Container(
            decoration: BoxDecoration(
              color: Colors.black.withOpacity(0.6),
              borderRadius: BorderRadius.circular(10),
              border: Border.all(color: Colors.transparent, width: 2),
              boxShadow: [
                BoxShadow(color: Colors.cyan.withOpacity(0.7), blurRadius: 10),
              ],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: [
                CachedNetworkImage(
                  imageUrl: imageUrl ?? 'https://via.placeholder.com/150',
                  height: 140,
                  width: double.infinity,
                  fit: BoxFit.cover,
                  placeholder:
                      (context, url) =>
                          const Center(child: CircularProgressIndicator()),
                  errorWidget:
                      (context, url, error) => const Center(
                        child: Text(
                          'NOT FOUND',
                          style: TextStyle(color: Colors.white, fontSize: 12),
                        ),
                      ),
                ),
                Padding(
                  padding: const EdgeInsets.all(6),
                  child: Flexible(
                    child: Text(
                      product['title'] ?? 'Untitled',
                      style: const TextStyle(color: Colors.cyan, fontSize: 13),
                      textAlign: TextAlign.center,
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ),
                if (product['price'] != null)
                  Padding(
                    padding: const EdgeInsets.fromLTRB(6, 0, 6, 2),
                    child: Text(
                      product['price'],
                      style: const TextStyle(
                        color: Colors.white70,
                        fontSize: 11,
                      ),
                      textAlign: TextAlign.center,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                Padding(
                  padding: const EdgeInsets.fromLTRB(6, 0, 6, 4),
                  child: ElevatedButton(
                    onPressed: () {
                      ScaffoldMessenger.of(context).showSnackBar(
                        const SnackBar(content: Text('AR View Coming Soon')),
                      );
                    },
                    style: ElevatedButton.styleFrom(
                      minimumSize: const Size(double.infinity, 28),
                      padding: const EdgeInsets.symmetric(vertical: 4),
                    ),
                    child: const Text(
                      'View in AR',
                      style: TextStyle(fontSize: 11),
                    ),
                  ),
                ),
              ],
            ),
          ),
        );
      },
    );
  }
}
