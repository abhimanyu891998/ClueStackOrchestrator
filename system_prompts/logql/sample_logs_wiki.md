# MarketDataPublisher Server - Complete Log Samples

## Overview
The MarketDataPublisher Server uses a multi-layered logging system with JSON formatting and three main logger types:
- **Main application logger** - System events, client connections, server lifecycle
- **Data logger** - Orderbook data updates (separate files)
- **System events logger** - Performance metrics, incidents, system health

## System Status & Performance
```json
{"asctime": "2025-07-18 20:08:54", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 353, "funcName": "_log_processing_metrics", "message": "System status: Rate: 6.5 msg/sec, Memory: 37.4MB, Queue: 0"}
{"asctime": "2025-07-18 20:08:43", "name": "queue_processor", "levelname": "WARNING", "filename": "queue_processor.py", "lineno": 346, "funcName": "_log_processing_metrics", "message": "Memory usage elevated: 112.3MB (threshold: 150MB), Queue backlog: 150 messages (1.5% capacity)"}
{"asctime": "2025-07-18 20:08:35", "name": "queue_processor", "levelname": "ERROR", "filename": "queue_processor.py", "lineno": 344, "funcName": "_log_processing_metrics", "message": "Memory usage critical: 156.7MB (threshold: 150MB), Queue: 245, Processing: 287ms"}
{"asctime": "2025-07-18 20:08:27", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 350, "funcName": "_log_processing_metrics", "message": "Queue utilization: 25 messages (0.3% capacity), Processing rate: 8.2 msg/sec"}
```

## Queue Processing & Performance Degradation
```json
{"asctime": "2025-07-18 20:08:33", "name": "queue_processor", "levelname": "ERROR", "filename": "queue_processor.py", "lineno": 148, "funcName": "_process_queue", "message": "Processing performance degraded: 234.2ms (expected: 50ms)"}
{"asctime": "2025-07-18 20:08:28", "name": "queue_processor", "levelname": "WARNING", "filename": "queue_processor.py", "lineno": 150, "funcName": "_process_queue", "message": "Processing latency elevated: 127.3ms"}
{"asctime": "2025-07-18 20:08:25", "name": "queue_processor", "levelname": "WARNING", "filename": "queue_processor.py", "lineno": 143, "funcName": "_process_queue", "message": "Queue backlog detected: 100 messages, Memory: 89.2MB, Processing: 156ms"}
{"asctime": "2025-07-18 20:08:20", "name": "queue_processor", "levelname": "WARNING", "filename": "queue_processor.py", "lineno": 84, "funcName": "add_orderbook", "message": "Queue capacity reached, dropping oldest message"}
```

## Orderbook Data Processing
```json
{"asctime": "2025-07-18 20:08:23", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 98, "funcName": "add_orderbook", "message": "Queue utilization: 1/10000 messages"}
{"asctime": "2025-07-18 20:08:19", "name": "system_events", "levelname": "WARNING", "filename": "queue_processor.py", "lineno": 178, "funcName": "_process_orderbook", "message": "Data staleness detected: orderbook 45672 aged 1234.5ms"}
{"asctime": "2025-07-18 20:08:17", "name": "system_events", "levelname": "ERROR", "filename": "queue_processor.py", "lineno": 176, "funcName": "_process_orderbook", "message": "Data staleness critical: orderbook 45671 aged 2567.8ms"}
{"asctime": "2025-07-18 20:08:15", "name": "system_events", "levelname": "ERROR", "filename": "queue_processor.py", "lineno": 182, "funcName": "_process_orderbook", "message": "Processing performance degraded: orderbook 45670 took 178.45ms (expected: 50ms)"}
```

## Data Loader & Scenario Management
```json
{"asctime": "2025-07-18 20:08:16", "name": "data_loader", "levelname": "INFO", "filename": "data_loader.py", "lineno": 104, "funcName": "get_next_update", "message": "Reached end of scenario 'stable-mode', restarting data feed"}
{"asctime": "2025-07-18 20:08:12", "name": "data_loader", "levelname": "INFO", "filename": "data_loader.py", "lineno": 75, "funcName": "switch_scenario", "message": "Switched from 'stable-mode' to 'burst-mode'"}
{"asctime": "2025-07-18 20:08:10", "name": "data_loader", "levelname": "INFO", "filename": "data_loader.py", "lineno": 45, "funcName": "load_scenario", "message": "Loaded scenario 'burst-mode' with 1500 updates"}
{"asctime": "2025-07-18 20:08:08", "name": "data_loader", "levelname": "ERROR", "filename": "data_loader.py", "lineno": 31, "funcName": "load_scenario", "message": "Scenario 'invalid-scenario' not found"}
{"asctime": "2025-07-18 20:08:06", "name": "data_loader", "levelname": "ERROR", "filename": "data_loader.py", "lineno": 37, "funcName": "load_scenario", "message": "Scenario file not found: ../data/generated/missing-data.json"}
```

