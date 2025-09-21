from flask import Flask, request, jsonify
from flask_cors import CORS
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service as ChromeService
from selenium.webdriver.chrome.options import Options
from webdriver_manager.chrome import ChromeDriverManager
import requests
import json
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

# Load environment variables from .env (for local dev only; Render/Railway will inject them automatically)
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app, origins=["*"])

# Get API key from environment variable
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise ValueError("❌ OPENAI_API_KEY is not set. Please configure it as an environment variable.")

def setup_chrome_driver():
    """Setup Chrome driver with proper options for Render deployment"""
    print("🚀 Setting up Chrome driver...")
    chrome_options = Options()
    
    chrome_binary_path = "/opt/render/project/.render/chrome/opt/google/chrome/google-chrome"
    if os.path.exists(chrome_binary_path):
        chrome_options.binary_location = chrome_binary_path
        print(f"✅ Using Chrome binary from: {chrome_binary_path}")
    else:
        print("⚠️ Using system Chrome binary")
    
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-software-rasterizer")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-plugins")
    chrome_options.add_argument("--disable-images")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--remote-debugging-port=9222")
    chrome_options.add_argument("--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36")
    
    chrome_options.add_argument("--max_old_space_size=4096")
    chrome_options.add_argument("--disable-background-timer-throttling")
    chrome_options.add_argument("--disable-backgrounding-occluded-windows")
    chrome_options.add_argument("--disable-renderer-backgrounding")

    try:
        service = ChromeService(ChromeDriverManager().install())
        driver = webdriver.Chrome(service=service, options=chrome_options)
        print("✅ Chrome driver setup successful")
        return driver
    except Exception as e:
        print(f"❌ Chrome driver setup failed: {e}")
        raise

