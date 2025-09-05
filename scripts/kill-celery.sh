#!/bin/bash
# Kill all Celery workers for local development

echo "🔍 Looking for Celery workers..."
PIDS=$(ps aux | grep 'celery.*worker.*core' | grep -v grep | awk '{print $2}')

if [ -z "$PIDS" ]; then
    echo "✅ No Celery workers found"
else
    echo "🔪 Killing Celery workers: $PIDS"
    echo "$PIDS" | xargs kill -9
    echo "✅ All workers killed"
fi

# Verify no workers remain
REMAINING=$(ps aux | grep 'celery.*worker.*core' | grep -v grep | wc -l)
if [ "$REMAINING" -eq 0 ]; then
    echo "✅ Confirmed: No workers running"
else
    echo "⚠️  Warning: $REMAINING worker(s) may still be running"
fi