## Client Connection Management
```json
{"asctime": "2025-07-18 20:08:05", "name": "main", "levelname": "INFO", "filename": "main.py", "lineno": 66, "funcName": "connect", "message": "Client connected. Total clients: 3"}
{"asctime": "2025-07-18 20:08:03", "name": "main", "levelname": "INFO", "filename": "main.py", "lineno": 72, "funcName": "disconnect", "message": "Client disconnected. Total clients: 2"}
{"asctime": "2025-07-18 20:08:01", "name": "main", "levelname": "ERROR", "filename": "main.py", "lineno": 79, "funcName": "send_personal_message", "message": "Error sending message to client: Connection closed"}
{"asctime": "2025-07-18 20:07:58", "name": "main", "levelname": "ERROR", "filename": "main.py", "lineno": 89, "funcName": "broadcast", "message": "Error broadcasting to client: WebSocket connection closed"}
```

## System Incidents & Memory Monitoring
```json
{"asctime": "2025-07-18 20:07:55", "name": "queue_processor", "levelname": "ERROR", "filename": "queue_processor.py", "lineno": 283, "funcName": "_trigger_incident", "message": "System incident: memory_threshold_exceeded", "type": "memory_threshold_exceeded", "timestamp": "2025-07-18T20:07:55.123456", "details": {"memory_usage_mb": 167.3, "threshold_mb": 150, "queue_size": 234}, "scenario": "burst-mode", "uptime_seconds": 3600.5}
{"asctime": "2025-07-18 20:07:52", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 255, "funcName": "_memory_monitor", "message": "Memory usage normalized"}
{"asctime": "2025-07-18 20:07:50", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 291, "funcName": "_trigger_incident", "message": "System status: Queue 2.3% full, Memory 89.5% used, Processing rate 7.8 msg/sec"}
```

## Data Validation & Audit
```json
{"asctime": "2025-07-18 20:07:48", "name": "system_events", "levelname": "ERROR", "filename": "queue_processor.py", "lineno": 449, "funcName": "_validate_sequence_integrity", "message": "Error in sequence validation: Invalid sequence format"}
{"asctime": "2025-07-18 20:07:45", "name": "system_events", "levelname": "ERROR", "filename": "queue_processor.py", "lineno": 484, "funcName": "_update_audit_trail", "message": "Error updating audit trail: Missing timestamp field"}
{"asctime": "2025-07-18 20:07:42", "name": "data_loader", "levelname": "ERROR", "filename": "data_loader.py", "lineno": 212, "funcName": "validate_orderbook_data", "message": "Orderbook validation error: Invalid price ordering"}
{"asctime": "2025-07-18 20:07:40", "name": "data_loader", "levelname": "WARNING", "filename": "data_loader.py", "lineno": 273, "funcName": "start_publishing", "message": "Invalid orderbook data at sequence 45669"}
```

## Server Lifecycle & Configuration
```json
{"asctime": "2025-07-18 20:07:38", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 54, "funcName": "start", "message": "Queue processor started"}
{"asctime": "2025-07-18 20:07:36", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 66, "funcName": "stop", "message": "Queue processor stopping"}
{"asctime": "2025-07-18 20:07:34", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 78, "funcName": "stop", "message": "Queue processor stopped"}
{"asctime": "2025-07-18 20:07:32", "name": "queue_processor", "levelname": "INFO", "filename": "queue_processor.py", "lineno": 393, "funcName": "switch_scenario", "message": "Scenario switched from 'stable-mode' to 'burst-mode' (processing delay: 156ms)"}
```

## Loki Integration
```json
{"asctime": "2025-07-18 20:07:30", "name": "logger", "levelname": "WARNING", "filename": "logger.py", "lineno": 62, "funcName": "setup_logger", "message": "Failed to setup Loki handler: Connection timeout to Grafana Cloud"}
```

## Key Patterns for NLP Analysis

### Log Structure
- **JSON Format**: All logs use consistent JSON structure with fields: `asctime`, `name`, `levelname`, `filename`, `lineno`, `funcName`, `message`
- **Extended Fields**: System incidents include additional fields like `type`, `timestamp`, `details`, `scenario`, `uptime_seconds`

### Logger Names
- `queue_processor` - Core processing metrics and system health
- `data_loader` - Data loading and scenario management
- `main` - Client connections and server lifecycle
- `system_events` - Performance monitoring and incidents
- `logger` - Logging infrastructure issues

### Log Levels & Patterns
- **INFO**: Normal operations, status updates, client connections
- **WARNING**: Elevated metrics, backlogs, data staleness, invalid data
- **ERROR**: Critical thresholds exceeded, processing failures, connection errors

### Performance Metrics
- Processing rates (msg/sec)
- Memory usage (MB and percentages)
- Queue utilization (capacity percentages)
- Processing latency (milliseconds)
- Data age/staleness (milliseconds)

### System Health Indicators
- Memory thresholds (150MB critical)
- Expected processing times (50ms baseline)
- Queue capacity limits (10,000 messages)
- Data validation failures
- Connection stability