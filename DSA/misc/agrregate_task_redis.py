"""
Aggregate tasks by account_id in Redis, then process ONE request per account
instead of one request per individual task.

Flow:
  1. Incoming tasks land in a Redis set keyed by account.
  2. Account ids with pending work are tracked in a pending set.
  3. A flusher pops each account once and processes all buffered items together.
"""

import json
import redis


PENDING_ACCOUNTS_KEY = "agg:pending_accounts"


def _account_key(account_id: str, prefix: str = "agg") -> str:
    return f"{prefix}:account:{account_id}"


def enqueue_task_for_account(
    redis_client: redis.Redis,
    account_id: str,
    task: dict,
    prefix: str = "agg",
) -> None:
    """
    Buffer a task under its account. Multiple tasks for the same account
    accumulate; they will be flushed as a single batch later.
    """
    key = _account_key(account_id, prefix)
    redis_client.sadd(key, json.dumps(task, sort_keys=True))
    redis_client.sadd(PENDING_ACCOUNTS_KEY, account_id)
    print(f"Buffered task for account={account_id}: {task}")


def flush_one_account(
    redis_client: redis.Redis,
    account_id: str,
    process_batch,
    prefix: str = "agg",
) -> int:
    """
    Take all buffered tasks for one account and process them in a single call.
    Returns how many tasks were processed.
    """
    key = _account_key(account_id, prefix)
    raw_items = redis_client.smembers(key)
    if not raw_items:
        redis_client.srem(PENDING_ACCOUNTS_KEY, account_id)
        return 0

    tasks = [json.loads(item) for item in raw_items]

    # Process ONE request for this account with all aggregated tasks.
    process_batch(account_id, tasks)

    # Clear buffer only after successful processing.
    redis_client.delete(key)
    redis_client.srem(PENDING_ACCOUNTS_KEY, account_id)
    return len(tasks)


def flush_all_pending_accounts(
    redis_client: redis.Redis,
    process_batch,
    prefix: str = "agg",
) -> None:
    """
    Process every account that has pending work — one batch request each.
    """
    account_ids = list(redis_client.smembers(PENDING_ACCOUNTS_KEY))
    if not account_ids:
        print("No pending accounts")
        return

    for account_id in account_ids:
        # Redis may return bytes depending on decode_responses setting.
        if isinstance(account_id, bytes):
            account_id = account_id.decode()

        count = flush_one_account(redis_client, account_id, process_batch, prefix)
        print(f"Flushed account={account_id}, tasks={count}")


def process_account_batch(account_id: str, tasks: list[dict]) -> None:
    """
    Stand-in for your real API / worker call.
    This is the 'one request per account' boundary.
    """
    print(f"\n=== ONE request for account={account_id} ===")
    print(f"Aggregated {len(tasks)} task(s):")
    for t in tasks:
        print(f"  - {t}")
    # e.g. requests.post(f"/accounts/{account_id}/bulk", json={"tasks": tasks})


if __name__ == "__main__":
    redis_client = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

    # Simulate many incoming single-task events for a few accounts.
    enqueue_task_for_account(redis_client, "acc_1", {"task_id": "t1", "action": "sync"})
    enqueue_task_for_account(redis_client, "acc_1", {"task_id": "t2", "action": "sync"})
    enqueue_task_for_account(redis_client, "acc_1", {"task_id": "t3", "action": "notify"})
    enqueue_task_for_account(redis_client, "acc_2", {"task_id": "t4", "action": "sync"})
    enqueue_task_for_account(redis_client, "acc_2", {"task_id": "t5", "action": "sync"})

    # Instead of 5 requests, this becomes 2 (one per account).
    flush_all_pending_accounts(redis_client, process_account_batch)
