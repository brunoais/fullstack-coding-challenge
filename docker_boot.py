import subprocess


subprocess.check_call(['python', 'dbInstall.py'])

print("DB install complete. Starting server")

subprocess.check_call(["gunicorn", '--worker-class', 'eventlet', "-b", "0.0.0.0:8000", '-p', 'challenge-server', "main:app"],
                      )

