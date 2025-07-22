# MarketDataPublisher Server - Log Samples

## Overview
Multi-layered logging system with JSON formatting and three main logger types:
- **Main application logger**: System events, client connections, server lifecycle
- **Data logger**: Orderbook data updates (separate files)
- **System events logger**: Performance metrics, incidents, system health

## System Status & Performance Monitoring

### Normal Operations
```json
{"asctime": "2025-07-22 08:17:54", "name": "queue_processor", "levelname": "INFO", "message": "System status: Rate: 6.5 msg/sec, Memory: 37.4MB, Queue: 0"}
{"asctime": "2025-07-22 08:17:27", "name": "queue_processor", "levelname": "INFO", "message": "Queue utilization: 1/10000 messages"}
```

### Performance Degradation Alerts
```json
{"asctime": "2025-07-22 08:17:43", "name": "queue_processor", "levelname": "WARNING", "message": "Memory usage elevated: 112.3MB (threshold: 150MB), Queue backlog: 150 messages (1.5% capacity)"}
{"asctime": "2025-07-22 08:17:28", "name": "queue_processor", "levelname": "WARNING", "message": "Processing latency elevated: 127.3ms"}
```

### Critical Issues
```json
{"asctime": "2025-07-22 08:17:35", "name": "queue_processor", "levelname": "ERROR", "message": "Memory usage critical: 156.7MB (threshold: 150MB), Queue: 245, Processing: 287ms"}
{"asctime": "2025-07-22 08:17:33", "name": "queue_processor", "levelname": "ERROR", "message": "Processing performance degraded: 234.2ms (expected: 50ms)"}
{"asctime": "2025-07-22 08:17:20", "name": "queue_processor", "levelname": "WARNING", "message": "Queue capacity reached, dropping oldest message"}
```

## Orderbook Data Processing

### Data Staleness Detection
```json
{"asctime": "2025-07-22 08:17:19", "name": "system_events", "levelname": "WARNING", "message": "Data staleness detected: orderbook 45672 aged 1234.5ms"}
{"asctime": "2025-07-22 08:17:17", "name": "system_events", "levelname": "ERROR", "message": "Data staleness critical: orderbook 45671 aged 2567.8ms"}
```

## Client Connection Management
```json
{"asctime": "2025-07-22 08:17:05", "name": "main", "levelname": "INFO", "message": "Client connected. Total clients: 3"}
{"asctime": "2025-07-22 08:17:03", "name": "main", "levelname": "INFO", "message": "Client disconnected. Total clients: 2"}
{"asctime": "2025-07-22 08:17:01", "name": "main", "levelname": "ERROR", "message": "Error sending message to client: Connection closed"}
{"asctime": "2025-07-22 08:16:58", "name": "main", "levelname": "ERROR", "message": "Error broadcasting to client: WebSocket connection closed"}
```

## System Incidents & Memory Monitoring
```json
{
  "asctime": "2025-07-22 08:16:55",
  "name": "queue_processor",
  "levelname": "ERROR",
  "message": "System incident: memory_threshold_exceeded",
  "type": "memory_threshold_exceeded",
  "timestamp": "2025-07-22T08:16:55.123456",
  "details": {
    "memory_usage_mb": 167.3,
    "threshold_mb": 150,
    "queue_size": 234
  },
  "scenario": "burst-mode",
  "uptime_seconds": 3600.5
}
```

```json
{"asctime": "2025-07-22 08:16:52", "name": "queue_processor", "levelname": "INFO", "message": "Memory usage normalized"}
{"asctime": "2025-07-22 08:16:50", "name": "queue_processor", "levelname": "INFO", "message": "System status: Queue 2.3% full, Memory 89.5% used, Processing rate 7.8 msg/sec"}
```

## Server Lifecycle
```json
{"asctime": "2025-07-22 08:16:45", "name": "main", "levelname": "INFO", "message": "MarketDataPublisher server starting"}
{"asctime": "2025-07-22 08:16:44", "name": "main", "levelname": "INFO", "message": "Server listening on localhost:8000"}
{"asctime": "2025-07-22 08:16:43", "name": "main", "levelname": "INFO", "message": "Market scenarios loaded"}
{"asctime": "2025-07-22 08:16:42", "name": "main", "levelname": "INFO", "message": "Queue processor started"}
{"asctime": "2025-07-22 08:16:41", "name": "main", "levelname": "INFO", "message": "Data publishing started automatically"}
```

## Scenario Management
```json
{"asctime": "2025-07-22 08:16:32", "name": "main", "levelname": "INFO", "message": "Received profile switch request: burst-mode"}
{"asctime": "2025-07-22 08:16:30", "name": "main", "levelname": "INFO", "message": "Successfully switched to profile: burst-mode"}
{"asctime": "2025-07-22 08:16:28", "name": "queue_processor", "levelname": "INFO", "message": "Scenario switched from 'stable-mode' to 'burst-mode' (processing delay: 156ms)"}
```

## System Alerts & Broadcasting
```json
{"asctime": "2025-07-22 08:16:25", "name": "main", "levelname": "WARNING", "message": "System alert broadcasted: stale_data"}
{"asctime": "2025-07-22 08:16:23", "name": "main", "levelname": "WARNING", "message": "System alert broadcasted: memory_threshold_exceeded"}
```

## Specialized Event Logging
```json
{"asctime": "2025-07-22 08:16:18", "name": "main", "levelname": "INFO", "message": "Scenario switched", "event": "scenario_switch", "old_scenario": "stable-mode", "new_scenario": "burst-mode"}
{"asctime": "2025-07-22 08:16:15", "name": "main", "levelname": "WARNING", "message": "Incident alert triggered", "event": "incident_alert", "alert_type": "stale_data", "details": {"sequence_id": 45671, "data_age_ms": 2567.8}}
```

## Key Thresholds & Metrics
- **Memory threshold**: 150MB
- **Expected processing time**: 50ms
- **Queue capacity**: 10,000 messages
- **Server port**: localhost:8000
- **Scenarios**: stable-mode, burst-mode