import subprocess
subprocess.Popen(f"python Math_Dragon.pyw --mode online --port {input('port: ') or 9090} --ip {input('ip: ') or 'localhost'}".split())
