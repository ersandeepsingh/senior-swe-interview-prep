import redis

def dedup_tasks(task, redis_client, prefix="task", ttl_field=1):
    """
    Deduplicate tasks using Redis.
    - task: tuple, with (task_id, ttl)
    - redis_client: redis.StrictRedis or redis.Redis instance
    - prefix: namespace for task keys in Redis
    - ttl_field: index of TTL in the task tuple
    """
    task_id = task[0]
    ttl = task[ttl_field]

    key = f"{prefix}:{task_id}"
    # Use SETNX to set key only if it doesn't already exist, then set expiry
    is_new = redis_client.set(key, "1", nx=True, ex=ttl)
    if is_new:
        print("New task queued:", task_id)
    else:
        print("Duplicate task ignored:", task_id)
    return

if __name__ == "__main__":
    # Create a Redis client (assuming local Redis with default settings)
    redis_client = redis.Redis(host='localhost', port=6379, db=0)

    task = ("task1", 1)
    task2 = ("task1", 1)
    dedup_tasks(task, redis_client)
    dedup_tasks(task2, redis_client)
    # here we need to see system time and subtract the ttl and remove id ttl has become 0
    
    
    

