import json
import logging
import threading
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse
from ..health.health_checker import HealthChecker
from ..metrics.metrics_collector import metrics

logger = logging.getLogger(__name__)

class MonitoringHandler(BaseHTTPRequestHandler):
    def __init__(self, *args, health_checker=None, **kwargs):
        self.health_checker = health_checker or HealthChecker()
        super().__init__(*args, **kwargs)
    
    def do_GET(self):
        """Handle GET requests"""
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/health':
            self._handle_health()
        elif parsed_path.path == '/metrics':
            self._handle_metrics()
        elif parsed_path.path == '/':
            self._handle_root()
        else:
            self._handle_not_found()
    
    def _handle_health(self):
        """Handle health check endpoint"""
        try:
            health_status = self.health_checker.check_health()
            status_code = 200 if self.health_checker.is_healthy() else 503
            
            self.send_response(status_code)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = json.dumps(health_status, indent=2)
            self.wfile.write(response.encode())
            
        except Exception as e:
            logger.error(f"Health check error: {e}")
            self._send_error_response(500, "Internal server error")
    
    def _handle_metrics(self):
        """Handle metrics endpoint"""
        try:
            all_metrics = metrics.get_all_metrics()
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            
            response = json.dumps(all_metrics, indent=2)
            self.wfile.write(response.encode())
            
        except Exception as e:
            logger.error(f"Metrics error: {e}")
            self._send_error_response(500, "Internal server error")
    
    def _handle_root(self):
        """Handle root endpoint"""
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        
        html = '''
        <html>
        <head><title>Kafka Consumer Monitoring</title></head>
        <body>
            <h1>Kafka Consumer Service</h1>
            <ul>
                <li><a href="/health">Health Check</a></li>
                <li><a href="/metrics">Metrics</a></li>
            </ul>
        </body>
        </html>
        '''
        self.wfile.write(html.encode())
    
    def _handle_not_found(self):
        """Handle 404 errors"""
        self._send_error_response(404, "Not found")
    
    def _send_error_response(self, status_code: int, message: str):
        """Send error response"""
        self.send_response(status_code)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        
        error_response = json.dumps({'error': message})
        self.wfile.write(error_response.encode())
    
    def log_message(self, format, *args):
        """Override to use our logger"""
        logger.debug(f"{self.address_string()} - {format % args}")

class MonitoringServer:
    def __init__(self, host='0.0.0.0', port=8080):
        self.host = host
        self.port = port
        self.server = None
        self.server_thread = None
        self.health_checker = HealthChecker()
    
    def start(self):
        """Start the monitoring server"""
        try:
            # Create handler with health checker
            def handler(*args, **kwargs):
                return MonitoringHandler(*args, health_checker=self.health_checker, **kwargs)
            
            self.server = HTTPServer((self.host, self.port), handler)
            self.server_thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.server_thread.start()
            
            logger.info(f"Monitoring server started on {self.host}:{self.port}")
            
        except Exception as e:
            logger.error(f"Failed to start monitoring server: {e}")
            raise
    
    def stop(self):
        """Stop the monitoring server"""
        if self.server:
            self.server.shutdown()
            self.server.server_close()
            logger.info("Monitoring server stopped")
    
    def is_running(self) -> bool:
        """Check if server is running"""
        return self.server_thread and self.server_thread.is_alive()