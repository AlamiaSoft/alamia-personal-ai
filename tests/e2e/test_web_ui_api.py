import unittest
import requests
import threading
import time
from src.web.server import start_server

class TestWebUIApi(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.port = 8001
        cls.server_thread = threading.Thread(target=start_server, args=(cls.port, '127.0.0.1'))
        cls.server_thread.daemon = True
        cls.server_thread.start()
        time.sleep(1) # wait for server to start

    def test_static_index(self):
        resp = requests.get(f"http://127.0.0.1:{self.port}/index.html")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("<!DOCTYPE html>", resp.text)
        
    def test_static_css(self):
        resp = requests.get(f"http://127.0.0.1:{self.port}/css/styles.css")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("data-theme", resp.text)
        
    def test_static_js(self):
        resp = requests.get(f"http://127.0.0.1:{self.port}/js/app.js")
        self.assertEqual(resp.status_code, 200)
        self.assertIn("function", resp.text)

    # To fully test API routes we need inventory builder mocks at integration level or test system
    # Since this E2E test starts real server, we can at least test config which is mocked right now
    def test_api_config(self):
        resp = requests.get(f"http://127.0.0.1:{self.port}/api/config")
        self.assertEqual(resp.status_code, 200)
        data = resp.json()
        self.assertIn("mode", data)

if __name__ == '__main__':
    unittest.main()
