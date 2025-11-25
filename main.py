#!/usr/bin/env python3
"""
AlbertAI - Proxy Rotator
Advanced proxy rotation system with Windows integration
"""

import sys
import os
import argparse
from gui_app import main as gui_main
from proxy_rotator import ProxyRotator
from system_proxy import WindowsSystemProxy

def main():
    parser = argparse.ArgumentParser(description="AlbertAI Proxy Rotator")
    parser.add_argument('--gui', action='store_true', help='Launch GUI interface')
    parser.add_argument('--rotate', action='store_true', help='Start rotation in CLI mode')
    parser.add_argument('--interval', type=int, default=300, help='Rotation interval in seconds')
    parser.add_argument('--validate', action='store_true', help='Validate proxies before starting')
    
    args = parser.parse_args()
    
    if args.gui:
        print("Launching AlbertAI Proxy Rotator GUI...")
        gui_main()
    else:
        # CLI mode
        rotator = ProxyRotator()
        system_proxy = WindowsSystemProxy()
        
        if args.validate:
            print("Validating proxies...")
            valid_proxies = rotator.validate_proxies()
            print(f"Found {len(valid_proxies)} valid proxies")
        
        if args.rotate:
            print(f"Starting proxy rotation with {args.interval} second interval...")
            rotator.set_rotation_interval(args.interval)
            rotator.start_rotation()
            
            try:
                while True:
                    input("Press Enter to stop rotation...\n")
                    break
            except KeyboardInterrupt:
                pass
            finally:
                rotator.stop_rotation()
                system_proxy.disable_system_proxy()
                print("Rotation stopped and system proxy disabled")

if __name__ == "__main__":
    main()