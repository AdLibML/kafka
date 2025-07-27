#!/usr/bin/env bash
set -e

echo "Starting Kubernetes port-forwarding..."

# Kill any existing kubectl port-forward processes
pkill -f "kubectl.*port-forward" || true

# Start port forwarding for all services
kubectl port-forward svc/order-api 32000:8000 &
kubectl port-forward svc/processor-api 32001:8001 &
kubectl port-forward svc/kafka-ui 32002:8080 &
kubectl -n portainer port-forward svc/portainer 32003:9000 &
kubectl -n kubernetes-dashboard port-forward svc/kubernetes-dashboard 32004:443 &

echo "Port forwarding started:"
echo "  Order API       → http://localhost:32000"
echo "  Processor API   → http://localhost:32001" 
echo "  Kafka UI        → http://localhost:32002"
echo "  Portainer       → http://localhost:32003"
echo "  Dashboard       → https://localhost:32004  (accept cert warning)"
echo ""
echo "Press Ctrl+C to stop all port forwarding"

# Function to cleanup on exit
cleanup() {
    echo "Stopping port forwarding..."
    pkill -f "kubectl.*port-forward" || true
    exit 0
}

trap cleanup SIGINT SIGTERM

# Wait for all background processes
wait