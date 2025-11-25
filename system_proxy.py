import winreg
import ctypes
import subprocess
from typing import Optional, Dict
import urllib.parse

class WindowsSystemProxy:
    def __init__(self):
        self.reg_path = r"Software\Microsoft\Windows\CurrentVersion\Internet Settings"
    
    def enable_system_proxy(self, proxy_data: Dict) -> bool:
        """
        Enable system-wide proxy in Windows with protocol support
        Returns: bool - Success status
        """
        try:
            protocol = proxy_data.get('protocol', 'http')
            ip = proxy_data['ip']
            port = proxy_data['port']
            username = proxy_data.get('username')
            password = proxy_data.get('password')
            
            # Format proxy server string
            proxy_server = f"{ip}:{port}"
            
            # Set registry values
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 1)
                winreg.SetValueEx(key, "ProxyServer", 0, winreg.REG_SZ, proxy_server)
                winreg.SetValueEx(key, "ProxyOverride", 0, winreg.REG_SZ, "<local>")
                
                # Store proxy credentials if available
                if username and password:
                    encoded_auth = self._encode_credentials(username, password)
                    winreg.SetValueEx(key, "ProxyAuth", 0, winreg.REG_SZ, encoded_auth)
            
            # Refresh system settings
            self._refresh_system_proxy()
            
            # Set up authenticated proxy if credentials provided
            if username and password:
                self._set_proxy_credentials(ip, port, username, password)
            
            print(f"System proxy enabled: {protocol}://{proxy_server}")
            return True
            
        except Exception as e:
            print(f"Error enabling system proxy: {e}")
            return False
    
    def _encode_credentials(self, username: str, password: str) -> str:
        """Encode credentials for storage"""
        import base64
        credentials = f"{username}:{password}"
        return base64.b64encode(credentials.encode()).decode()
    
    def _decode_credentials(self, encoded: str) -> tuple:
        """Decode stored credentials"""
        import base64
        try:
            decoded = base64.b64decode(encoded.encode()).decode()
            return decoded.split(':', 1)
        except:
            return None, None
    
    def _set_proxy_credentials(self, ip: str, port: str, username: str, password: str) -> bool:
        """Set proxy credentials using netsh"""
        try:
            # This is a simplified approach - Windows proxy auth is complex
            cmd = [
                'netsh', 'winhttp', 'set', 'proxy',
                f'{ip}:{port}',
                f'bypass-list="<local>"'
            ]
            
            subprocess.run(cmd, capture_output=True, shell=True)
            return True
        except Exception as e:
            print(f"Error setting proxy credentials: {e}")
            return False
    
    def disable_system_proxy(self) -> bool:
        """
        Disable system-wide proxy in Windows
        Returns: bool - Success status
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_WRITE) as key:
                winreg.SetValueEx(key, "ProxyEnable", 0, winreg.REG_DWORD, 0)
            
            self._refresh_system_proxy()
            print("System proxy disabled")
            return True
            
        except Exception as e:
            print(f"Error disabling system proxy: {e}")
            return False
    
    def get_current_proxy(self) -> Optional[Dict]:
        """
        Get current system proxy settings
        Returns: Dict with proxy info or None
        """
        try:
            with winreg.OpenKey(winreg.HKEY_CURRENT_USER, self.reg_path, 0, winreg.KEY_READ) as key:
                try:
                    enabled = winreg.QueryValueEx(key, "ProxyEnable")[0]
                    if enabled:
                        server = winreg.QueryValueEx(key, "ProxyServer")[0]
                        
                        # Try to get credentials
                        username, password = None, None
                        try:
                            encoded_auth = winreg.QueryValueEx(key, "ProxyAuth")[0]
                            username, password = self._decode_credentials(encoded_auth)
                        except FileNotFoundError:
                            pass
                        
                        return {
                            'enabled': True,
                            'server': server,
                            'username': username,
                            'password': password,
                            'override': winreg.QueryValueEx(key, "ProxyOverride")[0] if winreg.QueryValueEx(key, "ProxyOverride") else '<local>'
                        }
                except FileNotFoundError:
                    pass
                    
            return {'enabled': False, 'server': None, 'username': None, 'password': None, 'override': None}
            
        except Exception as e:
            print(f"Error reading proxy settings: {e}")
            return None
    
    def _refresh_system_proxy(self) -> None:
        """
        Refresh system proxy settings using WinINet
        """
        try:
            internet_set_option = ctypes.windll.Wininet.InternetSetOptionW
            internet_set_option(0, 39, 0, 0)  # INTERNET_OPTION_SETTINGS_CHANGED
            internet_set_option(0, 37, 0, 0)  # INTERNET_OPTION_REFRESH
            
            # Additional refresh using netsh
            subprocess.run(['netsh', 'winhttp', 'import', 'proxy', 'source=ie'], 
                         capture_output=True, shell=True)
                         
        except Exception as e:
            print(f"Error refreshing proxy: {e}")