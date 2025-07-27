# Kafka Cluster with Docker Compose

This setup provides a complete Kafka cluster with 3 brokers, Zookeeper, and a web UI for management.

## Components

- **Zookeeper**: Coordination service for Kafka
- **Kafka Broker 1**: Port 9092 (localhost)
- **Kafka Broker 2**: Port 9093 (localhost)
- **Kafka Broker 3**: Port 9094 (localhost)
- **Kafka UI**: Port 8080 (web interface)

## Quick Start

### 1. Start the Cluster
```bash
docker-compose up -d
```

### 2. Check Status
```bash
docker-compose ps
```

### 3. View Logs
```bash
# All services
docker-compose logs -f

# Specific service
docker-compose logs -f kafka-broker-1
```

### 4. Stop the Cluster
```bash
docker-compose down
```

### 5. Stop and Remove Data
```bash
docker-compose down -v
```

## Access Points

- **Kafka UI**: http://localhost:8080
- **Kafka Bootstrap Servers**: localhost:9092,localhost:9093,localhost:9094
- **Zookeeper**: localhost:2181

## Testing the Cluster

### Using Kafka Console Tools (from inside container)

#### Create a Topic
```bash
docker exec -it kafka-broker-1 kafka-topics --create --topic test-topic --bootstrap-server localhost:9092 --partitions 3 --replication-factor 3
```

#### List Topics
```bash
docker exec -it kafka-broker-1 kafka-topics --list --bootstrap-server localhost:9092
```

#### Produce Messages
```bash
docker exec -it kafka-broker-1 kafka-console-producer --topic test-topic --bootstrap-server localhost:9092
```

#### Consume Messages
```bash
docker exec -it kafka-broker-1 kafka-console-consumer --topic test-topic --bootstrap-server localhost:9092 --from-beginning
```

### Using External Tools

You can connect to the cluster using external tools with these connection strings:
- **Bootstrap Servers**: `localhost:9092,localhost:9093,localhost:9094`

## Configuration Details

- **Replication Factor**: 3 (data is replicated across all brokers)
- **Min ISR**: 2 (minimum in-sync replicas)
- **Auto Topic Creation**: Enabled
- **Data Persistence**: Enabled with Docker volumes

## Troubleshooting

### Check if all services are running
```bash
docker-compose ps
```

### Check logs for errors
```bash
docker-compose logs kafka-broker-1
docker-compose logs zookeeper
```

### Restart a specific service
```bash
docker-compose restart kafka-broker-1
```

### Clean restart (removes all data)
```bash
docker-compose down -v
docker-compose up -d
```

## Production Considerations

For production use, consider:
1. Adding authentication and SSL/TLS
2. Tuning JVM settings
3. Configuring log retention policies
4. Setting up monitoring and alerting
5. Using external storage for persistent volumes
6. Implementing proper backup strategies

## Application Services

In addition to the Kafka cluster, this `docker-compose` starts two FastAPI services:

- **Order API**  
  • URL: http://localhost:8000  
  • Exposed port: `8000` → container `8000`  
- **Processor API**  
  • URL: http://localhost:5698  
  • Exposed port: `5698` → container `8001`

### Start everything

```bash
# From the repo root
docker-compose up -d
```
