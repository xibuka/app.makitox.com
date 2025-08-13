import aiohttp
import asyncio
from bs4 import BeautifulSoup
import re
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)

class GoldPriceScraper:
    """Scraper for Tanaka gold prices"""
    
    def __init__(self):
        self.base_url = "https://gold.tanaka.co.jp/commodity/souba/d-gold.php"
        self.yearly_url = "https://gold.tanaka.co.jp/commodity/souba/d-gold.php"  # May need different URL for yearly data
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    
    async def scrape_gold_prices(self) -> Dict[str, Any]:
        """
        Scrape gold prices from the Tanaka website
        Returns formatted JSON data
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(self.base_url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch page: HTTP {response.status}")
                        return {}
                    
                    html = await response.text()
                    
            soup = BeautifulSoup(html, 'html.parser')
            
            # Extract JavaScript data
            prices_data = self._extract_js_data(soup)
            
            if not prices_data:
                # Fallback: try to extract from table
                prices_data = self._extract_table_data(soup)
            
            if not prices_data:
                logger.error("Could not extract price data from any source")
                return {}
            
            # Process data and handle "-" symbols
            processed_data = self._process_price_data(prices_data)
            
            # Format as JSON structure
            result = {
                "metadata": {
                    "source": "Tanaka Precious Metals",
                    "url": self.base_url,
                    "currency": "JPY",
                    "unit": "per gram",
                    "last_updated": datetime.now().isoformat(),
                    "total_entries": len(processed_data)
                },
                "prices": processed_data
            }
            
            logger.info(f"Successfully scraped {len(processed_data)} price entries")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping gold prices: {e}")
            return {}
    
    async def scrape_yearly_prices(self) -> Dict[str, Any]:
        """
        Scrape one year of gold prices from the table structure
        This attempts to extract more comprehensive data including table data
        """
        try:
            async with aiohttp.ClientSession(headers=self.headers) as session:
                async with session.get(self.base_url, timeout=30) as response:
                    if response.status != 200:
                        logger.error(f"Failed to fetch page: HTTP {response.status}")
                        return {}
                    
                    html = await response.text()
                    
            soup = BeautifulSoup(html, 'html.parser')
            
            # Try to extract from JavaScript first
            prices_data = self._extract_js_data(soup)
            
            # Then try to extract from any tables or grid structures
            table_data = self._extract_yearly_table_data(soup)
            if table_data:
                prices_data.extend(table_data)
            
            # Remove duplicates based on date
            seen_dates = set()
            unique_prices = []
            for entry in prices_data:
                if entry['date'] not in seen_dates:
                    unique_prices.append(entry)
                    seen_dates.add(entry['date'])
            
            if not unique_prices:
                logger.error("Could not extract yearly price data")
                return {}
            
            # Process data and handle "-" symbols
            processed_data = self._process_price_data(unique_prices)
            
            # Format as JSON structure
            result = {
                "metadata": {
                    "source": "Tanaka Precious Metals",
                    "url": self.base_url,
                    "currency": "JPY",
                    "unit": "per gram",
                    "last_updated": datetime.now().isoformat(),
                    "total_entries": len(processed_data),
                    "data_type": "yearly"
                },
                "prices": processed_data
            }
            
            logger.info(f"Successfully scraped {len(processed_data)} yearly price entries")
            return result
            
        except Exception as e:
            logger.error(f"Error scraping yearly gold prices: {e}")
            return {}
    
    def _extract_js_data(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Extract price data from JavaScript arrays"""
        try:
            # Find script tags containing the data
            scripts = soup.find_all('script', string=True)
            
            labels_data = []
            prices_data = []
            
            for script in scripts:
                script_text = script.string
                if not script_text:
                    continue
                
                # Extract labels array (dates)
                labels_match = re.search(r'const labels_in\s*=\s*\[(.*?)\]', script_text, re.DOTALL)
                if labels_match:
                    labels_str = labels_match.group(1)
                    # Extract quoted strings
                    labels_data = re.findall(r'"([^"]*)"', labels_str)
                
                # Extract data1 array (prices)
                data_match = re.search(r'const data1\s*=\s*\[(.*?)\]', script_text, re.DOTALL)
                if data_match:
                    data_str = data_match.group(1)
                    # Extract quoted strings
                    prices_data = re.findall(r'"([^"]*)"', data_str)
            
            if not labels_data or not prices_data:
                logger.warning("Could not extract JavaScript data arrays")
                return []
            
            if len(labels_data) != len(prices_data):
                logger.warning(f"Mismatch in data lengths: {len(labels_data)} labels vs {len(prices_data)} prices")
                return []
            
            # Combine labels and prices
            combined_data = []
            for label, price in zip(labels_data, prices_data):
                # Parse date from label (format: "2025-08-13-09:30")
                date_part = label.split('-')[0:3]  # Take YYYY-MM-DD
                date_str = '-'.join(date_part)
                
                combined_data.append({
                    'date': date_str,
                    'price': price
                })
            
            return combined_data
            
        except Exception as e:
            logger.error(f"Error extracting JavaScript data: {e}")
            return []
    
    def _extract_table_data(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """Fallback method to extract data from HTML tables"""
        try:
            # Look for tables with price data
            tables = soup.find_all('table')
            
            for table in tables:
                # Check if this table contains price data
                if self._is_price_table(table):
                    return self._parse_price_table(table)
            
            logger.warning("No suitable price table found")
            return []
            
        except Exception as e:
            logger.error(f"Error extracting table data: {e}")
            return []
    
    def _extract_yearly_table_data(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract yearly data from HTML tables or grid structures
        Looking for table with class price_12months or similar structures
        """
        try:
            # Look for table with price_12months class
            yearly_table = soup.find('table', class_='price_12months')
            if yearly_table:
                return self._parse_yearly_table(yearly_table)
            
            # Look for any table that might contain yearly data
            tables = soup.find_all('table')
            for table in tables:
                if self._is_yearly_price_table(table):
                    return self._parse_yearly_table(table)
            
            # Look for text-based grid structures (fallback)
            return self._extract_text_grid_data(soup)
            
        except Exception as e:
            logger.error(f"Error extracting yearly table data: {e}")
            return []
    
    def _is_yearly_price_table(self, table) -> bool:
        """Check if a table contains yearly price data"""
        try:
            # Check if table has the specific monthly structure we found
            rows = table.find_all('tr')
            if len(rows) < 30:  # Should have ~32 rows (31 days + header)
                return False
                
            # Check first row for month headers
            header_row = rows[0]
            header_cells = header_row.find_all(['th', 'td'])
            if not header_cells:
                return False
                
            header_text = ' '.join(cell.get_text(strip=True) for cell in header_cells)
            
            # Look for 2024年 and 2025年 pattern with months
            has_2024_months = '2024年' in header_text and '月' in header_text
            has_2025_months = '2025年' in header_text and '月' in header_text
            
            # Check for day numbers in first column (1日, 2日, etc.)
            has_days = False
            for row in rows[1:6]:  # Check first few data rows
                cells = row.find_all(['th', 'td'])
                if cells:
                    first_cell = cells[0].get_text(strip=True)
                    if '日' in first_cell and any(d in first_cell for d in ['1', '2', '3', '4', '5']):
                        has_days = True
                        break
            
            return has_2024_months and has_2025_months and has_days
        except:
            return False
    
    def _parse_yearly_table(self, table) -> List[Dict[str, str]]:
        """
        Parse yearly price data from the monthly table structure
        Table format:
        Row 0: ['', '2024年9月', '2024年10月', ..., '2025年8月']
        Row 1: ['1日', price, price, ..., price]
        Row 2: ['2日', price, price, ..., price]
        ...
        """
        try:
            data = []
            rows = table.find_all('tr')
            
            if len(rows) < 2:
                return data
            
            # Parse header row to get month information
            header_row = rows[0]
            header_cells = header_row.find_all(['th', 'td'])
            
            months = []
            for i, cell in enumerate(header_cells[1:], 1):  # Skip first empty cell
                month_text = cell.get_text(strip=True)
                if '年' in month_text and '月' in month_text:
                    # Parse year and month from text like "2024年9月"
                    try:
                        year_month = month_text.replace('年', '-').replace('月', '')
                        if '-' in year_month:
                            year, month = year_month.split('-')
                            months.append((int(year), int(month), i))
                    except:
                        continue
            
            logger.info(f"Found {len(months)} months in table: {months}")
            
            # Parse data rows (each row represents a day)
            for row_idx, row in enumerate(rows[1:], 1):
                cells = row.find_all(['td', 'th'])
                if not cells:
                    continue
                
                # First cell contains the day
                day_text = cells[0].get_text(strip=True)
                if '日' not in day_text:
                    continue
                
                try:
                    day = int(day_text.replace('日', ''))
                except:
                    continue
                
                # Process each month column
                for year, month, col_idx in months:
                    if col_idx < len(cells):
                        price_text = cells[col_idx].get_text(strip=True)
                        
                        # Skip empty or '-' prices for now (will be handled in processing)
                        if price_text and price_text != '-':
                            # Create date string
                            try:
                                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                                # Validate date exists (handles Feb 29, etc.)
                                datetime.strptime(date_str, '%Y-%m-%d')
                                
                                data.append({
                                    'date': date_str,
                                    'price': price_text
                                })
                            except ValueError:
                                # Invalid date (like Feb 30), skip
                                continue
                        elif price_text == '-':
                            # Store '-' entries for processing
                            try:
                                date_str = f"{year:04d}-{month:02d}-{day:02d}"
                                datetime.strptime(date_str, '%Y-%m-%d')
                                
                                data.append({
                                    'date': date_str,
                                    'price': '-'
                                })
                            except ValueError:
                                continue
            
            logger.info(f"Extracted {len(data)} entries from yearly table")
            return data
            
        except Exception as e:
            logger.error(f"Error parsing yearly table: {e}")
            return []
    
    def _extract_text_grid_data(self, soup: BeautifulSoup) -> List[Dict[str, str]]:
        """
        Extract data from text-based grid structures (fallback method)
        """
        try:
            data = []
            # Look for div or pre elements that might contain grid data
            grid_elements = soup.find_all(['div', 'pre', 'p'], string=re.compile(r'\d{4}[-/]\d{1,2}[-/]\d{1,2}'))
            
            for element in grid_elements:
                text = element.get_text()
                # Use regex to find date-price patterns
                patterns = [
                    r'(\d{4}[-/]\d{1,2}[-/]\d{1,2})[^\d]*(\d+)',
                    r'(\d{1,2}[-/]\d{1,2}[-/]\d{4})[^\d]*(\d+)',
                    r'(\d{4}年\d{1,2}月\d{1,2}日)[^\d]*(\d+)'
                ]
                
                for pattern in patterns:
                    matches = re.findall(pattern, text)
                    for match in matches:
                        date_str, price_str = match
                        parsed_date = self._parse_date(date_str)
                        if parsed_date:
                            data.append({
                                'date': parsed_date,
                                'price': price_str
                            })
            
            return data
            
        except Exception as e:
            logger.error(f"Error extracting text grid data: {e}")
            return []
    
    def _is_price_table(self, table) -> bool:
        """Check if a table contains price data"""
        try:
            # Look for indicators that this is a price table
            text = table.get_text().lower()
            return any(indicator in text for indicator in ['価格', 'price', '円', 'yen'])
        except:
            return False
    
    def _parse_price_table(self, table) -> List[Dict[str, str]]:
        """Parse price data from an HTML table"""
        try:
            data = []
            rows = table.find_all('tr')
            
            for row in rows[1:]:  # Skip header row
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    # Assume first cell is date, second is price
                    date_text = cells[0].get_text(strip=True)
                    price_text = cells[1].get_text(strip=True)
                    
                    # Try to parse date
                    parsed_date = self._parse_date(date_text)
                    if parsed_date:
                        data.append({
                            'date': parsed_date,
                            'price': price_text
                        })
            
            return data
            
        except Exception as e:
            logger.error(f"Error parsing price table: {e}")
            return []
    
    def _parse_date(self, date_text: str) -> Optional[str]:
        """Parse date from various formats"""
        try:
            # Remove common Japanese characters
            date_text = re.sub(r'[年月日]', '-', date_text).strip('-')
            
            # Try different date formats
            formats = ['%Y-%m-%d', '%m-%d', '%d']
            
            for fmt in formats:
                try:
                    parsed = datetime.strptime(date_text, fmt)
                    # If no year specified, assume current year
                    if fmt in ['%m-%d', '%d']:
                        parsed = parsed.replace(year=datetime.now().year)
                    return parsed.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            return None
            
        except Exception:
            return None
    
    def _process_price_data(self, raw_data: List[Dict[str, str]]) -> List[Dict[str, Any]]:
        """
        Process price data and handle '-' symbols
        If a price is '-', use the previous day's value
        """
        try:
            # Sort data by date (oldest first) to process chronologically
            sorted_data = sorted(raw_data, key=lambda x: x['date'])
            
            processed_data = []
            previous_price = None
            
            for entry in sorted_data:
                date = entry['date']
                price_str = entry['price'].strip()
                
                # Handle '-' symbol (no change from previous day)
                if price_str == '-':
                    if previous_price is not None:
                        price_value = previous_price
                    else:
                        # If first entry is '-', skip it or use a default
                        logger.warning(f"First entry has '-' price for date {date}, skipping")
                        continue
                else:
                    # Clean price string and convert to number
                    price_cleaned = re.sub(r'[^\d.]', '', price_str)
                    try:
                        price_value = float(price_cleaned) if price_cleaned else 0
                    except ValueError:
                        logger.warning(f"Could not parse price '{price_str}' for date {date}")
                        price_value = previous_price if previous_price is not None else 0
                
                processed_entry = {
                    'date': date,
                    'price': price_value,
                    'original_price_str': price_str
                }
                
                processed_data.append(processed_entry)
                previous_price = price_value
            
            # Sort final data by date (newest first) for API response
            processed_data.sort(key=lambda x: x['date'], reverse=True)
            
            return processed_data
            
        except Exception as e:
            logger.error(f"Error processing price data: {e}")
            return []

# Test function
async def test_scraper():
    """Test the scraper functionality"""
    scraper = GoldPriceScraper()
    
    print("=== Testing regular scraper ===")
    data = await scraper.scrape_gold_prices()
    print(f"Regular scraper - Total entries: {len(data.get('prices', []))}")
    
    if data.get('prices'):
        print("\nFirst 5 entries:")
        for entry in data['prices'][:5]:
            print(f"  {entry['date']}: ¥{entry['price']} (original: {entry['original_price_str']})")
    
    print("\n=== Testing yearly scraper ===")
    yearly_data = await scraper.scrape_yearly_prices()
    print(f"Yearly scraper - Total entries: {len(yearly_data.get('prices', []))}")
    
    if yearly_data.get('prices'):
        print("\nFirst 5 yearly entries:")
        for entry in yearly_data['prices'][:5]:
            print(f"  {entry['date']}: ¥{entry['price']} (original: {entry['original_price_str']})")
        print(f"\nLast 5 yearly entries:")
        for entry in yearly_data['prices'][-5:]:
            print(f"  {entry['date']}: ¥{entry['price']} (original: {entry['original_price_str']})")

if __name__ == "__main__":
    asyncio.run(test_scraper())