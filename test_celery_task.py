"""
Simple script to test the generate_text_async Celery task.
Run this with: uv run test_celery_task.py
"""
import os
import django
import time
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'core.settings')
django.setup()

# Import the task after Django setup
from apps.ai.tasks import generate_text_async
from django_celery_results.models import TaskResult

def test_generate_text():
    print("Sending async task to generate text...")
    
    # Call the task asynchronously
    result = generate_text_async.delay(
        prompt="Write a short story about a magic forest",
        max_tokens=150
    )
    
    task_id = result.id
    print(f"Task sent. Task ID: {task_id}")
    print("The task is running in the background. Check your Celery worker terminal for logs.")
    
    # Poll for task completion using the Django DB
    print("\nPolling for task completion (up to 15 seconds)...")
    max_wait = 15  # seconds
    poll_interval = 1  # seconds
    waited = 0
    
    while waited < max_wait:
        try:
            # Check if task is in the database
            task_result = TaskResult.objects.filter(task_id=task_id).first()
            
            if task_result:
                if task_result.status == 'SUCCESS':
                    print("\nTask completed successfully!")
                    print(f"Result: {task_result.result}")
                    return
                elif task_result.status == 'FAILURE':
                    print(f"\nTask failed: {task_result.result}")
                    return
                else:
                    print(f"Task status: {task_result.status}...", end='\r')
            else:
                print(f"Waiting for task result... ({waited}s)", end='\r')
                
            sys.stdout.flush()
            time.sleep(poll_interval)
            waited += poll_interval
            
        except Exception as e:
            print(f"\nError checking task status: {e}")
            break
    
    print("\nTimeout waiting for task completion.")
    print("Check Celery worker logs for details.")

if __name__ == "__main__":
    test_generate_text()
