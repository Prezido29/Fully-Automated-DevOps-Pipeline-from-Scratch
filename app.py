from flask import Flask
import time

app = Flask(__name__)


@app.route("/")
def get_current_time():
    current_time = time.strftime("%H:%M:%S", time.localtime())
    return f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Complete DevOps Project</title>
<style>
  * {{ margin: 0; padding: 0; box-sizing: border-box; }}
  body {{
    background: #000000;
    color: #ffffff;
    font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
    height: 100vh;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    text-align: center;
  }}
  .welcome {{
    font-size: 22px;
    font-weight: 400;
    letter-spacing: 4px;
    text-transform: uppercase;
    color: #66e0ff;
    text-shadow: 0 0 8px rgba(102,224,255,0.6), 0 0 20px rgba(102,224,255,0.4);
    margin-bottom: 2.5rem;
    opacity: 0.9;
  }}
  .clock {{
    font-size: 88px;
    font-weight: 700;
    letter-spacing: 2px;
    color: #ffffff;
    text-shadow:
      0 0 10px rgba(102,224,255,0.9),
      0 0 25px rgba(102,224,255,0.7),
      0 0 55px rgba(102,224,255,0.5),
      0 0 90px rgba(102,224,255,0.3);
    line-height: 1.1;
  }}
  .label {{
    margin-top: 1.5rem;
    font-size: 15px;
    font-weight: 400;
    color: #7a8a94;
    letter-spacing: 2px;
    text-transform: uppercase;
  }}
</style>
</head>
<body>
  <div class="welcome">Welcome, sir Sire</div>
  <div class="clock" id="clock">{current_time}</div>
  <div class="label">Live from EC2 + k8s-snap</div>

  <script>
    function tick() {{
      const el = document.getElementById('clock');
      const parts = el.textContent.split(':').map(Number);
      let [h, m, s] = parts;
      s += 1;
      if (s >= 60) {{ s = 0; m += 1; }}
      if (m >= 60) {{ m = 0; h += 1; }}
      if (h >= 24) {{ h = 0; }}
      const pad = n => String(n).padStart(2, '0');
      el.textContent = `${{pad(h)}}:${{pad(m)}}:${{pad(s)}}`;
    }}
    setInterval(tick, 1000);
  </script>
</body>
</html>"""


@app.route("/health")
def health():
    return "ok", 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080)