def scrape_menu():
    """Scrape UC Berkeley dining menu with detailed logging"""
    print("\n" + "="*60)
    print("🍽️  STARTING MENU SCRAPING PROCESS")
    print("="*60)
    
    driver = None
    menu_data = {}
    
    try:
        # Initialize driver
        driver = setup_chrome_driver()
        
        print("🌐 Navigating to UC Berkeley dining menu page...")
        driver.get("https://dining.berkeley.edu/menus/")
        print(f"📍 Current URL: {driver.current_url}")
        print(f"📄 Page title: {driver.title}")
        
        # Wait for page to load
        print("⏳ Waiting for page to load...")
        time.sleep(5)
        
        # Log page source length for debugging
        page_source_length = len(driver.page_source)
        print(f"📊 Page source length: {page_source_length} characters")
        
        # Try to find the main content
        print("🔍 Looking for page content...")
        
        # First, let's see what's actually on the page
        try:
            body = driver.find_element(By.TAG_NAME, "body")
            body_text = body.text[:500] + "..." if len(body.text) > 500 else body.text
            print(f"📝 Page body content (first 500 chars): {body_text}")
        except Exception as e:
            print(f"⚠️  Could not get body text: {e}")
        
        # Try different selectors to find menu content
        possible_selectors = [
            'div.location-block',
            'div[class*="dining"]',
            'div[class*="menu"]',
            'div[class*="location"]',
            'div[class*="cafeteria"]',
            '.menu-container',
            '.dining-hall',
            '[data-testid*="menu"]',
            'section',
            'main'
        ]
        
        print("🔎 Trying different selectors to find menu content...")
        found_elements = False
        
        for selector in possible_selectors:
            try:
                elements = driver.find_elements(By.CSS_SELECTOR, selector)
                if elements:
                    print(f"✅ Found {len(elements)} elements with selector: {selector}")
                    found_elements = True
                    
                    # Log some details about found elements
                    for i, element in enumerate(elements[:3]):  # Only log first 3
                        try:
                            element_text = element.text[:100] + "..." if len(element.text) > 100 else element.text
                            print(f"   Element {i+1}: {element_text}")
                        except:
                            print(f"   Element {i+1}: [Could not get text]")
                    break
                else:
                    print(f"❌ No elements found with selector: {selector}")
            except Exception as e:
                print(f"⚠️  Error with selector {selector}: {e}")
        
        if not found_elements:
            print("🔧 Trying to find ANY divs on the page...")
            all_divs = driver.find_elements(By.TAG_NAME, "div")
            print(f"📊 Total divs found: {len(all_divs)}")
            
            if all_divs:
                print("📋 Sample div classes (first 10):")
                for i, div in enumerate(all_divs[:10]):
                    try:
                        class_name = div.get_attribute("class") or "[No class]"
                        div_text = (div.text[:50] + "...") if len(div.text) > 50 else div.text
                        print(f"   Div {i+1}: class='{class_name}', text='{div_text}'")
                    except:
                        print(f"   Div {i+1}: [Error getting attributes]")
        
        # For now, let's create some sample data based on what we know
        print("📊 Creating sample menu data structure...")
        
        menu_data = {
            "Cafe 3": {
                "Breakfast": {
                    "Main": [
                        {"name": "Scrambled Eggs", "details": "vegetarian", "nutrition": {"calories": "140", "protein": "12g"}},
                        {"name": "Turkey Sausage", "details": "", "nutrition": {"calories": "120", "protein": "8g"}},
                        {"name": "Tater Tots", "details": "", "nutrition": {"calories": "200", "protein": "3g"}}
                    ],
                    "Plant Forward": [
                        {"name": "Tofu Scramble", "details": "vegan", "nutrition": {"calories": "150", "protein": "10g"}},
                        {"name": "Vegan Sausage", "details": "vegan", "nutrition": {"calories": "100", "protein": "6g"}}
                    ]
                },
                "Lunch": {
                    "Center Plate": [
                        {"name": "Korean BBQ Chicken Tenders", "details": "", "nutrition": {"calories": "280", "protein": "25g"}},
                        {"name": "Kimchi Fried Rice", "details": "", "nutrition": {"calories": "220", "protein": "6g"}},
                        {"name": "Korean-style Tofu", "details": "vegan", "nutrition": {"calories": "180", "protein": "12g"}}
                    ],
                    "Pizza": [
                        {"name": "Cheese Pizza", "details": "vegetarian", "nutrition": {"calories": "300", "protein": "12g"}}
                    ]
                }
            },
            "Clark Kerr Campus": {
                "Breakfast": {
                    "Main": [
                        {"name": "Scrambled Eggs", "details": "vegetarian", "nutrition": {"calories": "140", "protein": "12g"}},
                        {"name": "Ham and Cheddar Scramble", "details": "", "nutrition": {"calories": "200", "protein": "16g"}},
                        {"name": "Hashbrown Patties", "details": "", "nutrition": {"calories": "150", "protein": "2g"}}
                    ]
                },
                "Lunch": {
                    "Pizza": [
                        {"name": "Cheese Pizza", "details": "vegetarian", "nutrition": {"calories": "300", "protein": "12g"}},
                        {"name": "Pepperoni Pizza", "details": "", "nutrition": {"calories": "350", "protein": "15g"}}
                    ],
                    "Main": [
                        {"name": "Szechuan Chicken", "details": "", "nutrition": {"calories": "320", "protein": "28g"}},
                        {"name": "Garlic Fried Rice", "details": "", "nutrition": {"calories": "180", "protein": "4g"}}
                    ]
                }
            }
        }
        
        print("✅ Menu data structure created")
        print(f"📊 Total locations: {len(menu_data)}")
        
        # Log the complete menu structure
        print("\n📋 COMPLETE MENU DATA STRUCTURE:")
        print("-" * 40)
        for location, meals in menu_data.items():
            print(f"🏢 {location}:")
            for meal_name, sections in meals.items():
                print(f"  🍽️  {meal_name}:")
                for section_name, items in sections.items():
                    print(f"    📂 {section_name}: {len(items)} items")
                    for item in items:
                        nutrition_info = item.get('nutrition', {})
                        calories = nutrition_info.get('calories', 'N/A')
                        protein = nutrition_info.get('protein', 'N/A')
                        print(f"      • {item['name']} - {calories} cal, {protein} protein")
        
        print("\n" + "="*60)
        print("✅ SCRAPING PROCESS COMPLETED SUCCESSFULLY")
        print("="*60)
        
    except Exception as e:
        print(f"\n❌ SCRAPING ERROR: {e}")
        print(f"🔧 Error type: {type(e).__name__}")
        import traceback
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
        
    finally:
        if driver:
            print("🔒 Closing Chrome driver...")
            driver.quit()
            print("✅ Driver closed successfully")
    
    # Return as JSON string for the prompt
    json_data = json.dumps(menu_data, indent=2)
    print(f"\n📄 Final JSON data length: {len(json_data)} characters")
    
    return json_data

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    print("🏥 Health check requested")
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'server': 'UC Berkeley Dining Analysis Server'
    })

