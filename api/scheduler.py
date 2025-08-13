import asyncio
import schedule
import time
from datetime import datetime
import logging
from scraper import GoldPriceScraper
import json
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

DATA_DIR = "data"
GOLD_PRICES_FILE = os.path.join(DATA_DIR, "gold_prices.json")
LAST_UPDATE_FILE = os.path.join(DATA_DIR, "last_update.txt")

os.makedirs(DATA_DIR, exist_ok=True)

async def update_gold_prices_scheduled():
    """Scheduled task to update gold prices"""
    logger.info("Starting scheduled gold price update...")
    
    try:
        scraper = GoldPriceScraper()
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
        
        logger.info(f"Successfully updated gold prices with {len(data['prices'])} entries")
        return True
        
    except Exception as e:
        logger.error(f"Error in scheduled update: {e}")
        return False

def run_update():
    """Wrapper to run async update in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        loop.run_until_complete(update_gold_prices_scheduled())
    finally:
        loop.close()

def start_scheduler():
    """Start the scheduler for daily updates"""
    logger.info("Starting gold price scheduler...")
    
    # Schedule daily update at 9:00 AM (when markets typically open)
    schedule.every().day.at("09:00").do(run_update)
    
    # Also schedule an evening update at 6:00 PM
    schedule.every().day.at("18:00").do(run_update)
    
    logger.info("Scheduler configured for daily updates at 9:00 AM and 6:00 PM")
    
    # Run initial update
    logger.info("Running initial update...")
    run_update()
    
    # Keep the scheduler running
    while True:
        schedule.run_pending()
        time.sleep(60)  # Check every minute

if __name__ == "__main__":
    try:
        start_scheduler()
    except KeyboardInterrupt:
        logger.info("Scheduler stopped by user")
    except Exception as e:
        logger.error(f"Scheduler error: {e}")