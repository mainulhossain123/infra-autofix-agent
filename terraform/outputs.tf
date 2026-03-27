output "elastic_ip" {
  description = "Permanent public IP address of the server"
  value       = aws_eip.main.public_ip
}

output "dashboard_url" {
  description = "React dashboard — share this URL with people"
  value       = "http://${aws_eip.main.public_ip}:3000"
}

output "api_url" {
  description = "Flask API base URL"
  value       = "http://${aws_eip.main.public_ip}:5000"
}

output "api_health_url" {
  description = "Health check endpoint — should return {status: healthy}"
  value       = "http://${aws_eip.main.public_ip}:5000/health"
}

output "grafana_url" {
  description = "Grafana dashboard (login: admin / your GRAFANA_PASSWORD)"
  value       = "http://${aws_eip.main.public_ip}:3001"
}

output "prometheus_url" {
  description = "Prometheus metrics explorer"
  value       = "http://${aws_eip.main.public_ip}:9090"
}

output "ssh_command" {
  description = "SSH command to connect to the server (replace path to .pem)"
  value       = "ssh -i ~/infra-autofix-key.pem ubuntu@${aws_eip.main.public_ip}"
}

output "setup_log_command" {
  description = "Command to watch the first-boot setup progress via SSH"
  value       = "ssh -i ~/infra-autofix-key.pem ubuntu@${aws_eip.main.public_ip} 'tail -f /var/log/infra-autofix-setup.log'"
}
