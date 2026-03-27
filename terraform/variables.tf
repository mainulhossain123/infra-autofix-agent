variable "aws_region" {
  description = "AWS region to deploy into"
  type        = string
  default     = "ap-southeast-1"
}

variable "instance_type" {
  description = "EC2 instance type — t2.micro is AWS free tier (1 vCPU, 1 GB RAM)"
  type        = string
  default     = "t2.micro"
}

variable "key_pair_name" {
  description = "Name of the EC2 Key Pair you created manually in Step 2"
  type        = string
  default     = "infra-autofix-key"
}

variable "groq_api_key" {
  description = "Groq API key for AI chat (get free key at https://console.groq.com)"
  type        = string
  sensitive   = true
}

variable "postgres_password" {
  description = "PostgreSQL database password — use a strong random string"
  type        = string
  sensitive   = true
}

variable "grafana_password" {
  description = "Grafana admin panel password"
  type        = string
  sensitive   = true
}
