from playwright.sync_api import sync_playwright
import requests
import os
from urllib.parse import urlparse, urljoin
import time
import mimetypes
import re
def standardize_user_url(user_url):
    """
    Standardizes a user-provided URL to ensure it has proper scheme and format.
    
    Args:
        user_url (str): The URL input by the user
        
    Returns:
        str: The standardized URL with https:// scheme if none was provided
        
    Raises:
        ValueError: If the URL is empty or invalid
    """
    if not user_url or not user_url.strip():
        raise ValueError("URL cannot be empty")
    
    url = user_url.strip()
    
    # Add https:// if no scheme is present
    
    if not url.startswith(('http://', 'https://')):
        url = 'https://' + url
    # Validate the URL structure
    parsed = urlparse(url)
    if not parsed.netloc:
        raise ValueError("Invalid URL format - missing domain")
    
    # Remove any trailing slashes for consistency
    url = url.rstrip('/')
    
    return url

def download_images(image_urls, base_url, folder_name="downloaded_images"):
    """Download all images to specified folder with proper file extensions"""
    os.makedirs(folder_name, exist_ok=True)
    downloaded_files = []
    
    for i, url in enumerate(image_urls):
        try:
            if not url or url.startswith('data:'):
                continue
                
            # Make absolute URL if relative
            url = standardize_user_url(url)
            
            # Get the image with browser-like headers
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, stream=True, timeout=15)
            response.raise_for_status()
            
            # Determine file extension
            content_type = response.headers.get('content-type', '')
            ext = mimetypes.guess_extension(content_type) or '.jpg'
            
            # Clean filename
            parsed = urlparse(url)
            filename = os.path.basename(parsed.path)
            if not filename or '.' not in filename:
                filename = f"image_{i+1}{ext}"
            else:
                # Keep original extension if valid
                _, old_ext = os.path.splitext(filename)
                if len(old_ext) <= 5:  # Reasonable extension length
                    ext = old_ext
                filename = f"image_{i+1}{ext}"
            
            filepath = os.path.join(folder_name, filename)
            
            # Save the image
            with open(filepath, 'wb') as f:
                for chunk in response.iter_content(1024):
                    f.write(chunk)
            
            downloaded_files.append(filepath)
            print(f"Saved: {filename}")
            
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
    
    return downloaded_files

def scrape_images_from_website(url, scroll_times=3, scroll_delay=1):
    """Scrape all images from any website with Playwright"""
    url = standardize_user_url(url)
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        
        try:
            print(f"Navigating to {url}")
            page.goto(url, timeout=60000)
            
            # Scroll to trigger lazy-loaded images
            for _ in range(scroll_times):
                page.evaluate("""() => {
                    window.scrollBy(0, window.innerHeight);
                    return document.body.scrollHeight;
                }""")
                time.sleep(scroll_delay)
            
            # Get all image URLs with various approaches
            image_urls = []
            
            # 1. Standard img tags
            img_elements = page.query_selector_all("img")
            for img in img_elements:
                src = img.get_attribute("src")
                if src:
                    image_urls.append(src)
            
            # 2. CSS background images
            bg_elements = page.query_selector_all("[style*='background-image']")
            for element in bg_elements:
                style = element.get_attribute("style")
                if style and 'url(' in style:
                    start = style.find('url(') + 4
                    end = style.find(')', start)
                    bg_url = style[start:end].strip('"\'').split('?')[0]
                    if bg_url:
                        image_urls.append(bg_url)
            
            # 3. Picture/source elements
            source_elements = page.query_selector_all("picture source, source[srcset]")
            for source in source_elements:
                srcset = source.get_attribute("srcset") or source.get_attribute("src")
                if srcset:
                    # Take the first URL from srcset if multiple exist
                    first_url = srcset.split(',')[0].split()[0]
                    image_urls.append(first_url)
            
            # Remove duplicates
            unique_urls = list(set(image_urls))
            
            return unique_urls
            
        finally:
            browser.close()

if __name__ == "__main__":
    target_url = input("Enter website URL to scrape images from: ").strip()
    
    print("\nStarting image scraping...")
    image_urls = scrape_images_from_website(target_url)
    
    if image_urls:
        print("\nStarting image downloads...")
        downloaded_files = download_images(image_urls, target_url)
        print(f"\nDownloaded {len(downloaded_files)} images to 'downloaded_images' folder")
    else:
        print("No images found on the page")