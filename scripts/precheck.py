import time

print("Run Pre check")

while True:
    from django.db import connections
    from django.db.utils import OperationalError

    conn = connections["default"]
    try:
        c = conn.cursor()
        print("Pre-check: Ready")
        break
    except OperationalError:
        time.sleep(1.25)
