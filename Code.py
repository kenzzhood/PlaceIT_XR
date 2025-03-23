import os
import json
import requests
import urllib.parse
from urllib.parse import quote
from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
from fake_useragent import UserAgent
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import google.generativeai as genai
from PIL import Image
import logging
import io

# Configure Flask app
app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": ["http://localhost:*", "http://10.0.2.2:*"]}})  # Allow all localhost ports and emulator

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure the Gemini API with your API key
genai.configure(api_key='AIzaSyAQdFCnSxPofY6Vi4jPidW-7WQVRJJlONM')

# Google Custom Search API credentials
GOOGLE_API_KEY = "AIzaSyCb3XBbRYWXxHk9tjp9yvoSkAPQRSvmEhY"
GOOGLE_CSE_ID = "026cf97a784eb49ca"

def get_google_search_links(query, num_results=10):
    search_url = f"https://www.googleapis.com/customsearch/v1?q={quote(query)}&cx={GOOGLE_CSE_ID}&key={GOOGLE_API_KEY}&num={num_results}"
    logger.info(f"Searching Google with query: {query}")

    try:
        response = requests.get(search_url)
        response.raise_for_status()
        search_results = response.json()
        
        results = []
        if "items" in search_results:
            for item in search_results["items"]:
                results.append({'title': item.get("title"), 'link': item.get("link")})
        else:
            logger.warning("No items found in Google search results")
        
        return results
    except Exception as e:
        logger.error(f"Error fetching Google search results: {e}")
        return []

def generate_perfect_keywords(user_input, image_path=None):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Single prompt combining initial generation and refinement logic
        prompt = (
            f"Given the input '{user_input}', generate a concise set of keywords for an online search targeting the product mentioned, designed to return a variety of results (e.g., multiple brands, styles, or variations). "
            f"Include the product name and any explicit qualifiers (e.g., 'blue', 'cheap') from the input, adding 1-2 general terms (e.g., a prominent brand or category attribute) to enhance diversity without limiting scope. "
            f"Avoid overly specific terms unless explicitly required, and exclude related items or accessories beyond the product category. "
            f"Also, suggest one hypothetical product link (e.g., a plausible URL for a specific product page from a known retailer like Amazon, Walmart, or a brand site) based on the input, ensuring it points to a single product (not a search or category page). "
            f"Return the output in this format: 'Keywords: [keywords separated by spaces]\nLink: [hypothetical product link]'"
        )
        
        # If an image is provided, incorporate image analysis into the same prompt
        if image_path and os.path.exists(image_path):
            img = Image.open(image_path)
            prompt = (
                f"Analyze the image and the input '{user_input}'. Generate a concise set of keywords for an online search targeting the product in '{user_input}', designed to return a variety of results (e.g., multiple brands, styles, or variations). "
                f"Include the product name and any explicit qualifiers from the input, incorporating 1-2 image-specific attributes (e.g., color, material) and a prominent brand or category term to enhance diversity without limiting scope. "
                f"Avoid overly specific terms unless required, and exclude related items or accessories beyond the product category. "
                f"Also, suggest one hypothetical product link (e.g., a plausible URL for a specific product page from a known retailer like Amazon, Walmart, or a brand site) based on the input and image, ensuring it points to a single product. "
                f"Return the output in this format: 'Keywords: [keywords separated by spaces]\nLink: [hypothetical product link]'"
            )
            response = model.generate_content([prompt, img])
        else:
            response = model.generate_content(prompt)
        
        # Parse the response
        response_text = response.text.strip()
        logger.info(f"Generated response: {response_text}")
        
        keywords = ""
        product_link = None
        for line in response_text.split('\n'):
            if line.startswith("Keywords:"):
                keywords = line.replace("Keywords:", "").strip()
            elif line.startswith("Link:"):
                product_link = line.replace("Link:", "").strip()
        
        if not keywords:
            logger.warning("No keywords parsed; using fallback")
            keywords = user_input  # Fallback to raw input
        
        logger.info(f"Generated keywords: {keywords}")
        logger.info(f"Selected product link: {product_link}")
        return keywords, product_link
    
    except Exception as e:
        logger.error(f"Error generating keywords with Gemini API: {e}")
        return user_input, None  # Fallback to original input with no link

