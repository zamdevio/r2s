"""Proxy service for React2Shell."""

import random
from typing import Optional, List, Dict
from urllib.parse import urlparse


class ProxyManager:
    """Manage proxy rotation and configuration."""
    
    def __init__(self, proxy: Optional[str] = None, proxy_file: Optional[str] = None):
        self.proxies: List[str] = []
        self.current_index = 0
        
        if proxy:
            self.proxies.append(proxy)
        
        if proxy_file:
            self.load_from_file(proxy_file)
    
    def load_from_file(self, filename: str):
        """Load proxies from file."""
        try:
            with open(filename, 'r') as f:
                for line in f:
                    proxy = line.strip()
                    if proxy and not proxy.startswith('#'):
                        self.proxies.append(proxy)
        except Exception:
            pass
    
    def get_proxy(self, rotate: bool = False) -> Optional[Dict[str, str]]:
        """Get current proxy or rotate to next."""
        if not self.proxies:
            return None
        
        if rotate:
            self.current_index = (self.current_index + 1) % len(self.proxies)
        elif len(self.proxies) > 1:
            # Random selection
            self.current_index = random.randint(0, len(self.proxies) - 1)
        
        proxy_url = self.proxies[self.current_index]
        
        # Parse proxy URL
        parsed = urlparse(proxy_url)
        if parsed.scheme in ['http', 'https']:
            return {
                'http': proxy_url,
                'https': proxy_url
            }
        return None
    
    def add_proxy(self, proxy: str):
        """Add a proxy to the list."""
        if proxy not in self.proxies:
            self.proxies.append(proxy)
    
    def remove_proxy(self, proxy: str):
        """Remove a proxy from the list."""
        if proxy in self.proxies:
            self.proxies.remove(proxy)

