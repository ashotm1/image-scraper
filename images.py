from playwright.sync_api import sync_playwright
import requests
import os
from urllib.parse import urlparse

def download_images(image_urls, folder_name="downloaded_images"):
    """Download all images to specified folder"""
    # Create folder if it doesn't exist
    os.makedirs(folder_name, exist_ok=True)
    
    for i, url in enumerate(image_urls):
        try:
            if not url:  # Skip empty URLs
                continue
                
            print(f"Downloading image {i+1}/{len(image_urls)}")
            
            # Get the image data
            response = requests.get(url, stream=True)
            response.raise_for_status()  # Raise error for bad status
            
            # Extract filename from URL or generate one
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename:
                filename = f"image_{i+1}.jpg"
            
            # Save the image
            filepath = os.path.join(folder_name, filename)
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            print(f"Saved: {filepath}")
            
        except Exception as e:
            print(f"Failed to download {url}: {str(e)}")

with sync_playwright() as p:
    browser = p.chromium.launch()
    page = browser.new_page()
    
    # Navigate to the page
    page.goto("https://www.bing.com/images/search?q=bombastic+definition&form=HDRSC4&first=1")
    
    # Wait for images to load (adjust timeout as needed)
    page.wait_for_selector("img", state="attached")
    
    # Get all image URLs
    images = page.eval_on_selector_all(
        "img", 
        "elements => elements.map(e => e.src)"
    )
    
    # Filter out blank or placeholder images
    valid_images = [img for img in images if img and not img.startswith("data:image")]
    
    print(f"Found {len(valid_images)} images")
    
    # Close the browser
    browser.close()

# Download all images
if valid_images:
    download_images(valid_images)
else:
    print("No images found to download")