import time, random
from locust import HttpUser, TaskSet, task, between

class UserBehavior(TaskSet):
    names = ["Alice", "Bob", "Charlie", "Diana", "Eve"]

    @task
    def home_page(self):
        self.client.get("/home")

    @task
    def meet_page(self):
        name = random.choice(["Alice", "Bob", "Charlie", "Diana", "Eve"])
        self.client.get(f"/meet/{name}")

# User agent that can visit different end points
class WebAppUser(HttpUser):
    tasks = [UserBehavior]
    wait_time = between(1, 5)