def get_gemini_description(product_title):
    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = f"Generate a short product description (2-3 sentences) for the following item: {product_title}"
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        logger.error(f"Error generating description with Gemini API: {e}")
        return "Description not available."

def get_product_image_and_price(url, folder_name, index):
    ua = UserAgent()
    headers = {
        'User-Agent': ua.random,
        'Referer': url,
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5'
    }
    
    options = Options()
    options.add_argument('--headless')
    options.add_argument(f'user-agent={headers["User-Agent"]}')
    options.add_argument('--disable-gpu')
    options.add_argument('--no-sandbox')
    options.add_argument('--enable-unsafe-swiftshader')
    driver = webdriver.Chrome(options=options)
    
    try:
        logger.info(f"Fetching page: {url}")
        driver.get(url)
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        image_url = None
        product_image_selectors = [
            {'id': 'landing-image'},
            {'id': 'main-image'},
            {'class': 'imgTagWrapper'},
            {'class': 'a-dynamic-image'},
        ]
        
        for selector in product_image_selectors:
            for key, value in selector.items():
                img = soup.find('img', {key: value})
                if img:
                    src = img.get('src') or img.get('data-src') or img.get('data-lazy') or img.get('srcset')
                    if src:
                        if src.startswith('//'):
                            src = 'https:' + src
                        elif not src.startswith('http'):
                            src = urllib.parse.urljoin(url, src)
                        
                        try:
                            img_response = requests.head(src, headers=headers, timeout=10)
                            content_type = img_response.headers.get('Content-Type', '')
                            if 'image' in content_type and 'sprite' not in src.lower():
                                image_url = src
                                logger.info(f"Product image URL found: {image_url}")
                                break
                        except Exception as e:
                            logger.error(f"Failed to validate image URL: {e}")
            if image_url:
                break
        
        if not image_url:
            images = soup.find_all('img')
            logger.info(f"Found {len(images)} images on page")
            for img in images:
                src = img.get('src') or img.get('data-src') or img.get('data-lazy') or img.get('srcset')
                if src:
                    if src.startswith('//'):
                        src = 'https:' + src
                    elif not src.startswith('http'):
                        src = urllib.parse.urljoin(url, src)
                    
                    try:
                        img_response = requests.head(src, headers=headers, timeout=10)
                        content_type = img_response.headers.get('Content-Type', '')
                        if 'image' in content_type and 'sprite' not in src.lower():
                            image_url = src
                            logger.info(f"Fallback image URL found: {image_url}")
                            break
                    except Exception as e:
                        logger.error(f"Failed to validate image URL: {e}")
        
        price = "Not found"
        price_elements = soup.find_all(['span', 'div'], class_=['price', 'a-price-whole', 'discounted-price', '_30jeq3'])
        for elem in price_elements:
            text = elem.get_text(strip=True)
            if '₹' in text or 'Rs' in text or text.replace(',', '').isdigit():
                price = text
                break

        return image_url, None, price
    except Exception as e:
        logger.error(f"Error fetching page {url}: {e}")
        return None, None, "Not found"
    finally:
        driver.quit()

def process_search(query, image_path=None):
    keywords, product_link = generate_perfect_keywords(query, image_path)
    
    results = get_google_search_links(keywords)
    if not results:
        logger.warning("No search results returned")
        return []
    
    processed_results = []
    for i, result in enumerate(results, 1):
        image_url, _, price = get_product_image_and_price(result['link'], None, i)
        description = get_gemini_description(result['title'])
        processed_results.append({
            'id': i,
            'title': result['title'],
            'link': result['link'],
            'image_url': image_url if image_url else None,
            'price': price,
            'description': description,
            'selected_link': product_link if i == 1 else None
        })
    
    logger.info(f"Processed {len(processed_results)} results")
    return processed_results

