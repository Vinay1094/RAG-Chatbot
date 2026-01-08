import subprocess
import time
import os
import requests


def wait_for_url(url, timeout=30.0):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(url, timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            time.sleep(0.5)
    return False


def test_gradio_integration():
    port = 7865
    env = os.environ.copy()
    env["GRADIO_PORT"] = str(port)

    p = subprocess.Popen([env.get("PYTHON", "python"), "-u", "app.py"], env=env)
    try:
        url = f"http://127.0.0.1:{port}"
        assert wait_for_url(url), "Gradio server did not start in time"

        # call the predict endpoint
        predict_url = url + "/api/predict"
        q = "How many holdings does Garfield have?"
        r = requests.post(predict_url, json={"data": [q]}, timeout=10)
        assert r.status_code == 200
        j = r.json()
        # response text usually available in j['data'][0]
        assert any("Garfield" in str(x) for x in j.get("data", [])) or "221" in str(j), f"Unexpected response: {j}"
    finally:
        p.terminate()
        try:
            p.wait(timeout=5)
        except Exception:
            p.kill()
