"""
Locust load testing file for infra-autofix-agent API
Run with: locust -f locustfile.py --host http://localhost:5000
"""

from locust import HttpUser, task, between


class APIUser(HttpUser):
    """Simulates a user making requests to the API"""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    @task(3)
    def get_health(self):
        """Health check endpoint - most common"""
        self.client.get("/health")
    
    @task(2)
    def get_incidents(self):
        """Get incidents list"""
        self.client.get("/api/incidents")
    
    @task(2)
    def get_metrics(self):
        """Get current metrics"""
        self.client.get("/api/metrics")
    
    @task(1)
    def get_remediation_history(self):
        """Get remediation history"""
        self.client.get("/api/remediation/history")
    
    @task(1)
    def get_prometheus_metrics(self):
        """Get Prometheus metrics"""
        self.client.get("/metrics")
    
    def on_start(self):
        """Called when a simulated user starts"""
        # Could add authentication or setup here
        pass
