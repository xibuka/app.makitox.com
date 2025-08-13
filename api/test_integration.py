#!/usr/bin/env python3
"""
Integration test suite for Makitox unified architecture
"""

import asyncio
import aiohttp
import json
import time
from datetime import datetime

class IntegrationTester:
    def __init__(self, base_url="http://localhost:8000"):
        self.base_url = base_url
        self.session = None
        self.results = []
        
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def test_endpoint(self, name, url, expected_status=200, method="GET", 
                           expected_content_type=None, check_json=False):
        """Test a single endpoint"""
        print(f"🧪 Testing {name}...")
        
        try:
            start_time = time.time()
            
            if method == "GET":
                async with self.session.get(f"{self.base_url}{url}") as response:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    text = await response.text()
            elif method == "POST":
                async with self.session.post(f"{self.base_url}{url}") as response:
                    status = response.status
                    content_type = response.headers.get('content-type', '')
                    text = await response.text()
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            # Status check
            status_ok = status == expected_status
            
            # Content type check
            content_type_ok = True
            if expected_content_type:
                content_type_ok = expected_content_type in content_type
            
            # JSON validation
            json_ok = True
            json_data = None
            if check_json:
                try:
                    json_data = json.loads(text)
                    json_ok = True
                except json.JSONDecodeError:
                    json_ok = False
            
            # Overall result
            passed = status_ok and content_type_ok and json_ok
            
            result = {
                "name": name,
                "url": url,
                "method": method,
                "status": status,
                "expected_status": expected_status,
                "status_ok": status_ok,
                "content_type": content_type,
                "content_type_ok": content_type_ok,
                "json_ok": json_ok,
                "response_time_ms": round(response_time, 2),
                "passed": passed,
                "data": json_data
            }
            
            self.results.append(result)
            
            if passed:
                print(f"✅ {name} - {response_time:.0f}ms")
            else:
                print(f"❌ {name} - Status: {status}, Expected: {expected_status}")
                if not content_type_ok:
                    print(f"   Content-Type issue: got {content_type}")
                if not json_ok:
                    print(f"   JSON parsing failed")
            
            return result
            
        except Exception as e:
            print(f"❌ {name} - Error: {e}")
            result = {
                "name": name,
                "url": url,
                "method": method,
                "error": str(e),
                "passed": False,
                "response_time_ms": 0
            }
            self.results.append(result)
            return result
    
    async def run_all_tests(self):
        """Run comprehensive integration tests"""
        print("🚀 Starting Makitox Integration Tests")
        print("=" * 50)
        print(f"Testing server at: {self.base_url}")
        print(f"Test started at: {datetime.now().isoformat()}")
        print()
        
        # Website tests
        print("📱 Website Tests:")
        await self.test_endpoint("Homepage", "/", expected_content_type="text/html")
        await self.test_endpoint("MiraiAlarm Page", "/app-miraialarm", expected_content_type="text/html")
        await self.test_endpoint("Support Page", "/support", expected_content_type="text/html")
        await self.test_endpoint("Privacy Page", "/privacy", expected_content_type="text/html")
        
        print()
        print("🔌 API Tests:")
        
        # API info
        await self.test_endpoint("API Info", "/api", 
                                expected_content_type="application/json", check_json=True)
        
        # Status endpoint
        status_result = await self.test_endpoint("API Status", "/api/status", 
                                                expected_content_type="application/json", check_json=True)
        
        # Gold price endpoints
        latest_result = await self.test_endpoint("Latest Gold Price", "/api/gold-prices/latest",
                                                expected_content_type="application/json", check_json=True)
        
        daily_result = await self.test_endpoint("Daily Gold Prices", "/api/gold-prices",
                                               expected_content_type="application/json", check_json=True)
        
        yearly_result = await self.test_endpoint("Yearly Gold Prices", "/api/gold-prices/yearly",
                                                expected_content_type="application/json", check_json=True)
        
        # Admin endpoint (might be slower)
        print("⚠️  Testing admin update endpoint (may take 2-5 seconds)...")
        update_result = await self.test_endpoint("Force Update", "/api/update", method="POST",
                                                expected_content_type="application/json", check_json=True)
        
        print()
        print("📊 Performance Tests:")
        
        # Test cached performance
        print("Testing cached response performance...")
        cache_times = []
        for i in range(3):
            start = time.time()
            await self.test_endpoint(f"Cached Test {i+1}", "/api/gold-prices/latest", 
                                   expected_content_type="application/json", check_json=True)
            cache_times.append((time.time() - start) * 1000)
        
        avg_cache_time = sum(cache_times) / len(cache_times)
        print(f"📈 Average cached response time: {avg_cache_time:.0f}ms")
        
        print()
        self.print_summary()
        
        return self.results
    
    def print_summary(self):
        """Print test results summary"""
        print("📋 Test Summary:")
        print("-" * 30)
        
        total = len(self.results)
        passed = sum(1 for r in self.results if r.get('passed', False))
        failed = total - passed
        
        print(f"Total Tests: {total}")
        print(f"✅ Passed: {passed}")
        print(f"❌ Failed: {failed}")
        print(f"Success Rate: {(passed/total*100):.1f}%")
        
        if failed > 0:
            print(f"\n❌ Failed Tests:")
            for result in self.results:
                if not result.get('passed', False):
                    print(f"   • {result['name']} - {result.get('error', 'Status/Content issues')}")
        
        # Performance summary
        response_times = [r['response_time_ms'] for r in self.results if r.get('response_time_ms', 0) > 0]
        if response_times:
            avg_time = sum(response_times) / len(response_times)
            max_time = max(response_times)
            min_time = min(response_times)
            
            print(f"\n⚡ Performance Summary:")
            print(f"   Average response: {avg_time:.0f}ms")
            print(f"   Fastest response: {min_time:.0f}ms") 
            print(f"   Slowest response: {max_time:.0f}ms")
        
        # Data validation
        print(f"\n📊 Data Validation:")
        
        for result in self.results:
            if result.get('data') and 'gold-prices' in result['name'].lower():
                data = result['data']
                if 'metadata' in data:
                    entries = data['metadata'].get('total_entries', 0)
                    print(f"   • {result['name']}: {entries} entries")
                elif 'price' in data:
                    price = data.get('price', 0)
                    print(f"   • {result['name']}: ¥{price:,.0f}")

async def main():
    """Run integration tests"""
    
    # Check if server is likely running
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex(('localhost', 8000))
    sock.close()
    
    if result != 0:
        print("❌ Server not accessible on localhost:8000")
        print("💡 Start the server first:")
        print("   python server.py")
        print("   # or")
        print("   ./run.sh")
        return
    
    async with IntegrationTester() as tester:
        results = await tester.run_all_tests()
        
        # Save results
        with open('integration_test_results.json', 'w') as f:
            json.dump({
                'timestamp': datetime.now().isoformat(),
                'base_url': tester.base_url,
                'results': results
            }, f, indent=2)
        
        print(f"\n💾 Results saved to integration_test_results.json")
        
        # Return exit code
        failed_count = sum(1 for r in results if not r.get('passed', False))
        return 0 if failed_count == 0 else 1

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    exit(exit_code)