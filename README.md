# 🌟 Makitox Platform

Premium mobile app showcase website with integrated live gold price API.

## 🚀 Quick Start

### Option 1: One-Command Launch (Recommended)

```bash
# Simple launcher script
./run.sh

# Alternative Python launcher
python start.py
```

### Option 2: Manual Setup

```bash
# Install dependencies
pip install -r api/requirements.txt

# Run from project root
python server.py
```


## 📍 Access Your Platform

- **🌐 Website**: http://localhost:8000
- **🔌 API**: http://localhost:8000/api
- **📊 Gold Prices**: http://localhost:8000/api/gold-prices/yearly
- **💊 Health**: http://localhost:8000/api/status

## ✨ Features

### Website
- **Glassmorphism Design**: Modern, elegant UI
- **Live Gold Prices**: Real-time updates on homepage  
- **Responsive Layout**: Mobile-first design
- **App Showcase**: MiraiAlarm and future apps

### API
- **347+ Price Points**: Full year of gold price data
- **Lightning Fast**: ~10ms cached responses
- **Smart Caching**: Daily updates, instant serving
- **JSON Format**: Clean, structured data

## 📁 Project Structure

```
makitox/
├── 🌟 index.html              # Homepage with live gold prices
├── app-miraialarm.html        # MiraiAlarm product page
├── support.html               # Support page
├── privacy.html               # Privacy policy
├── assets/                    # Images, icons
├── css/                       # Stylesheets  
├── js/                        # JavaScript
├── 🚀 server.py               # Main server launcher
├── 🚀 start.py                # Python launcher with auto-setup
├── 🚀 run.sh                  # Shell launcher script
└── api/                       # API server code
    ├── integrated_server.py   # Core server
    ├── scraper.py             # Gold price scraping
    ├── requirements.txt       # Dependencies
    └── data/                  # Cached data
```

## 🎯 API Endpoints

| Endpoint | Description | Cache | Response Time |
|----------|-------------|-------|---------------|
| `GET /api/gold-prices/latest` | Current price | ✅ | ~5ms |
| `GET /api/gold-prices` | Daily data (30 entries) | ✅ | ~10ms |
| `GET /api/gold-prices/yearly` | Full year (347+ entries) | ✅ | ~10ms |
| `POST /api/update` | Force refresh | - | ~2-3s |
| `GET /api/status` | Health check | - | ~1ms |

## 📊 Gold Price Data

### Data Coverage
- **Date Range**: September 2024 → Present
- **Entries**: 347+ individual price points
- **Source**: Tanaka Precious Metals
- **Currency**: Japanese Yen (¥) per gram
- **Updates**: Daily automatic refresh

### Example Response
```json
{
  "metadata": {
    "total_entries": 347,
    "last_updated": "2025-08-13T18:46:30",
    "currency": "JPY",
    "unit": "per gram"
  },
  "prices": [
    {
      "date": "2025-08-13",
      "price": 17567.0,
      "original_price_str": "17567"
    }
  ]
}
```

## 🔧 Configuration

### Environment Variables
```bash
export MAKITOX_PORT=8000        # Server port
export MAKITOX_HOST=0.0.0.0     # Bind address
export MAKITOX_DATA_DIR=api/data # Data directory
```

### Custom Gold Widget Placement
Add this to any HTML page:
```html
<div id="gold-price-display"></div>
<!-- Widget automatically injected -->
```

## 📈 Performance

### Benchmarks
- **Website Loading**: < 100ms
- **API Response (Cached)**: < 10ms  
- **API Response (Fresh)**: < 3s
- **Memory Usage**: ~80MB
- **Concurrent Users**: 100+ supported

### Caching Strategy
- **Daily Data**: 24-hour cache
- **Yearly Data**: 24-hour cache  
- **Force Update**: Manual refresh via `/api/update`
- **Smart Invalidation**: Automatic daily refresh

## 🖥️ Production Deployment

### VPS/Server Deployment
```bash
# With screen/tmux for background running
screen -S makitox
python server.py

# Detach with Ctrl+A, D
# Reattach with: screen -r makitox
```

### Process Management
```bash
# Check if server is running
ps aux | grep "python server.py"

# Kill server if needed
pkill -f "python server.py"

# Restart server
python server.py
```

## 🧪 Testing

### Integration Tests
```bash
python api/test_integration.py
```

### Manual Testing
```bash
# Test website
curl http://localhost:8000

# Test API
curl http://localhost:8000/api/gold-prices/latest

# Test health
curl http://localhost:8000/api/status
```

## 🔒 Security

### Built-in Security
- **Rate Limiting**: API endpoint protection
- **CORS**: Properly configured
- **Input Validation**: FastAPI automatic validation
- **Security Headers**: XSS, frame protection

### Production Recommendations
- **HTTPS**: SSL/TLS certificates
- **Firewall**: Restrict admin endpoints
- **Monitoring**: Health check alerts
- **Backups**: Regular data directory backups

## 🚀 Deployment Options

### Local Development
```bash
python server.py
# → http://localhost:8000
```

### VPS/Server
```bash
# With screen/tmux
screen -S makitox
python server.py

# With systemd
sudo systemctl enable makitox.service
sudo systemctl start makitox
```

### Cloud Platforms
- **Heroku**: Create `Procfile` with `web: python server.py`
- **Railway**: Auto-deploy from Git repository
- **DigitalOcean**: App Platform with Python
- **PythonAnywhere**: Simple Python hosting
- **Vercel**: With Python runtime

## 🛠️ Development

### Adding New Pages
```python
@app.get("/new-page", response_class=HTMLResponse)
async def new_page():
    return serve_html_file("new-page.html")
```

### Customizing Gold Widget
Edit `integrated_server.py` → `inject_gold_price_widget()`

### Adding API Endpoints
```python
@app.get("/api/new-endpoint")
async def new_endpoint():
    return {"message": "Hello World"}
```

## 📚 Documentation

- **Architecture Guide**: `ARCHITECTURE.md`
- **API Documentation**: http://localhost:8000/docs (FastAPI auto-docs)
- **Migration Guide**: `api/migrate.py`

## ❓ Troubleshooting

### Common Issues

1. **Port Already in Use**
   ```bash
   lsof -ti:8000 | xargs kill -9  # Kill process on port 8000
   ```

2. **Dependencies Missing**
   ```bash
   pip install -r api/requirements.txt
   ```

3. **Permission Denied**
   ```bash
   chmod +x run.sh
   ```

4. **Data Directory Issues**
   ```bash
   mkdir -p api/data
   ```

### Getting Help
- **Check Status**: http://localhost:8000/api/status
- **View Logs**: Console output
- **Test API**: http://localhost:8000/docs

## 📄 License

This project is part of the Makitox platform for educational and demonstration purposes.

---

## 🎯 Quick Commands Reference

```bash
# Start server
python start.py

# Quick launcher
./run.sh  

# Run tests
python api/test_integration.py

# Check server status
make status

# View API docs
# Visit: http://localhost:8000/docs
```

---

**Ready to launch your premium mobile app platform with live gold prices! 🌟**