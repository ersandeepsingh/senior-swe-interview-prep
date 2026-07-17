
# Designing metrics aggregation system

# Requirement:-
# CPU , memory
# API Latency
# Failure, service errors

# service sends--> metric name, matric value
# focus -- classes and relationships
avg = 70+30+50

# Service components:
# Metric
# id, name, value, created_at, updated_at, metric_type_id
# Enums ["CPU", "Memory Usage", "API"]


# Metric Type
# agg_type
# type
# time


# service
# id 
# service_id
# matric_type
# name
# aggreated_value
# many Metrics


# AgrregationType
# count
# average