@app.route('/search', methods=['POST'])
def search():
    # Handle query from either form-data or JSON
    query = None
    if request.form and 'query' in request.form:
        query = request.form['query'].strip()
    elif request.get_json() and 'query' in request.get_json():
        query = request.get_json()['query'].strip()
    
    if not query:
        logger.error("No query provided in request")
        return jsonify({'error': 'No query provided'}), 400
    
    # Handle image upload if provided
    image_path = None
    if 'image' in request.files:
        file = request.files['image']
        if file.filename:
            image_path = os.path.join("uploads", file.filename)
            os.makedirs("uploads", exist_ok=True)
            file.save(image_path)
            logger.info(f"Image saved to {image_path}")
    else:
        logger.info("No image provided; proceeding with text-only search")

    results = process_search(query, image_path)
    if not results:
        logger.warning("No results to return")
        return jsonify({'results': [], 'message': 'No results found'}), 200
    
    # Clean up the uploaded image file after processing
    if image_path and os.path.exists(image_path):
        try:
            os.remove(image_path)
            logger.info(f"Deleted temporary image file: {image_path}")
        except Exception as e:
            logger.error(f"Error deleting temporary image file: {e}")
    
    logger.info("Returning search results")
    return jsonify({'results': results})

@app.route('/proxy-image')
def proxy_image():
    image_url = request.args.get('url')
    if not image_url:
        return jsonify({'error': 'No image URL provided'}), 400
    
    try:
        ua = UserAgent()
        headers = {'User-Agent': ua.random}
        response = requests.get(image_url, headers=headers, stream=True)
        if response.status_code != 200:
            return jsonify({'error': 'Failed to fetch image'}), 500
        
        return send_file(
            io.BytesIO(response.content),
            mimetype=response.headers.get('Content-Type', 'image/jpeg')
        )
    except Exception as e:
        logger.error(f"Error proxying image: {e}")
        return jsonify({'error': 'Error fetching image'}), 500

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    if not data or 'message' not in data:
        logger.error("No message provided in request")
        return jsonify({'error': 'No message provided'}), 400

    user_message = data['message'].strip()
    logger.info(f"Received chat message: {user_message}")

    try:
        model = genai.GenerativeModel('gemini-1.5-flash')
        prompt = (
            f"You are a shopping assistant for an app called Artifex. The user has provided the following requirement: '{user_message}'. "
            f"Analyze the requirement and respond in one of three ways:\n"
            f"1. If the user is asking for a specific product recommendation with clear criteria (e.g., 'I need a modern sofa under $500'), extract a search query to find relevant products and provide a brief response. "
            f"   Return the output in this format: 'Response: [your response]\nSearchQuery: [search query]'\n"
            f"2. If the user’s requirement is vague or missing key details (e.g., 'I need a sofa that matches my room colors'), ask a follow-up question to clarify the missing details (e.g., colors, dimensions) and do not provide a search query yet. "
            f"   Return the output in this format: 'Response: [your follow-up question]'\n"
            f"3. If the user is asking a general question unrelated to product search (e.g., 'What is the best material for a sofa?'), provide a helpful response without a search query. "
            f"   Return the output in this format: 'Response: [your response]'"
        )
        response = model.generate_content(prompt)
        response_text = response.text.strip()
        logger.info(f"Gemini response: {response_text}")

        bot_response = ""
        search_query = None
        for line in response_text.split('\n'):
            if line.startswith("Response:"):
                bot_response = line.replace("Response:", "").strip()
            elif line.startswith("SearchQuery:"):
                search_query = line.replace("SearchQuery:", "").strip()

        return jsonify({
            'response': bot_response,
            'searchQuery': search_query
        })
    except Exception as e:
        logger.error(f"Error processing chat message with Gemini API: {e}")
        return jsonify({'response': 'Sorry, I encountered an error. Please try again.'}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=3001, debug=True)