from locust import HttpUser, task

class HelloWorldUser(HttpUser):
    @task 
    def hello_world(self):
        self.client.get("/api/get_cookies")
        self.client.get("/api/history_data")
