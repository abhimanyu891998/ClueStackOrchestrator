# MarketDataPublisher System

The MarketDataPublisher system is a real-time financial market data distribution service that processes and streams orderbook updates to connected clients. Based on the codebase, this system simulates market data scenarios and provides WebSocket-based streaming with performance monitoring capabilities.

## Core Business Logic

The system operates as a **real-time orderbook data service** that loads market scenarios, processes orderbook updates through a message queue, and distributes them to WebSocket clients.

## Data Flow Pipeline

The business logic follows this sequence:

1. **Market Data Loading**: The `MarketDataLoader` loads predefined market scenarios from JSON files containing orderbook data
2. **Data Publishing**: The `DataPublisher` streams orderbook updates from the loaded scenarios at configurable speeds
3. **Queue Processing**: The `MessageQueueProcessor` receives orderbook updates, applies processing delays based on market conditions, and validates data integrity
4. **Client Distribution**: Processed orderbook data is broadcast to all connected WebSocket clients in real-time

## Performance Scenarios

The system simulates different market conditions through configurable performance profiles:

* **stable-mode**: 50ms processing delay (normal market operation)
* **burst-mode**: 300ms delay (high-frequency trading conditions)
* **gradual-spike**: 150ms delay (moderate volatility)
* **extreme-spike**: 500ms delay (maximum stress testing)

These scenarios allow testing how the system behaves under different market stress conditions.

## Client Interface

The system exposes a WebSocket endpoint at `/ws` for real-time data streaming and REST endpoints for:

* Health monitoring (`/health`)
* Runtime scenario switching (`/config/profile/{name}`)
* System status and metrics (`/status`, `/metrics`)

## Monitoring and Observability

The system includes comprehensive monitoring with:

* **Prometheus metrics** for orderbook processing rates, memory usage, and queue depth
* **Multi-layered logging** with data validation and audit trails
* **Performance incident detection** when memory thresholds are exceeded or processing delays become critical