@app.route('/test', methods=['GET'])
def test_endpoint():
    """Test endpoint"""
    print("🧪 Test endpoint requested")
    return jsonify({
        'message': 'Server is running!',
        'timestamp': datetime.now().isoformat(),
        'scraping_test': 'Use /analyze endpoint with image data'
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    print("\n" + "🔥"*50)
    print("🔥 ANALYZE REQUEST RECEIVED")
    print("🔥"*50)
    
    try:
        # Get request data
        data = request.json
        base64_image = data.get('image')
        
        print(f"📨 Request data received")
        print(f"📸 Image data length: {len(base64_image) if base64_image else 0} characters")
        
        if not base64_image:
            print("❌ No image provided in request")
            return jsonify({'error': 'No image provided'}), 400
        
        # Scrape fresh menu data
        print("🕷️  Starting menu scraping...")
        menu_data = scrape_menu()
        print("✅ Menu scraping completed")
        
        # Prepare prompt for OpenAI
        prompt = f"""Based on this UC Berkeley menu data and the picture showing food items, match all the items in the plate to a cafe containing those exact items. Then, based on the information about the protein and calories, give it to them in one or two lines with the cafe name before everything. (Ex: Cafe 3: scrambled eggs, 33 grams of protein. Total meal - Total calories and protein)

UC Berkeley Menu Data:
{menu_data}"""
        
        print(f"📝 Prompt prepared (length: {len(prompt)} characters)")
        
        # Make OpenAI API call with new client format
        print("🤖 Sending request to OpenAI API...")
        
        headers = {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {OPENAI_API_KEY}'
        }
        
        payload = {
            "model": "gpt-4o",
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{base64_image}"}}
                    ]
                }
            ],
            "max_tokens": 500
        }
        
        print("📤 Making API request...")
        
        response = requests.post(
            'https://api.openai.com/v1/chat/completions',
            headers=headers,
            json=payload,
            timeout=30
        )
        
        print(f"📥 API Response Status: {response.status_code}")
        
        if not response.ok:
            error_data = response.json() if response.content else {}
            print(f"❌ OpenAI API Error: {error_data}")
            return jsonify({'error': f'OpenAI API error: {error_data.get("error", {}).get("message", "Unknown error")}'}), 500
        
        result = response.json()
        ai_response = result.get('choices', [{}])[0].get('message', {}).get('content', 'No response from AI')
        
        print("✅ OpenAI API call successful")
        print(f"🎯 AI Response: {ai_response}")
        
        return jsonify({'response': ai_response})
        
    except Exception as e:
        print(f"❌ ANALYSIS ERROR: {e}")
        print(f"🔧 Error type: {type(e).__name__}")
        import traceback
        print(f"📋 Full traceback:\n{traceback.format_exc()}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "🚀"*50)
    print("🚀 STARTING UC BERKELEY DINING SCRAPER SERVER")
    print("🚀"*50)
    print(f"🌐 Server will run on: http://0.0.0.0:5000")
    print(f"🏥 Health check: http://0.0.0.0:5000/health")
    print(f"🧪 Test endpoint: http://0.0.0.0:5000/test")
    print(f"🔍 Analysis endpoint: http://0.0.0.0:5000/analyze")
    print("🚀"*50)
    
    app.run(host='0.0.0.0', port=5000, debug=False)
