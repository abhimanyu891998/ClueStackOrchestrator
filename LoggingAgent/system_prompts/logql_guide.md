# LogQL Complete Reference Guide

## Overview

LogQL (Log Query Language) is Loki's native query language - essentially a distributed grep with labels for filtering. **Every LogQL query MUST contain a log stream selector.**

A LogQL query consists of:
1. **Log Stream Selector** (required) - reduces log streams to manageable volume
2. **Filter Expression** (optional) - performs distributed grep over retrieved streams

## Log Stream Selector Syntax

### Basic Structure
```logql
{label="value",label2="value2"}
```

### Label Matching Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `=` | Exactly equal | `{app="mysql"}` |
| `!=` | Not equal | `{app!="mysql"}` |
| `=~` | Regex matches | `{name=~"mysql.+"}` |
| `!~` | Regex does not match | `{name!~"mysql.+"}` |

### Examples
```logql
{app="mysql",name="mysql-backup"}
{name=~"mysql.+"}
{name!~"mysql.+"}
{instance=~"kafka-[23]",name="kafka"}
```

## Filter Expression Syntax

### Filter Operators

| Operator | Description | Example |
|----------|-------------|---------|
| `\|=` | Log line contains string | `{job="mysql"} \|= "error"` |
| `!=` | Log line does not contain string | `{job="mysql"} != "timeout"` |
| `\|~` | Log line matches regex | `{name="kafka"} \|~ "tsdb-ops.*io:2003"` |
| `!~` | Log line does not match regex | `{job="mysql"} !~ "timeout.*error"` |

### Filter Chaining
Filters can be chained and are applied sequentially - ALL filters must match:
```logql
{job="mysql"} |= "error" != "timeout"
```

### Regex Notes
- Uses Go RE2 syntax
- Case-sensitive by default
- Use `(?i)` prefix for case-insensitive matching: `|~ "(?i)error"`

## Range Vector Aggregation

### Time Range Syntax
```logql
{job="mysql"}[5m]    # Last 5 minutes
{job="mysql"}[1h]    # Last 1 hour
{job="mysql"}[24h]   # Last 24 hours
```

### Aggregation Functions

| Function | Description | Example |
|----------|-------------|---------|
| `rate()` | Entries per second | `rate({job="mysql"}[5m])` |
| `count_over_time()` | Count entries in range | `count_over_time({job="mysql"}[5m])` |

### Complex Aggregation Examples
```logql
# Rate of non-timeout errors
rate(({job="mysql"} |= "error" != "timeout")[10s])

# Count MySQL logs in last 5 minutes
count_over_time({job="mysql"}[5m])
```

## Aggregation Operators

### Available Operators
- `sum` - Calculate sum over labels
- `min` - Select minimum over labels  
- `max` - Select maximum over labels
- `avg` - Calculate average over labels
- `stddev` - Population standard deviation
- `stdvar` - Population standard variance
- `count` - Count number of elements
- `bottomk` - Select smallest k elements
- `topk` - Select largest k elements

### Grouping Syntax
```logql
<aggr-op>([parameter,] <vector expression>) [without|by (<label list>)]
```

- `by` - Include only specified labels in result
- `without` - Exclude specified labels from result
- `parameter` - Required only for `topk` and `bottomk`

### Aggregation Examples
```logql
# Top 10 applications by log throughput
topk(10, sum(rate({region="us-east1"}[5m])) by (name))

# Count logs by level
sum(count_over_time({job="mysql"}[5m])) by (level)

# Average rate of HTTP GET requests by region
avg(rate(({job="nginx"} |= "GET")[10s])) by (region)
```

## JSON Log Processing

### JSON Parser
```logql
{job="containerlogs"} | json
```

### Error Handling
```logql
{job="containerlogs"} | json | __error__ = ""
```

### Field Access
```logql
{job="containerlogs"} | json | level="error"
{job="containerlogs"} | json | msg!="configuration"
```

## Common Query Patterns

### General Error Detection
```logql
# Basic error detection
{job="containerlogs"} |~ "(?i)(error|fail|lost|closed|panic|fatal|crash|password|authentication|denied)"

# With false positive removal
{job="containerlogs", container_name!~"^promtail.+"} |~ "(?i)(error|fail|lost|closed|panic|fatal|crash|password|authentication|denied)" != "ForgotPassword"

# Advanced with JSON parsing
{job="containerlogs", container_name=~"myapp-\\w+-prod"} |~ "(?i)(error|fail|lost|closed|panic|fatal|crash|password|authentication|denied)" != "ForgotPassword" | json | __error__ = "" | level="error"
```

### Rate Limiting Issues
```logql
{job="containerlogs"} |~ "(too many requests|rate.limit)"
```

### Authentication Errors
```logql
# Basic
{job="containerlogs"} |~ "(unauthenticated|access.denied)"

# Advanced
{job="containerlogs"} |~ "(?i)((not |un)authenticated|(not |un)authorized|access.denied|invalid)"
```

### Data/Parsing Errors
```logql
{job="containerlogs"} |~ "(?i)(deserialize|unmarshal|bad request|missing required|invalid value)"
```

### Third-party Service Issues
```logql
{job="containerlogs"} |~ "(?i)(service unavailable|maintenance|capacity|try again later|time(d |-)?out)" | json | __error__ = "" | msg!="configuration"
```

### Server Errors
```logql
{job="containerlogs"} |~ "(?i)(internal server error)"
```

## Query Construction Rules

### Essential Rules
1. **ALWAYS start with a log stream selector in curly braces**
2. **Use specific labels to reduce stream volume before filtering**
3. **Chain filters from most to least restrictive**
4. **Use appropriate time ranges for performance**

### Performance Tips
1. More specific label selectors = better performance
2. Use `!=` and `!~` sparingly as they're expensive
3. Apply string filters before regex filters
4. Use shorter time ranges when possible

### Common Mistakes to Avoid
1. Missing log stream selector (will cause query to fail)
2. Using `=` instead of `|=` for log content filtering
3. Not escaping special regex characters
4. Forgetting case-insensitive flag `(?i)` when needed
5. Using overly broad time ranges without specific labels

## Query Template Structure
```logql
{required_label="value"[,additional_labels]} [time_range] [|= "string_filter"] [|~ "regex_filter"] [| json] [| field_selector] [aggregation_function]
```

## Example Complete Queries
```logql
# Error rate for specific service
rate(({app="myservice", env="prod"} |= "ERROR")[5m])

# Top error-prone containers
topk(5, sum(count_over_time({job="kubernetes-pods"} |~ "(?i)error"[1h])) by (container))

# Authentication failures with context
{app="api-gateway"} |~ "(?i)(authentication|unauthorized)" | json | __error__ = "" | status_code >= 400
```