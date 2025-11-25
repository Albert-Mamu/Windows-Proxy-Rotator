import requests
import concurrent.futures
from typing import List, Dict
import time
import socks
import socket

class ProxyChecker:
    def __init__(self, timeout: int = 15):
        self.timeout = timeout
        self.test_urls = [
            "http://httpbin.org/ip",
            "http://api.ipify.org",
            "http://icanhazip.com"
        ]
    
    def check_proxy(self, proxy_data: Dict) -> bool:
        """
        Check if proxy is working with authentication support
        Returns: bool - True if proxy is valid
        """
        try:
            proxy_url = self._format_proxy_url(proxy_data)
            protocol = proxy_data.get('protocol', 'http')
            
            # Prepare proxies dict for requests
            proxies = self._prepare_proxies_dict(proxy_data)
            
            start_time = time.time()
            
            if protocol.startswith('socks'):
                # Test SOCKS proxy with socket
                result = self._test_socks_proxy(proxy_data)
            else:
                # Test HTTP/HTTPS proxy with requests
                result = self._test_http_proxy(proxies)
            
            response_time = time.time() - start_time
            
            if result:
                print(f"✓ Proxy {proxy_url} valid - Response time: {response_time:.2f}s")
                return True
            else:
                print(f"✗ Proxy {proxy_url} failed")
                return False
                
        except Exception as e:
            print(f"✗ Proxy {proxy_url} error: {str(e)}")
            return False
    
    def _format_proxy_url(self, proxy_data: Dict) -> str:
        """Format proxy URL for display"""
        protocol = proxy_data.get('protocol', 'http')
        ip = proxy_data['ip']
        port = proxy_data['port']
        username = proxy_data.get('username')
        
        if username:
            return f"{protocol}://{username}:***@{ip}:{port}"
        else:
            return f"{protocol}://{ip}:{port}"
    
    def _prepare_proxies_dict(self, proxy_data: Dict) -> Dict[str, str]:
        """Prepare proxies dictionary for requests"""
        protocol = proxy_data.get('protocol', 'http')
        ip = proxy_data['ip']
        port = proxy_data['port']
        username = proxy_data.get('username')
        password = proxy_data.get('password')
        
        if username and password:
            auth_part = f"{username}:{password}@"
        elif username:
            auth_part = f"{username}@"
        else:
            auth_part = ""
        
        base_url = f"{auth_part}{ip}:{port}"
        
        if protocol == 'http':
            return {
                'http': f"http://{base_url}",
                'https': f"http://{base_url}"
            }
        elif protocol == 'https':
            return {
                'http': f"https://{base_url}",
                'https': f"https://{base_url}"
            }
        elif protocol == 'socks4':
            return {
                'http': f"socks4://{base_url}",
                'https': f"socks4://{base_url}"
            }
        elif protocol == 'socks5':
            return {
                'http': f"socks5://{base_url}",
                'https': f"socks5://{base_url}"
            }
        else:
            return {'http': f"http://{base_url}", 'https': f"http://{base_url}"}
    
    def _test_http_proxy(self, proxies: Dict) -> bool:
        """Test HTTP/HTTPS proxy"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            
            for test_url in self.test_urls:
                try:
                    response = requests.get(
                        test_url, 
                        proxies=proxies, 
                        timeout=self.timeout,
                        headers=headers
                    )
                    
                    if response.status_code == 200:
                        # Verify we're actually using the proxy by checking IP
                        if 'origin' in response.json():
                            return True
                except:
                    continue
            
            return False
            
        except Exception:
            return False
    
    def _test_socks_proxy(self, proxy_data: Dict) -> bool:
        """Test SOCKS proxy using socket"""
        try:
            ip = proxy_data['ip']
            port = int(proxy_data['port'])
            protocol = proxy_data.get('protocol', 'socks5')
            username = proxy_data.get('username')
            password = proxy_data.get('password')
            
            # Set SOCKS proxy
            if protocol == 'socks4':
                socks_type = socks.SOCKS4
            elif protocol == 'socks5':
                socks_type = socks.SOCKS5
            else:
                socks_type = socks.SOCKS5
            
            # Create SOCKS socket
            socks.set_default_proxy(
                socks_type,
                ip,
                port,
                username=username,
                password=password
            )
            socket.socket = socks.socksocket
            
            # Test connection
            test_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            test_socket.settimeout(self.timeout)
            test_socket.connect(('httpbin.org', 80))
            test_socket.close()
            
            # Reset socket to default
            socks.set_default_proxy()
            socket.socket = socket._socketobject
            
            return True
            
        except Exception as e:
            # Reset socket to default on error
            socks.set_default_proxy()
            socket.socket = socket._socketobject
            return False
    
    def check_proxy_batch(self, proxy_list: List[Dict], max_workers: int = 10) -> List[Dict]:
        """
        Check multiple proxies concurrently
        Returns: List of valid proxies
        """
        valid_proxies = []
        
        with concurrent.futures.ThreadPoolExecutor(max_workers=max_workers) as executor:
            future_to_proxy = {
                executor.submit(self.check_proxy, proxy): proxy 
                for proxy in proxy_list
            }
            
            for future in concurrent.futures.as_completed(future_to_proxy):
                proxy = future_to_proxy[future]
                try:
                    if future.result():
                        valid_proxies.append(proxy)
                except Exception as e:
                    print(f"Error checking proxy {proxy}: {e}")
        
        print(f"Validation complete: {len(valid_proxies)}/{len(proxy_list)} proxies valid")
        return valid_proxies
    
    def get_proxy_info(self, proxy_data: Dict) -> Dict:
        """
        Get detailed information about proxy
        """
        info = {
            'url': self._format_proxy_url(proxy_data),
            'valid': False,
            'response_time': None,
            'protocol': proxy_data.get('protocol', 'http'),
            'anonymity': None,
            'country': None
        }
        
        if self.check_proxy(proxy_data):
            info['valid'] = True
            
            try:
                proxies = self._prepare_proxies_dict(proxy_data)
                start_time = time.time()
                response = requests.get(
                    "http://httpbin.org/ip", 
                    proxies=proxies, 
                    timeout=self.timeout
                )
                info['response_time'] = time.time() - start_time
                
                # Check anonymity
                if 'origin' in response.json():
                    headers = response.headers
                    if 'via' in headers or 'x-forwarded-for' in headers:
                        info['anonymity'] = 'transparent'
                    else:
                        info['anonymity'] = 'anonymous'
                        
            except Exception as e:
                print(f"Error getting proxy info: {e}")
        
        return info