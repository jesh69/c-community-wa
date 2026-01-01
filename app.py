from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import subprocess
import re

app = Flask(__name__)

def run_c_safely(code: str, timeout=1.5) -> str:
    if re.search(r'\b(system|exec|fork|socket|popen|bash|sh)\b', code):
        return "❌ Blocked: Dangerous system call."

    if "main(" not in code:
        return "❌ Error: main() function missing."

    try:
        proc = subprocess.Popen(
            ['tcc', '-run', '-'],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )

        try:
            stdout, stderr = proc.communicate(input=code, timeout=timeout)
            if proc.returncode == 0:
                if len(stdout) > 1500:
                    return stdout[:1500] + "\n...output truncated"
                return stdout.strip() or "(no output)"
            else:
                return f"❌ Compile Error:\n{stderr.strip()}"
        except subprocess.TimeoutExpired:
            proc.kill()
            return "⏱️ Timeout (possible infinite loop)"

    except Exception as e:
        return f"⚠️ Error: {str(e)}"

@app.route('/whatsapp', methods=['POST'])
def whatsapp():
    msg = request.values.get('Body', '').strip()
    resp = MessagingResponse()

    if msg.startswith('///c'):
        code = msg[4:].strip()
        output = run_c_safely(code)
        resp.message(f"🟢 C Output:\n{output}")
    else:
        resp.message("Send C code like:\n///c #include<stdio.h>\nint main(){printf(\"Hi\");}")

    return str(resp)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000)
