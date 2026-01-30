import os
import subprocess
import sys

def setup_final_agent():
    # 1. DETECT NEW PATHS
    project_path = os.getcwd()  # Should be /Users/allen/Projects/ai-news-analyst
    python_exec = os.path.join(project_path, ".venv", "bin", "python")
    script_path = os.path.join(project_path, "sentinel.py")
    
    # Verify Python exists
    if not os.path.exists(python_exec):
        print(f"❌ Error: Python not found at {python_exec}")
        print("Did you run Step 2 (Rebuild venv)?")
        return

    # 2. DEFINE PLIST CONTENT
    plist_content = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.foodie.sentinel</string>
    
    <key>WorkingDirectory</key>
    <string>{project_path}</string>

    <key>ProgramArguments</key>
    <array>
        <string>{python_exec}</string>
        <string>{script_path}</string>
    </array>

    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>19</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>

    <key>StandardOutPath</key>
    <string>{project_path}/logs/launchd.log</string>
    <key>StandardErrorPath</key>
    <string>{project_path}/logs/launchd_error.log</string>
</dict>
</plist>
"""

    # 3. WRITE TO SYSTEM LIBRARY
    plist_path = os.path.expanduser("~/Library/LaunchAgents/com.foodie.sentinel.plist")
    with open(plist_path, "w") as f:
        f.write(plist_content)
    print(f"✅ Configuration written to: {plist_path}")

    # 4. LOAD SERVICE
    # Unload old instances first (ignore errors)
    subprocess.run(["launchctl", "bootout", f"gui/{os.getuid()}/com.foodie.sentinel"], capture_output=True)
    
    # Load new instance
    result = subprocess.run(["launchctl", "bootstrap", f"gui/{os.getuid()}", plist_path], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Service successfully registered!")
    else:
        print(f"⚠️  Load Warning: {result.stderr}")

    # 5. INSTANT TEST
    print("🚀 Triggering Test Run...")
    subprocess.run(["launchctl", "kickstart", "-k", f"gui/{os.getuid()}/com.foodie.sentinel"])
    print("✅ Check logs/launchd.log in 5 seconds.")

if __name__ == "__main__":
    setup_final_agent()