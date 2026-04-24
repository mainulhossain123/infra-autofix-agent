terraform {
  required_version = ">= 1.6"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }

  # S3 backend — keeps Terraform state safe between GitHub Actions runs.
  # Bucket is passed via -backend-config in the GitHub Actions workflow
  # so you don't have to hardcode a globally-unique name here.
  backend "s3" {}
}

provider "aws" {
  region = var.aws_region
}

# ── Reference existing Key Pair (you created this in Step 2) ─────────────────
data "aws_key_pair" "main" {
  key_name = var.key_pair_name
}

# ── Default VPC — needed to create the security group in the right VPC ───────
data "aws_vpc" "default" {
  default = true
}

# ── Security Group — Terraform creates and manages this ───────────────────────
# Ports exposed to the internet:
#   22   — SSH (admin access)
#   3000 — React dashboard
#   80  — React dashboard (standard HTTP — no port number needed in URL)
#   5000 — Flask API
#   3001 — Grafana
#   9090 — Prometheus
# Internal-only (not exposed): 5432 postgres, 3100 loki, 8000 bot metrics
resource "aws_security_group" "main" {
  name        = "infra-autofix-sg"
  description = "Security group for infra-autofix-agent EC2 instance"
  vpc_id      = data.aws_vpc.default.id

  ingress {
    description = "SSH"
    from_port   = 22
    to_port     = 22
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "HTTP — React dashboard"
    from_port   = 80
    to_port     = 80
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "React dashboard (legacy port — kept for local dev compatibility)"
    from_port   = 3000
    to_port     = 3000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Flask API"
    from_port   = 5000
    to_port     = 5000
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Grafana"
    from_port   = 3001
    to_port     = 3001
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  ingress {
    description = "Prometheus"
    from_port   = 9090
    to_port     = 9090
    protocol    = "tcp"
    cidr_blocks = ["0.0.0.0/0"]
  }

  egress {
    description = "Allow all outbound traffic"
    from_port   = 0
    to_port     = 0
    protocol    = "-1"
    cidr_blocks = ["0.0.0.0/0"]
  }

  tags = {
    Name      = "infra-autofix-sg"
    ManagedBy = "terraform"
  }
}

# ── Latest Ubuntu 22.04 LTS AMI (Canonical official) ─────────────────────────
data "aws_ami" "ubuntu_22_04" {
  most_recent = true
  owners      = ["099720109477"] # Canonical

  filter {
    name   = "name"
    values = ["ubuntu/images/hvm-ssd/ubuntu-jammy-22.04-amd64-server-*"]
  }

  filter {
    name   = "virtualization-type"
    values = ["hvm"]
  }
}

# ── EC2 Instance — t2.micro (AWS free tier) ───────────────────────────────────
resource "aws_instance" "main" {
  ami                    = data.aws_ami.ubuntu_22_04.id
  instance_type          = var.instance_type
  key_name               = data.aws_key_pair.main.key_name
  vpc_security_group_ids = [aws_security_group.main.id]

  root_block_device {
    volume_size           = 20   # GB — default 8 GB is too small for Docker images
    volume_type           = "gp3"
    delete_on_termination = true
  }

  # EC2 runs this script automatically on first boot.
  # Terraform's templatefile() injects your secrets before it reaches the instance.
  user_data = base64encode(templatefile("${path.module}/user_data.sh", {
    groq_api_key      = var.groq_api_key
    postgres_password = var.postgres_password
    grafana_password  = var.grafana_password
  }))

  # user_data only runs once (on first boot). Ignore changes so subsequent
  # terraform applies don't destroy and recreate the instance.
  lifecycle {
    ignore_changes = [user_data]
  }

  tags = {
    Name        = "infra-autofix-agent"
    Environment = "production"
    ManagedBy   = "terraform"
  }
}

# ── Elastic IP — stable public address that survives stop/start cycles ────────
resource "aws_eip" "main" {
  instance   = aws_instance.main.id
  domain     = "vpc"
  depends_on = [aws_instance.main]

  tags = {
    Name      = "infra-autofix-agent-eip"
    ManagedBy = "terraform"
  }
}
