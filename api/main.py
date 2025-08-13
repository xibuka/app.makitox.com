from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import json
import os
from datetime import datetime, timedelta
import asyncio
from scraper import GoldPriceScraper
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Makitox Gold Price API",
    description="Daily gold prices from Tanaka Precious Metals",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_DIR = "data"
GOLD_PRICES_FILE = os.path.join(DATA_DIR, "gold_prices.json")
YEARLY_PRICES_FILE = os.path.join(DATA_DIR, "gold_prices_yearly.json")
LAST_UPDATE_FILE = os.path.join(DATA_DIR, "last_update.txt")
LAST_YEARLY_UPDATE_FILE = os.path.join(DATA_DIR, "last_yearly_update.txt")

os.makedirs(DATA_DIR, exist_ok=True)

scraper = GoldPriceScraper()

@app.on_event("startup")
async def startup_event():
    """Check if data needs updating on startup"""
    await check_and_update_data()

async def check_and_update_data():
    """Check if data needs updating and update if necessary"""
    needs_update = False
    
    # Check if files exist
    if not os.path.exists(GOLD_PRICES_FILE) or not os.path.exists(LAST_UPDATE_FILE):
        needs_update = True
        logger.info("Data files don't exist, will create them")
    else:
        # Check if data is older than 1 day
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

async def update_gold_prices():
    """Update daily gold prices by scraping the website"""
    try:
        logger.info("Starting daily gold price update...")
        
        # Scrape data
        data = await scraper.scrape_gold_prices()
        
        if not data:
            logger.error("No data returned from scraper")
            return False
        
        # Save data
        with open(GOLD_PRICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Update timestamp
        with open(LAST_UPDATE_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
        
        logger.info(f"Successfully updated daily gold prices with {len(data['prices'])} entries")
        return True
        
    except Exception as e:
        logger.error(f"Error updating daily gold prices: {e}")
        return False

async def check_and_update_yearly_data():
    """Check if yearly data needs updating and update if necessary"""
    needs_update = False
    
    # Check if yearly files exist
    if not os.path.exists(YEARLY_PRICES_FILE) or not os.path.exists(LAST_YEARLY_UPDATE_FILE):
        needs_update = True
        logger.info("Yearly data files don't exist, will create them")
    else:
        # Check if yearly data is older than 1 day
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

async def update_yearly_gold_prices():
    """Update yearly gold prices by scraping the website"""
    try:
        logger.info("Starting yearly gold price update...")
        
        # Scrape yearly data
        data = await scraper.scrape_yearly_prices()
        
        if not data:
            logger.error("No yearly data returned from scraper")
            return False
        
        # Save yearly data
        with open(YEARLY_PRICES_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        # Update yearly timestamp
        with open(LAST_YEARLY_UPDATE_FILE, 'w') as f:
            f.write(datetime.now().isoformat())
        
        logger.info(f"Successfully updated yearly gold prices with {len(data['prices'])} entries")
        return True
        
    except Exception as e:
        logger.error(f"Error updating yearly gold prices: {e}")
        return False

@app.get("/")
async def root():
    """API information"""
    return {
        "message": "Makitox Gold Price API",
        "endpoints": {
            "/gold-prices": "Get daily gold prices",
            "/gold-prices/latest": "Get latest gold price",
            "/gold-prices/yearly": "Get one year of gold prices",
            "/update": "Force update gold prices (admin)",
            "/status": "Get API status"
        }
    }

@app.get("/gold-prices")
async def get_gold_prices():
    """Get all daily gold prices"""
    try:
        # Check if update is needed
        await check_and_update_data()
        
        if not os.path.exists(GOLD_PRICES_FILE):
            raise HTTPException(status_code=404, detail="Gold price data not found")
        
        with open(GOLD_PRICES_FILE, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        return JSONResponse(content=data)
        
    except Exception as e:
        logger.error(f"Error getting gold prices: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/gold-prices/latest")
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
        
        latest = data['prices'][0]  # Assuming first entry is latest
        return {
            "date": latest['date'],
            "price": latest['price']
        }
        
    except Exception as e:
        logger.error(f"Error getting latest gold price: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

@app.get("/gold-prices/yearly")
async def get_yearly_gold_prices():
    """Get one year of gold prices from cached data"""
    try:
        # Check if yearly data needs updating
        await check_and_update_yearly_data()
        
        # Read cached yearly data
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

@app.post("/update")
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

@app.get("/status")
async def get_status():
    """Get API status and last update time"""
    try:
        status = {
            "status": "running",
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