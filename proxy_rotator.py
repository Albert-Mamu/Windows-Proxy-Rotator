import threading
import time
import random
import re
from typing import List, Dict, Optional, Tuple
from datetime import datetime
import requests
from proxy_checker import ProxyChecker

class ProxyRotator:
    def __init__(self, proxy_file: str = "proxy.txt"):
        self.proxy_file = proxy_file
        self.proxies: List[Dict] = []
        self.current_proxy: Optional[Dict] = None
        self.rotation_interval = 300
        self.is_rotating = False
        self.rotation_thread: Optional[threading.Thread] = None
        self.checker = ProxyChecker()
        self.load_proxies()
        
    def parse_proxy_line(self, line: str) -> Optional[Dict]:
        """
        Parse proxy line with format: ip:port:username:password
        Supports: http, https, socks4, socks5
        """
        line = line.strip()
        if not line:
            return None
            
        # Match proxy patterns
        patterns = [
            # ip:port:user:pass
            r'^(\d+\.\d+\.\d+\.\d+):(\d+):([^:]+):([^:]+)$',
            # ip:port:user (no password)
            r'^(\d+\.\d+\.\d+\.\d+):(\d+):([^:]+)$',
            # ip:port
            r'^(\d+\.\d+\.\d+\.\d+):(\d+)$'
        ]
        
        for pattern in patterns:
            match = re.match(pattern, line)
            if match:
                groups = match.groups()
                ip, port = groups[0], groups[1]
                username = groups[2] if len(groups) > 2 else None
                password = groups[3] if len(groups) > 3 else None
                
                # Auto-detect protocol based on port or other heuristics
                protocol = self.detect_protocol(port, line)
                
                return {
                    'ip': ip,
                    'port': port,
                    'username': username,
                    'password': password,
                    'protocol': protocol,
                    'raw_line': line
                }
        
        # If no pattern matches, try to parse as URL
        return self.parse_proxy_url(line)
    
    def parse_proxy_url(self, line: str) -> Optional[Dict]:
        """Parse proxy in URL format"""
        try:
            if '://' in line:
                protocol, rest = line.split('://', 1)
                if '@' in rest:
                    # With authentication: protocol://user:pass@ip:port
                    auth_host = rest.split('@', 1)
                    auth_part, host_part = auth_host[0], auth_host[1]
                    username, password = auth_part.split(':', 1) if ':' in auth_part else (auth_part, None)
                    
                    if ':' in host_part:
                        ip, port = host_part.split(':', 1)
                    else:
                        ip, port = host_part, None
                else:
                    # Without authentication
                    username, password = None, None
                    if ':' in rest:
                        ip, port = rest.split(':', 1)
                    else:
                        ip, port = rest, None
                
                return {
                    'ip': ip,
                    'port': port,
                    'username': username,
                    'password': password,
                    'protocol': protocol.lower(),
                    'raw_line': line
                }
        except Exception as e:
            print(f"Error parsing proxy URL {line}: {e}")
        
        return None
    
    def detect_protocol(self, port: str, line: str) -> str:
        """Auto-detect proxy protocol"""
        port_num = int(port) if port.isdigit() else None
        
        # Common proxy ports
        if port_num in [1080, 1081, 1082]:
            return 'socks5'
        elif port_num in [8080, 3128, 80, 8000]:
            return 'http'
        elif port_num in [443, 8443]:
            return 'https'
        elif 'socks4' in line.lower():
            return 'socks4'
        elif 'socks5' in line.lower():
            return 'socks5'
        elif 'https' in line.lower():
            return 'https'
        else:
            return 'http'  # Default to HTTP
    
    def format_proxy_url(self, proxy: Dict) -> str:
        """Format proxy dict to proper URL"""
        protocol = proxy.get('protocol', 'http')
        ip = proxy['ip']
        port = proxy['port']
        username = proxy.get('username')
        password = proxy.get('password')
        
        if username and password:
            return f"{protocol}://{username}:{password}@{ip}:{port}"
        elif username:
            return f"{protocol}://{username}@{ip}:{port}"
        else:
            return f"{protocol}://{ip}:{port}"
    
    def format_requests_proxy(self, proxy: Dict) -> Dict[str, str]:
        """Format proxy for requests library"""
        proxy_url = self.format_proxy_url(proxy)
        protocol = proxy.get('protocol', 'http')
        
        # Map protocol to requests proxy keys
        if protocol in ['http', 'https']:
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        elif protocol == 'socks4':
            return {
                'http': f"socks4://{proxy_url.split('://')[1]}",
                'https': f"socks4://{proxy_url.split('://')[1]}"
            }
        elif protocol == 'socks5':
            return {
                'http': f"socks5://{proxy_url.split('://')[1]}",
                'https': f"socks5://{proxy_url.split('://')[1]}"
            }
        else:
            return {'http': proxy_url, 'https': proxy_url}
    
    def load_proxies(self) -> None:
        """Load and parse proxies from file"""
        try:
            with open(self.proxy_file, 'r', encoding='utf-8') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            
            self.proxies = []
            for line in lines:
                proxy = self.parse_proxy_line(line)
                if proxy:
                    self.proxies.append(proxy)
                else:
                    print(f"Failed to parse proxy line: {line}")
                    
            print(f"Loaded {len(self.proxies)} proxies from {self.proxy_file}")
            
        except FileNotFoundError:
            print(f"Proxy file {self.proxy_file} not found")
            self.proxies = []
        except Exception as e:
            print(f"Error loading proxies: {e}")
            self.proxies = []
    
    def validate_proxies(self) -> List[Dict]:
        """Validate all loaded proxies"""
        valid_proxies = []
        for proxy in self.proxies:
            if self.checker.check_proxy(proxy):
                valid_proxies.append(proxy)
        
        self.proxies = valid_proxies
        return valid_proxies
    
    def set_rotation_interval(self, seconds: int) -> None:
        """Set proxy rotation interval in seconds"""
        self.rotation_interval = seconds
        print(f"Rotation interval set to {seconds} seconds")
    
    def get_random_proxy(self) -> Optional[Dict]:
        """Get random proxy from validated list"""
        if not self.proxies:
            return None
        
        return random.choice(self.proxies)
    
    def rotate_proxy(self) -> Optional[Dict]:
        """Perform proxy rotation"""
        self.current_proxy = self.get_random_proxy()
        
        if self.current_proxy:
            proxy_url = self.format_proxy_url(self.current_proxy)
            print(f"[{datetime.now()}] Rotated to proxy: {proxy_url}")
            return self.current_proxy
        return None
    
    def start_rotation(self) -> None:
        """Start automatic proxy rotation"""
        if self.is_rotating:
            return
            
        self.is_rotating = True
        self.rotation_thread = threading.Thread(target=self._rotation_worker, daemon=True)
        self.rotation_thread.start()
        print("Proxy rotation started")
    
    def stop_rotation(self) -> None:
        """Stop automatic proxy rotation"""
        self.is_rotating = False
        if self.rotation_thread:
            self.rotation_thread.join(timeout=2)
        print("Proxy rotation stopped")
    
    def _rotation_worker(self) -> None:
        """Background worker for proxy rotation"""
        while self.is_rotating:
            self.rotate_proxy()
            time.sleep(self.rotation_interval)
    
    def get_current_proxy(self) -> Optional[Dict]:
        """Get current active proxy"""
        return self.current_proxy
    
    def get_proxy_count(self) -> int:
        """Get number of loaded proxies"""
        return len(self.proxies)
    
    def get_proxies_by_protocol(self, protocol: str) -> List[Dict]:
        """Get proxies filtered by protocol"""
        return [p for p in self.proxies if p.get('protocol') == protocol]
    
    def add_proxy(self, proxy_data: Dict) -> bool:
        """Add a new proxy to the list"""
        try:
            self.proxies.append(proxy_data)
            
            # Append to file
            with open(self.proxy_file, 'a', encoding='utf-8') as f:
                f.write(f"\n{proxy_data['raw_line']}")
            
            return True
        except Exception as e:
            print(f"Error adding proxy: {e}")
            return False