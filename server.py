import requests
import time
import os

def upload_and_process(image_path, server_url):
    try:
        with open(image_path, 'rb') as f:
            files = {'file': (os.path.basename(image_path), f)}
            response = requests.post(
                f"{server_url}/upload-and-process", 
                files=files,
                timeout=120
            )
        return response.json()
    except Exception as e:
        return {"error": str(e)}

def download_model(server_url, save_path):
    try:
        response = requests.get(f"{server_url}/download-model", stream=True)
        response.raise_for_status()
        
        with open(save_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
                
        return f"Model saved to {os.path.abspath(save_path)}"
    except Exception as e:
        return f"Download failed: {str(e)}"

if __name__ == "__main__":
    server_url = input("Enter ngrok URL (from Colab): ").strip()
    image_path = input("Enter image path: ").strip()
    
    # Normalize Windows paths
    image_path = os.path.normpath(image_path)
    
    # Upload and process
    print("\nUploading image...")
    result = upload_and_process(image_path, server_url)
    print("Processing result:", result)
    
    if 'output_dir' in result:
        print("\nWaiting for model generation...")
        time.sleep(60)  # Adjust based on model complexity
        
        # Download model
        output_name = os.path.basename(result['output_dir']) + ".zip"
        download_path = os.path.join(os.getcwd(), output_name)
        print(download_model(server_url, download_path))