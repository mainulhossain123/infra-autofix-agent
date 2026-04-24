# No Elastic IP — DuckDNS provides the stable hostname (infra-autofix.duckdns.org)
# The EC2 public IP below is dynamic and changes on instance stop/start.
# The DuckDNS cron job (installed by deploy-app.yml) keeps the hostname up to date.

output "instance_public_ip" {
  description = "Current EC2 public IP (dynamic - use DuckDNS hostname instead)"
  value       = aws_instance.main.public_ip
}

output "dashboard_url" {
  description = "React dashboard - stable URL via DuckDNS"
  value       = "http://infra-autofix.duckdns.org"
}

output "api_url" {
  description = "Flask API base URL"
  value       = "http://infra-autofix.duckdns.org:5000"
}

output "api_health_url" {
  description = "Health check endpoint - should return {status: healthy}"
  value       = "http://infra-autofix.duckdns.org:5000/health"
}

output "grafana_url" {
  description = "Grafana dashboard (login: admin / your GRAFANA_PASSWORD)"
  value       = "http://infra-autofix.duckdns.org:3001"
}

output "prometheus_url" {
  description = "Prometheus metrics explorer"
  value       = "http://infra-autofix.duckdns.org:9090"
}

output "ssh_command" {
  description = "SSH command to connect to the server (replace path to .pem)"
  value       = "ssh -i ~/infra-autofix-key.pem ubuntu@${aws_instance.main.public_ip}"
}

output "setup_log_command" {
  description = "Command to watch the first-boot setup progress via SSH"
  value       = "ssh -i ~/infra-autofix-key.pem ubuntu@${aws_instance.main.public_ip} 'tail -f /var/log/infra-autofix-setup.log'"
}
