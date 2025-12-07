# GCP Infrastructure for Device Metrics Service
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
  }
}

provider "google" {
  project = var.gcp_project_id
  region  = var.gcp_region
}

# GKE Cluster
resource "google_container_cluster" "device_metrics" {
  name     = "device-metrics-gke"
  location = var.gcp_region

  remove_default_node_pool = true
  initial_node_count       = 1

  network    = google_compute_network.main.name
  subnetwork = google_compute_subnetwork.main.name

  master_auth {
    client_certificate_config {
      issue_client_certificate = false
    }
  }
}

resource "google_container_node_pool" "primary" {
  name       = "device-metrics-node-pool"
  location   = var.gcp_region
  cluster    = google_container_cluster.device_metrics.name
  node_count = 3

  node_config {
    preemptible  = false
    machine_type = "e2-standard-4"
    disk_size_gb = 100

    oauth_scopes = [
      "https://www.googleapis.com/auth/cloud-platform"
    ]
  }
}

# Cloud SQL PostgreSQL
resource "google_sql_database_instance" "postgres" {
  name             = "device-metrics-postgres"
  database_version = "POSTGRES_15"
  region           = var.gcp_region

  settings {
    tier              = "db-f1-micro"
    availability_type = "ZONAL"
    disk_size         = 100
    disk_type         = "PD_SSD"

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
    }

    ip_configuration {
      ipv4_enabled = false
      private_network = google_compute_network.main.id
    }
  }

  deletion_protection = false
}

resource "google_sql_database" "device_metrics" {
  name     = "device_metrics"
  instance = google_sql_database_instance.postgres.name
}

# Pub/Sub (Kafka alternative)
resource "google_pubsub_topic" "device_metrics" {
  name = "device-metrics"
}

resource "google_pubsub_subscription" "device_metrics" {
  name  = "device-metrics-consumer"
  topic = google_pubsub_topic.device_metrics.name

  ack_deadline_seconds = 20
  message_retention_duration = "604800s" # 7 days
}

# Cloud Storage for Metric Archives
resource "google_storage_bucket" "metrics_archive" {
  name          = "${var.project_name}-metrics-archive"
  location      = var.gcp_region
  force_destroy = false

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = 365
    }
    action {
      type = "Delete"
    }
  }
}

# Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "device-metrics-db-password"

  replication {
    automatic = true
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = var.db_password
}

# VPC Network
resource "google_compute_network" "main" {
  name                    = "device-metrics-network"
  auto_create_subnetworks = false
}

resource "google_compute_subnetwork" "main" {
  name          = "device-metrics-subnet"
  ip_cidr_range = "10.0.0.0/24"
  region        = var.gcp_region
  network       = google_compute_network.main.id
}

