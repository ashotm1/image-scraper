# Image Scraper

A Python script that scrapes and downloads all images from any website using Playwright.

## Features

- Scrapes images from `<img>` tags, CSS backgrounds, and `<picture>`/`<source>` elements
- Handles lazy-loaded images by auto-scrolling
- Standardizes URLs and saves images with proper extensions
- Creates a `downloaded_images` folder for all downloads

## Requirements

- Python 3.7+
- Playwright (`pip install playwright`)
- Requests (`pip install requests`)
- Playwright browsers (`python -m playwright install`)


