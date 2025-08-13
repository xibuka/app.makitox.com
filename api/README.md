# Makitox Gold Price API

A FastAPI-based service that scrapes daily gold prices from Tanaka Precious Metals and provides them via REST API endpoints.

## Features

- **Daily Gold Prices**: Scrapes current and historical gold prices from Tanaka website
- **Smart Data Handling**: Processes "-" symbols by using previous day's value
- **Automatic Updates**: Updates data daily with background checks
- **RESTful API**: Clean endpoints for accessing gold price data
- **JSON Storage**: Stores scraped data as static JSON files
- **CORS Enabled**: Ready for web frontend integration

## Installation

1. **Clone and Navigate**
   ```bash
   cd api
   ```

2. **Create Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

## Usage

### Development Server

```bash
python main.py
```

Or using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Production Server

```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

## API Endpoints

### Base URL
```
http://localhost:8000
```

### Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/` | API information and available endpoints |
| `GET` | `/gold-prices` | Get all daily gold prices |
| `GET` | `/gold-prices/latest` | Get the latest gold price only |
| `GET` | `/gold-prices/yearly` | Get one year of gold prices (extended data) |
| `POST` | `/update` | Force update gold prices (admin) |
| `GET` | `/status` | Get API status and last update time |

### Example Responses

#### `/gold-prices`
```json
{
  "metadata": {
    "source": "Tanaka Precious Metals",
    "url": "https://gold.tanaka.co.jp/commodity/souba/d-gold.php",
    "currency": "JPY",
    "unit": "per gram",
    "last_updated": "2025-08-13T10:30:00",
    "total_entries": 45
  },
  "prices": [
    {
      "date": "2025-08-13",
      "price": 17567,
      "original_price_str": "17567"
    },
    {
      "date": "2025-08-12",
      "price": 17663,
      "original_price_str": "17663"
    }
  ]
}
```

#### `/gold-prices/latest`
```json
{
  "date": "2025-08-13",
  "price": 17567
}
```

#### `/gold-prices/yearly`
```json
{
  "metadata": {
    "source": "Tanaka Precious Metals",
    "url": "https://gold.tanaka.co.jp/commodity/souba/d-gold.php",
    "currency": "JPY",
    "unit": "per gram",
    "last_updated": "2025-08-13T18:13:54.557898",
    "total_entries": 61,
    "data_type": "yearly"
  },
  "prices": [
    {
      "date": "2025-08-13",
      "price": 17567.0,
      "original_price_str": "17567"
    },
    // ... up to 61 entries spanning approximately one year
    {
      "date": "2025-01-01",
      "price": 13013.0,
      "original_price_str": "-"
    }
  ]
}
```

## Data Update Schedule

### Daily Data (30 entries)
- **Automatic**: Checks for updates on server startup and daily thereafter
- **Manual**: Use `POST /update` endpoint to force immediate update
- **Storage**: Data stored in `data/gold_prices.json`
- **Logging**: Update timestamps stored in `data/last_update.txt`

### Yearly Data (347+ entries)
- **Smart Caching**: Only scrapes once per day, serves cached data for subsequent requests
- **First Request**: May take 2-3 seconds (includes scraping)
- **Cached Requests**: Lightning fast (~10ms) serving from local file
- **Storage**: Data stored in `data/gold_prices_yearly.json`
- **Logging**: Update timestamps stored in `data/last_yearly_update.txt`
- **Manual Update**: Use `POST /update` to force refresh both daily and yearly data

## File Structure

```
api/
├── main.py                    # FastAPI server and endpoints
├── scraper.py                 # Web scraping and data processing
├── scheduler.py               # Daily update scheduler
├── requirements.txt           # Python dependencies
├── README.md                 # This file
└── data/                     # Auto-created directory
    ├── gold_prices.json          # Daily price data (30 entries)
    ├── gold_prices_yearly.json   # Yearly price data (347+ entries)
    ├── last_update.txt           # Daily update timestamp
    └── last_yearly_update.txt    # Yearly update timestamp
```

