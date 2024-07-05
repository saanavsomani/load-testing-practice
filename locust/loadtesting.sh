# locust -f locust.py --host http://localhost:8000 --users 100 --spawn-rate 5
#!/bin/sh
locust -f locust.py --host http://fastapi:8000 --users 100 --spawn-rate 5 --headless -t 3m
