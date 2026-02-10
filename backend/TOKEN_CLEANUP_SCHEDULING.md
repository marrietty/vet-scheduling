# Token Cleanup Scheduling

This document describes how the token cleanup task is scheduled and provides alternative scheduling options for different deployment scenarios.

## Overview

The token cleanup task removes expired tokens from the blacklist to prevent the database from growing indefinitely. This task needs to run periodically (recommended: daily).

**Requirements:** 7.3, 7.4

## Default Implementation: Built-in Background Task

The application includes a built-in background task that runs automatically when the FastAPI application starts.

### How It Works

1. **Startup**: When the application starts, a background asyncio task is created in the lifespan context manager
2. **Periodic Execution**: The task runs every 24 hours by default
3. **Cleanup**: Each run removes all tokens whose expiration timestamp has passed
4. **Logging**: Each cleanup operation logs the number of tokens removed
5. **Shutdown**: The task is gracefully cancelled when the application shuts down

### Configuration

The cleanup interval can be configured by modifying the `periodic_token_cleanup()` call in `app/main.py`:

```python
# Run cleanup every 12 hours instead of 24
cleanup_task = asyncio.create_task(periodic_token_cleanup(interval_hours=12))
```

### Advantages

- ✅ No external dependencies required
- ✅ Automatic startup and shutdown
- ✅ Integrated logging
- ✅ Works in all deployment environments

### Disadvantages

- ❌ Runs only while the application is running
- ❌ If the application restarts, the timer resets
- ❌ Not suitable if you need precise scheduling (e.g., run at 2 AM daily)

## Alternative: Cron Job (Linux/Unix)

For production environments where you need more control over scheduling, you can use a cron job.

### Setup

1. **Create a standalone script** (`backend/scripts/cleanup_tokens.py`):

```python
#!/usr/bin/env python3
"""Standalone script to cleanup expired tokens."""

import sys
import os

# Add the app directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.features.auth.tasks import cleanup_expired_tokens

if __name__ == "__main__":
    try:
        count = cleanup_expired_tokens()
        print(f"Successfully removed {count} expired token(s)")
        sys.exit(0)
    except Exception as e:
        print(f"Error during cleanup: {str(e)}", file=sys.stderr)
        sys.exit(1)
```

2. **Make the script executable**:

```bash
chmod +x backend/scripts/cleanup_tokens.py
```

3. **Add to crontab** (run daily at 2 AM):

```bash
crontab -e
```

Add this line:

```
0 2 * * * /path/to/venv/bin/python /path/to/backend/scripts/cleanup_tokens.py >> /var/log/token_cleanup.log 2>&1
```

### Advantages

- ✅ Runs independently of the application
- ✅ Precise scheduling (specific times)
- ✅ Continues even if application is down
- ✅ Standard Unix/Linux tool

### Disadvantages

- ❌ Requires shell access to the server
- ❌ Platform-specific (Unix/Linux only)
- ❌ Requires separate logging configuration

## Alternative: Windows Task Scheduler

For Windows servers, use Task Scheduler instead of cron.

### Setup

1. **Create the same standalone script** as shown in the Cron Job section

2. **Open Task Scheduler**:
   - Press `Win + R`, type `taskschd.msc`, press Enter

3. **Create a new task**:
   - Click "Create Basic Task"
   - Name: "Token Cleanup"
   - Trigger: Daily at 2:00 AM
   - Action: Start a program
   - Program: `C:\path\to\venv\Scripts\python.exe`
   - Arguments: `C:\path\to\backend\scripts\cleanup_tokens.py`

### Advantages

- ✅ Native Windows solution
- ✅ GUI-based configuration
- ✅ Precise scheduling

### Disadvantages

- ❌ Windows-only
- ❌ Requires GUI access or PowerShell scripting

## Alternative: APScheduler (Python Library)

For more advanced scheduling needs, you can use APScheduler.

### Setup

1. **Install APScheduler**:

```bash
pip install apscheduler
```

2. **Modify `app/main.py`** to use APScheduler:

```python
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

scheduler = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global scheduler
    
    # ... existing startup code ...
    
    # Start scheduler
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        cleanup_expired_tokens,
        CronTrigger(hour=2, minute=0),  # Run at 2 AM daily
        id='token_cleanup',
        name='Cleanup expired tokens',
        replace_existing=True
    )
    scheduler.start()
    logger.info("Token cleanup scheduler started")
    
    yield
    
    # Shutdown
    if scheduler:
        scheduler.shutdown()
        logger.info("Scheduler shut down")
```

### Advantages

- ✅ Cron-like scheduling in Python
- ✅ Runs within the application
- ✅ Cross-platform
- ✅ Advanced scheduling options (intervals, cron expressions, etc.)

### Disadvantages

- ❌ Requires additional dependency
- ❌ More complex configuration
- ❌ Only runs while application is running

## Alternative: Kubernetes CronJob

For Kubernetes deployments, use a CronJob resource.

### Setup

Create a Kubernetes CronJob manifest (`k8s/token-cleanup-cronjob.yaml`):

```yaml
apiVersion: batch/v1
kind: CronJob
metadata:
  name: token-cleanup
spec:
  schedule: "0 2 * * *"  # Daily at 2 AM
  jobTemplate:
    spec:
      template:
        spec:
          containers:
          - name: token-cleanup
            image: your-app-image:latest
            command: ["python", "/app/scripts/cleanup_tokens.py"]
            env:
            - name: DATABASE_URL
              valueFrom:
                secretKeyRef:
                  name: app-secrets
                  key: database-url
          restartPolicy: OnFailure
```

Apply with:

```bash
kubectl apply -f k8s/token-cleanup-cronjob.yaml
```

### Advantages

- ✅ Native Kubernetes solution
- ✅ Scales with your infrastructure
- ✅ Separate from main application
- ✅ Built-in retry and failure handling

### Disadvantages

- ❌ Requires Kubernetes
- ❌ More complex setup

## Monitoring and Troubleshooting

### Check Logs

The cleanup task logs its activity. Check application logs for entries like:

```
INFO - Starting cleanup of expired tokens from blacklist
INFO - Successfully removed 42 expired token(s) from blacklist
```

### Manual Execution

You can manually trigger cleanup by calling the function:

```python
from app.features.auth.tasks import cleanup_expired_tokens

count = cleanup_expired_tokens()
print(f"Removed {count} tokens")
```

### Common Issues

1. **Task not running**: Check that the application started successfully and the lifespan context manager executed
2. **No tokens removed**: This is normal if no tokens have expired yet
3. **Database errors**: Check database connectivity and permissions

## Recommendations

- **Development**: Use the built-in background task (default implementation)
- **Production (Single Server)**: Use cron job or Windows Task Scheduler for reliability
- **Production (Kubernetes)**: Use Kubernetes CronJob
- **Production (Complex Scheduling)**: Use APScheduler if you need advanced scheduling features

## Testing

To test the cleanup task:

```python
# Run the test suite
pytest backend/tests/test_token_cleanup_task.py -v
```

The test suite includes:
- Test cleanup removes only expired tokens
- Test cleanup with empty blacklist
- Test cleanup with no expired tokens
- Test cleanup with mixed expired/valid tokens
- Test cleanup returns correct count
