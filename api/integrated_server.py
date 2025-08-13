from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json
import os
from datetime import datetime, timedelta
import asyncio
from scraper import GoldPriceScraper
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize FastAPI app
app = FastAPI(
    title="Makitox - Premium Mobile Apps & Gold Price API",
    description="Unified platform serving Makitox website and gold price API",
    version="2.0.0"
)

# Enable CORS for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration
DATA_DIR = "data"
STATIC_DIR = "../"  # Path to static website files
GOLD_PRICES_FILE = os.path.join(DATA_DIR, "gold_prices.json")
YEARLY_PRICES_FILE = os.path.join(DATA_DIR, "gold_prices_yearly.json")
LAST_UPDATE_FILE = os.path.join(DATA_DIR, "last_update.txt")
LAST_YEARLY_UPDATE_FILE = os.path.join(DATA_DIR, "last_yearly_update.txt")

os.makedirs(DATA_DIR, exist_ok=True)
scraper = GoldPriceScraper()

# ============================================================================
# STATIC WEBSITE ROUTES
# ============================================================================

def setup_static_files():
    """Setup static file mounts based on current STATIC_DIR"""
    # Clear existing static mounts if they exist
    if hasattr(app, '_static_mounts_setup'):
        # Remove existing mounts
        for route in list(app.routes):
            if hasattr(route, 'path') and route.path in ['/assets', '/css', '/js']:
                app.routes.remove(route)
    
    # Mount static assets
    if os.path.exists(os.path.join(STATIC_DIR, "assets")):
        app.mount("/assets", StaticFiles(directory=os.path.join(STATIC_DIR, "assets")), name="assets")
    if os.path.exists(os.path.join(STATIC_DIR, "css")):
        app.mount("/css", StaticFiles(directory=os.path.join(STATIC_DIR, "css")), name="css")
    if os.path.exists(os.path.join(STATIC_DIR, "js")):
        app.mount("/js", StaticFiles(directory=os.path.join(STATIC_DIR, "js")), name="js")
    
    app._static_mounts_setup = True

# Initial setup
setup_static_files()

@app.get("/", response_class=HTMLResponse)
async def homepage():
    """Serve the main homepage"""
    return serve_html_file("index.html")

@app.get("/app-miraialarm", response_class=HTMLResponse)
async def miraialarm_page():
    """Serve MiraiAlarm product page"""
    return serve_html_file("app-miraialarm.html")

@app.get("/support", response_class=HTMLResponse)
async def support_page():
    """Serve support page"""
    return serve_html_file("support.html")

@app.get("/privacy", response_class=HTMLResponse)
async def privacy_page():
    """Serve privacy policy page"""
    return serve_html_file("privacy.html")

# Also serve with .html extensions for direct file access
@app.get("/app-miraialarm.html", response_class=HTMLResponse)
async def miraialarm_page_html():
    """Serve MiraiAlarm product page with .html extension"""
    return serve_html_file("app-miraialarm.html")

@app.get("/support.html", response_class=HTMLResponse)
async def support_page_html():
    """Serve support page with .html extension"""
    return serve_html_file("support.html")

@app.get("/privacy.html", response_class=HTMLResponse)
async def privacy_page_html():
    """Serve privacy policy page with .html extension"""
    return serve_html_file("privacy.html")

