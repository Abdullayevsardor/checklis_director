╔════════════════════════════════════════════════════════════════════════════════╗
║           🔍 WebAuthn Error Troubleshooting Guide                              ║
║  "The operation either timed out or was not allowed..."                       ║
╚════════════════════════════════════════════════════════════════════════════════╝

🔴 ERROR MESSAGE:
The operation either timed out or was not allowed. See: 
https://www.w3.org/TR/webauthn-2/#sctn-privacy-considerations-client

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✅ MOST COMMON CAUSES & SOLUTIONS:

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

1️⃣  RP_ID MISMATCH (MOST LIKELY!)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem:
  • Frontend uses: window.location.hostname = "127.0.0.1"
  • Backend expects: RP_ID = "localhost"
  • MISMATCH! ❌

Solution:
  Option A (RECOMMENDED for development):
    1. Access app via http://localhost:5173 (NOT http://127.0.0.1:5173)
    2. In /etc/hosts (Mac/Linux) or C:\Windows\System32\drivers\etc\hosts (Windows):
       127.0.0.1 localhost
    3. Confirm: ping localhost → should resolve to 127.0.0.1
    4. Access browser: http://localhost:5173

  Option B (Set environment variables):
    # If you must use 127.0.0.1:
    export RP_ID="127.0.0.1"
    export ORIGIN="http://127.0.0.1:5173"
    
    Then restart backend server

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

2️⃣  ORIGIN MISMATCH
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem:
  • Frontend origin: window.location.origin = "http://localhost:5173"
  • Backend ORIGIN env var mismatch

Check:
  1. Frontend URL in browser: http://localhost:5173 ✓
  2. Backend config: echo $ORIGIN
  3. Should match exactly!

Solution:
  In .env or environment:
    ORIGIN="http://localhost:5173"
    RP_ID="localhost"

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

3️⃣  NO PLATFORM AUTHENTICATOR AVAILABLE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem:
  • Device doesn't have Face ID / fingerprint scanner
  • Testing on desktop without biometric sensors

Solution:
  ✓ Mac with Touch ID: Works natively
  ✓ Windows 10+ with Hello: Works natively
  ✓ Android with fingerprint/face: Works with latest Chrome
  ✓ iPhone with Face ID: Works natively
  
  For testing on Desktop WITHOUT biometric:
    • Use Chrome DevTools emulation
    • Or use virtual authenticator for testing

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

4️⃣  HTTP vs HTTPS ISSUE
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem:
  • WebAuthn only works on HTTPS in production
  • HTTP is only allowed for localhost/127.0.0.1

Check:
  ✓ Localhost development: http://localhost:5173 (OK)
  ✓ Production: https://yourdomain.com (REQUIRED)
  ✓ Staging: HTTPS only (required even for staging)

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

5️⃣  BROWSER PRIVACY / PERMISSIONS
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Problem:
  • Browser blocks biometric access
  • Permission denied for device

Solution:
  Chrome/Edge:
    1. Open Settings > Privacy and security > Site settings > Additional permissions
    2. Search for "WebAuthn"
    3. Add localhost:5173 to allowed sites

  Safari (Mac):
    1. System Preferences > Security & Privacy
    2. Allow Safari access to authentication devices

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🔧 DEBUGGING STEPS:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Step 1: Open Browser Console
  F12 or Cmd+Option+J

Step 2: Run test
  Copy & paste:
    import("/src/utils/faceIdDebug.js").then(() => {
      window.testFaceIdSetup();
    });

Step 3: Check output:
  🟢 All GREEN ✓ → Issue is likely device-specific
  🔴 Any RED ✗ → Check that specific item

Step 4: Specific checks:
  In console, paste:
    
    // Check hostname
    console.log("Hostname:", window.location.hostname);
    
    // Check Origin  
    console.log("Origin:", window.location.origin);
    
    // Check WebAuthn support
    console.log("WebAuthn supported:", !!window.PublicKeyCredential);
    
    // Check platform authenticator
    PublicKeyCredential.isUserVerifyingPlatformAuthenticatorAvailable()
      .then(available => {
        console.log("Platform auth available:", available);
      });

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

📝 CHECKLIST:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

✓ Frontend URL: http://localhost:5173 (NOT 127.0.0.1)
✓ Backend RP_ID: "localhost"
✓ Backend ORIGIN: "http://localhost:5173"
✓ Device has biometric (Face ID / fingerprint)
✓ Browser allows WebAuthn
✓ Admin user created (Sardor/Anton/Asliddin)
✓ Admin Face ID is allowed: face_id_allowed = True
✓ No certificate/CORS issues

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🎯 QUICK FIXES:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

If on localhost and still getting error:

1. Restart frontend server:
   cd checklist-frontend
   npm run dev

2. Restart backend server:
   python -m uvicorn app.main:app --reload

3. Clear browser cache:
   Ctrl+Shift+Delete (Select "All time")

4. Verify hostname in browser:
   In console: window.location.hostname
   Should return: "localhost" (not "127.0.0.1")

5. Test with different device:
   - Desktop/Laptop with TouchID/Windows Hello
   - iPhone with Face ID
   - Android with fingerprint

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

🆘 IF STILL NOT WORKING:

1. Check backend logs:
   Look for: [WebAuthn Config] messages in terminal
   
2. Enable verbose logging:
   In app/modules/auth/service.py - already has debug prints

3. Test with curl:
   curl -X POST http://localhost:8000/auth/face-id/challenge

4. Check if admin exists:
   In Python terminal:
     python check_admins.py

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
