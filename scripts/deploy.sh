#!/bin/bash
# Deployment script for device-metrics

set -e

ENVIRONMENT=${1:-development}
NAMESPACE="device-metrics"

echo "Deploying Device Metrics to ${ENVIRONMENT}..."

case $ENVIRONMENT in
  local)
    echo "Starting local deployment with Docker Compose..."
    docker-compose up -d
    echo "Waiting for services to be ready..."
    sleep 10
    echo "Running database migrations..."
    alembic upgrade head
    echo "Local deployment complete!"
    echo "Backend: http://localhost:8000"
    echo "Frontend: http://localhost:3000"
    ;;
  
  k8s)
    echo "Deploying to Kubernetes with Helm..."
    
    # Deploy with Helm (creates namespace if needed)
    helm upgrade --install device-metrics ./helm/device-metrics \
      --namespace ${NAMESPACE} \
      --create-namespace \
      --set namespace.create=true \
      --set namespace.name=${NAMESPACE}
    
    echo "Kubernetes deployment complete!"
    echo "Check status: kubectl get pods -n ${NAMESPACE}"
    ;;
  
  aws)
    echo "Deploying to AWS EKS..."
    cd cloud/aws/terraform
    terraform apply -auto-approve
    cd ../..
    
    # Get cluster name from terraform output
    CLUSTER_NAME=$(terraform -chdir=cloud/aws/terraform output -raw eks_cluster_name)
    aws eks update-kubeconfig --name ${CLUSTER_NAME}
    
    helm upgrade --install device-metrics ./helm/device-metrics \
      --namespace ${NAMESPACE} \
      --create-namespace \
      --set config.env.DATABASE_URL=$(terraform -chdir=cloud/aws/terraform output -raw rds_endpoint) \
      --set config.env.KAFKA_BOOTSTRAP_SERVERS=$(terraform -chdir=cloud/aws/terraform output -raw kafka_brokers)
    ;;
  
  *)
    echo "Unknown environment: ${ENVIRONMENT}"
    echo "Usage: ./scripts/deploy.sh [local|k8s|aws|azure|gcp]"
    exit 1
    ;;
esac