def serve_html_file(filename: str):
    """Helper to serve HTML files with error handling"""
    try:
        file_path = os.path.join(STATIC_DIR, filename)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Inject gold price widget script if this is the homepage
            if filename == "index.html":
                content = inject_gold_price_widget(content)
            
            return HTMLResponse(content=content)
        else:
            raise HTTPException(status_code=404, detail=f"Page {filename} not found")
    except Exception as e:
        logger.error(f"Error serving {filename}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

def inject_gold_price_widget(html_content: str) -> str:
    """Inject live gold price widget into the homepage"""
    widget_script = """
    <!-- Live Gold Price Widget -->
    <script>
    async function loadGoldPrice() {
        try {
            const response = await fetch('/api/gold-prices/latest');
            const data = await response.json();
            const priceElement = document.getElementById('gold-price-display');
            if (priceElement && data.price) {
                priceElement.innerHTML = `
                    <div class="gold-price-widget">
                        <span class="gold-label">Live Gold Price:</span>
                        <span class="gold-price">¥${data.price.toLocaleString()}</span>
                        <span class="gold-unit">per gram</span>
                        <small class="gold-date">${new Date(data.date).toLocaleDateString()}</small>
                    </div>
                `;
            }
        } catch (error) {
            console.error('Failed to load gold price:', error);
        }
    }
    
    // Load gold price when page loads
    document.addEventListener('DOMContentLoaded', loadGoldPrice);
    // Refresh every 5 minutes
    setInterval(loadGoldPrice, 5 * 60 * 1000);
    </script>
    
    <style>
    .gold-price-widget {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 8px 16px;
        background: rgba(249, 115, 22, 0.1);
        border: 1px solid rgba(249, 115, 22, 0.3);
        border-radius: 8px;
        font-size: 14px;
        margin: 8px 0;
    }
    .gold-price {
        font-weight: 600;
        color: #f97316;
    }
    .gold-date {
        color: #6b7280;
        font-size: 12px;
    }
    </style>
    """
    
    # Inject before closing </body> tag
    if "</body>" in html_content:
        html_content = html_content.replace("</body>", f"{widget_script}</body>")
    
    return html_content

# ============================================================================
# API ROUTES
# ============================================================================

@app.on_event("startup")
async def startup_event():
    """Initialize data on startup"""
    await check_and_update_data()

async def check_and_update_data():
    """Check if data needs updating and update if necessary"""
    needs_update = False
    
    if not os.path.exists(GOLD_PRICES_FILE) or not os.path.exists(LAST_UPDATE_FILE):
        needs_update = True
        logger.info("Data files don't exist, will create them")
    else:
        try:
            with open(LAST_UPDATE_FILE, 'r') as f:
                last_update = datetime.fromisoformat(f.read().strip())
            
            if datetime.now() - last_update > timedelta(days=1):
                needs_update = True
                logger.info("Data is older than 1 day, will update")
        except Exception as e:
            logger.error(f"Error checking last update time: {e}")
            needs_update = True
    
    if needs_update:
        await update_gold_prices()

async def check_and_update_yearly_data():
    """Check if yearly data needs updating and update if necessary"""
    needs_update = False
    
    if not os.path.exists(YEARLY_PRICES_FILE) or not os.path.exists(LAST_YEARLY_UPDATE_FILE):
        needs_update = True
        logger.info("Yearly data files don't exist, will create them")
    else:
        try:
            with open(LAST_YEARLY_UPDATE_FILE, 'r') as f:
                last_update = datetime.fromisoformat(f.read().strip())
            
            if datetime.now() - last_update > timedelta(days=1):
                needs_update = True
                logger.info("Yearly data is older than 1 day, will update")
        except Exception as e:
            logger.error(f"Error checking yearly update time: {e}")
            needs_update = True
    
    if needs_update:
        await update_yearly_gold_prices()

async def update_gold_prices():
    """Update daily gold prices by scraping the website"""
    try:
        logger.info("Starting daily gold price update...")
        data = await scraper.scrape_gold_prices()
        
        if not data:
            logger.error("No data returned from scraper")
            return False
        
        with open(GOLD_PRICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(LAST_UPDATE_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
        
        logger.info(f"Successfully updated daily gold prices with {len(data['prices'])} entries")
        return True
        
    except Exception as e:
        logger.error(f"Error updating daily gold prices: {e}")
        return False

async def update_yearly_gold_prices():
    """Update yearly gold prices by scraping the website"""
    try:
        logger.info("Starting yearly gold price update...")
        data = await scraper.scrape_yearly_prices()
        
        if not data:
            logger.error("No yearly data returned from scraper")
            return False
        
        with open(YEARLY_PRICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        with open(LAST_YEARLY_UPDATE_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
        
        logger.info(f"Successfully updated yearly gold prices with {len(data['prices'])} entries")
        return True
        
    except Exception as e:
        logger.error(f"Error updating yearly gold prices: {e}")
        return False

# API Information
@app.get("/api")
async def api_info():
    """API information and available endpoints"""
    return {
        "message": "Makitox Gold Price API",
        "version": "2.0.0",
        "endpoints": {
            "/api/gold-prices": "Get daily gold prices (30 entries)",
            "/api/gold-prices/latest": "Get latest gold price only",
            "/api/gold-prices/yearly": "Get one year of gold prices (347+ entries)",
            "/api/update": "Force update gold prices (admin)",
            "/api/status": "Get API status and cache information"
        },
        "website": {
            "/": "Makitox homepage with live gold prices",
            "/app-miraialarm": "MiraiAlarm product page", 
            "/support": "Support and contact page",
            "/privacy": "Privacy policy page"
        }
    }

@app.get("/api/gold-prices")
async def get_gold_prices():
    """Get daily gold prices"""
    try:
        await check_and_update_data()
        
        if not os.path.exists(GOLD_PRICES_FILE):
            raise HTTPException(status_code=404, detail="Gold price data not found")
        
        with open(GOLD_PRICES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return JSONResponse(content=data)
        
    except Exception as e:
        logger.error(f"Error getting gold prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/gold-prices/latest")
async def get_latest_gold_price():
    """Get the latest gold price"""
    try:
        await check_and_update_data()
        
        if not os.path.exists(GOLD_PRICES_FILE):
            raise HTTPException(status_code=404, detail="Gold price data not found")
        
        with open(GOLD_PRICES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        if not data['prices']:
            raise HTTPException(status_code=404, detail="No price data available")
        
        latest = data['prices'][0]
        return {
            "date": latest['date'],
            "price": latest['price']
        }
        
    except Exception as e:
        logger.error(f"Error getting latest gold price: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/gold-prices/yearly")
async def get_yearly_gold_prices():
    """Get one year of gold prices from cached data"""
    try:
        await check_and_update_yearly_data()
        
        if not os.path.exists(YEARLY_PRICES_FILE):
            raise HTTPException(status_code=404, detail="Yearly gold price data not found")
        
        with open(YEARLY_PRICES_FILE, 'r', encoding='utf-8') as f:
            yearly_data = json.load(f)
        
        return JSONResponse(content=yearly_data)
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting yearly gold prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/api/update")
async def force_update():
    """Force update gold prices (admin endpoint)"""
    try:
        daily_success = await update_gold_prices()
        yearly_success = await update_yearly_gold_prices()
        
        if daily_success and yearly_success:
            return {
                "message": "Gold prices updated successfully", 
                "daily_updated": True,
                "yearly_updated": True
            }
        elif daily_success:
            return {
                "message": "Daily gold prices updated, yearly update failed",
                "daily_updated": True,
                "yearly_updated": False
            }
        elif yearly_success:
            return {
                "message": "Yearly gold prices updated, daily update failed",
                "daily_updated": False,
                "yearly_updated": True
            }
        else:
            raise HTTPException(status_code=500, detail="Failed to update gold prices")
            
    except Exception as e:
        logger.error(f"Error in force update: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/api/status")
async def get_status():
    """Get API status and cache information"""
    try:
        status = {
            "status": "running",
            "version": "2.0.0",
            "server_type": "integrated",
            "daily_data": {
                "available": os.path.exists(GOLD_PRICES_FILE),
                "last_update": None,
                "total_entries": 0
            },
            "yearly_data": {
                "available": os.path.exists(YEARLY_PRICES_FILE),
                "last_update": None,
                "total_entries": 0
            }
        }
        
        # Daily data status
        if os.path.exists(LAST_UPDATE_FILE):
            with open(LAST_UPDATE_FILE, 'r') as f:
                status["daily_data"]["last_update"] = f.read().strip()
        
        if os.path.exists(GOLD_PRICES_FILE):
            with open(GOLD_PRICES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                status["daily_data"]["total_entries"] = len(data.get('prices', []))
        
        # Yearly data status
        if os.path.exists(LAST_YEARLY_UPDATE_FILE):
            with open(LAST_YEARLY_UPDATE_FILE, 'r') as f:
                status["yearly_data"]["last_update"] = f.read().strip()
        
        if os.path.exists(YEARLY_PRICES_FILE):
            with open(YEARLY_PRICES_FILE, 'r', encoding='utf-8') as f:
                data = json.load(f)
                status["yearly_data"]["total_entries"] = len(data.get('prices', []))
        
        return status
        
    except Exception as e:
        logger.error(f"Error getting status: {e}")
        return {"status": "error", "message": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)