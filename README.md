<div align="center">
  <img src="https://raw.githubusercontent.com/Aswinvasu04/final-projet/refs/heads/main/placeitxr-removebg-preview%20(2).png" width="350">
  <h1>AI-Powered AR Product Visualization</h1>
  <p><i>PlaceIT XR is an AI-powered AR/VR based shopping app that helps users find and visualize the perfect product fit in their space.</i></p>
</div>

---

## 🚀 Overview  
**Problem Statement**  
Shopping online can be challenging, especially when trying to find products that match a space (furniture, décor) or personal preferences (shoes, accessories). Customers struggle with:

* **Visualizing** how a product fits in their environment.  
* **Matching colors and aesthetics** with their surroundings.  
* **Making informed decisions** before purchasing.  

---

## 🔍 Solution  
PlaceIT XR is a smart AR/VR shopping assistant that:

✔️ **AI-powered search optimization:**
 
User enters the product name. If it's a space-dependent product (like furniture), the user uploads an image of the placement area. A multimodal AI (Gemini) analyzes the space (color scheme, style) and creates an optimized search query. The AI fetches the best-matching results from Google Shopping (top 10-15).

✔️ **3D & AR Integration:**

Users can select a product and visualize it in AR. We web scrape product images and convert them into 3D models using Stable-Fast-3D (running on a server). The generated 3D models are displayed in AR using Unity.

✔️ **VR Real Estate Shopping:**
 
Real estate agents can use our platform to recreate homes/flats in VR. Buyers can browse & place furniture/products inside their VR home before purchasing. Supports Oculus Quest 2 for an immersive experience.

✔️ **Context-Aware AI Chatbot:**
  
A smart AI chatbot helps users find the right product and answers questions. Understands product details, specifications, reviews, and comparisons in real-time. Offers personalized recommendations based on user preferences and search history.

---

## 🎯 Target Audience  
 **Interior Designers** – Ensure perfect decor matches.  
 **Online Shoppers** – Try before you buy.  
 **Retail & E-Commerce** – Enhance customer experience.  
 **Tech Enthusiasts** – Experience AI-driven AR.  

---

## 🗃️ Tech Stack  

| **Category**      | **Technologies**                                  |
|-------------------|---------------------------------------------------|
| **Frontend**      | Flutter                                           |
| **Backend**       | Python, Flask                                     |
| **API**           | Hugging Face, FastAPI                             |
| **Cloud & GPU**   | Vast.AI, Firebase                                 |
| **AR & 3D**       | Unity, Unity XR SDK, Stable-Fast-3D               |
| **Gen AI Models** | Gemini (Shortlisting, Chatbot, Image Analysis)    |

---


## Use Cases

*   Homeowners & Renters – Easily visualize furniture before buying.
*   Fashion Shoppers – Find the best product fit based on style & preference.
*   Real Estate Agents – Offer VR home staging to boost property sales.

---

## 🛠️ Installation

### Flutter Frontend

1.  Follow the official Flutter documentation to set up Flutter on your machine: \[https://docs.flutter.dev/get-started/install](https://docs.flutter.dev/get-started/install)
2.  Clone this repository.
3.  Navigate to the project directory: cd shopping_mobile
4.  Get dependencies: flutter pub get
5.  Run the app: flutter run

### Flask Backend

1.  Navigate to the backend directory (where Code.py and server.py are located).
2.  Install Python dependencies: pip install -r requirements.txt
3.  Set up Gemini API key:
    *   Obtain a Gemini API key from Google AI Studio.
    *   Set the api_key variable in Code.py.
4.  Set up Google Custom Search API key and CSE ID:
    *   Obtain a Google Custom Search API key and CSE ID.
    *   Set the GOOGLE_API_KEY and GOOGLE_CSE_ID variables in Code.py.
5.  Run the Flask server: python Code.py

---


## Usage

### Flutter Frontend

*   *Home Page:* Displays a grid of products with search functionality.
*   *Search:* Use the search bar to find products by keywords or upload an image for image-based search.
*   *Chat Assistant:* Interact with the chat assistant to get product recommendations and answers to shopping-related questions.

### Flask Backend

The Flask server provides the following endpoints:

*   /search: Accepts a search query (text or image) and returns a list of products.
*   /chat: Accepts a user message and returns a response from the shopping assistant.
*   /proxy-image: Proxies images to avoid CORS issues.

---

## Model Uploading and Downloading

The Model-uploading & Downloading directory contains scripts for uploading and downloading 3D models.

*   server.py: A Python script that interacts with a server (likely running in Colab) to upload images, generate 3D models, and download the generated models.
*   To use this functionality:
    1.  Run the Colab server.
    2.  Obtain the ngrok URL from the Colab server.
    3.  Run server.py and enter the ngrok URL when prompted.
    4.  Enter the path to the image you want to upload.
    5.  The script will upload the image, wait for the model to be generated, and download the model to the current directory.

---

## Next Steps for the Hackathon

*   Prototype the AI search system using Gemini.
*   Develop a basic AR model viewer using Unity.
*   Create a demo for the VR real estate feature.

---

## Contributing

Contributions are welcome! Please fork the repository and submit a pull request with your changes.

## License

MIT License

Copyright (c) 2025

Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rightsto use, copy, modify, merge, publish, distribute, sublicense, and/or sellcopies of the Software, and to permit persons to whom the Software is furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS FOR PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