## Data Processing Logic

1. **Source**: Extracts data from JavaScript arrays on Tanaka website
2. **Fallback**: Falls back to HTML table parsing if JS extraction fails  
3. **"-" Handling**: When a cell contains "-", uses the previous day's price
4. **Sorting**: Data sorted by date (newest first)
5. **Validation**: Cleans and validates price strings before conversion

## Integration with Website

To integrate with your Makitox website:

1. **CORS**: Already configured to allow cross-origin requests
2. **JavaScript Example**:
   ```javascript
   // Fetch latest gold price
   fetch('http://localhost:8000/gold-prices/latest')
     .then(response => response.json())
     .then(data => {
       console.log(`Latest gold price: ¥${data.price}`);
     });
   ```

3. **HTML Example**:
   ```html
   <div id="gold-price">Loading gold price...</div>
   <script>
   fetch('/api/gold-prices/latest')
     .then(response => response.json())
     .then(data => {
       document.getElementById('gold-price').innerHTML = 
         `Gold: ¥${data.price.toLocaleString()}`;
     });
   </script>
   ```

## Testing

Test the scraper directly:
```bash
python scraper.py
```

Test API endpoints:
```bash
# Get status
curl http://localhost:8000/status

# Get latest price
curl http://localhost:8000/gold-prices/latest

# Get yearly data (61+ entries)
curl http://localhost:8000/gold-prices/yearly

# Force update
curl -X POST http://localhost:8000/update
```

## Deployment

For production deployment:

1. **Environment Variables**:
   ```bash
   export PYTHONPATH="${PYTHONPATH}:/path/to/api"
   ```

2. **Systemd Service** (Linux):
   ```ini
   [Unit]
   Description=Makitox Gold Price API
   After=network.target

   [Service]
   Type=simple
   User=www-data
   WorkingDirectory=/path/to/api
   ExecStart=/path/to/venv/bin/uvicorn main:app --host 0.0.0.0 --port 8000
   Restart=always

   [Install]
   WantedBy=multi-user.target
   ```

3. **Nginx Proxy**:
   ```nginx
   location /api/ {
       proxy_pass http://localhost:8000/;
       proxy_set_header Host $host;
       proxy_set_header X-Real-IP $remote_addr;
   }
   ```

## Monitoring

- **Logs**: Check server logs for scraping status and errors
- **Status Endpoint**: Monitor `/status` for health checks
- **Data Files**: Verify `data/gold_prices.json` is updated daily

## Troubleshooting

1. **No Data**: Check internet connection and source website availability
2. **Update Failures**: Verify website structure hasn't changed
3. **Permission Errors**: Ensure write access to `data/` directory
4. **Import Errors**: Verify all dependencies are installed with `pip list`

## Performance & Optimization

### Smart Caching System
- **Yearly Data**: Cached locally, only scrapes once per day
- **Fast Response**: Cached requests served in ~10ms vs 2-3 seconds for scraping
- **Efficient**: No unnecessary network requests for repeated yearly data access
- **Automatic Updates**: Daily refresh ensures data freshness

### Performance Comparison

| Endpoint | First Request | Cached Request | Data Points |
|----------|--------------|----------------|-------------|
| `/gold-prices` | ~1s | ~10ms | 30 entries |
| `/gold-prices/latest` | ~1s | ~5ms | 1 entry |
| `/gold-prices/yearly` | ~2.5s | ~10ms | 347+ entries |

### Cache Management
- **Daily Cache**: `data/gold_prices.json` (updated daily)
- **Yearly Cache**: `data/gold_prices_yearly.json` (updated daily)
- **Timestamps**: Separate tracking for daily vs yearly updates
- **Force Update**: `POST /update` refreshes both caches immediately

## License

This API is part of the Makitox project for educational and demonstration purposes.