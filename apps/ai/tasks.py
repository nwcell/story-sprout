from celery import shared_task, signals
from celery.schedules import crontab
from core.celery import app as celery_app
import time
import logging
import traceback

logger = logging.getLogger(__name__)

@shared_task
def generate_text_async(prompt, max_tokens=100):
    """
    Generate text using LiteLLM with the configured AI provider.
    
    LiteLLM provides a unified interface for multiple AI providers including OpenAI,
    Anthropic, Google, etc. The actual provider is configured through environment variables.
    """
    from litellm import completion
    import os
    
    logger.info(f"Generating text with prompt: {prompt[:50]}...")
    
    try:
        # Check if we have an API key configured
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            logger.warning("No OPENAI_API_KEY found in environment. Using simulated response.")
            return {
                "status": "completed",
                "text": f"[SIMULATED] Response for: '{prompt}'",
                "tokens_used": len(prompt) + 20,
                "model": "simulated"
            }
        
        # Make the API call through LiteLLM
        response = completion(
            model="gpt-3.5-turbo",  # Can be configured via environment variable
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens
        )
        
        # Extract the generated text
        generated_text = response.choices[0].message.content
        usage = response.usage
        
        logger.info(f"Successfully generated text. Used {usage.total_tokens} tokens.")
        
        return {
            "status": "completed",
            "text": generated_text,
            "tokens_used": usage.total_tokens,
            "model": response.model
        }
        
    except Exception as e:
        logger.error(f"Error generating text: {e}")
        logger.error(traceback.format_exc())
        
        return {
            "status": "error",
            "text": f"Error generating text: {str(e)}",
            "tokens_used": 0,
            "model": None
        }

@shared_task
def process_ai_prompt(prompt_id):
    """
    Process an AIPrompt by ID and update its status and result.
    
    This task fetches the prompt from the database, generates text using the AI,
    and updates the prompt record with the result.
    """
    from apps.ai.models import AIPrompt
    
    try:
        # Get the prompt from the database
        prompt = AIPrompt.objects.get(id=prompt_id)
        
        # Mark as processing
        prompt.mark_as_processing(process_ai_prompt.request.id)
        
        logger.info(f"Processing AI prompt {prompt_id}: {prompt.prompt[:50]}...")
        
        # Call the AI service to generate text
        result = generate_text_async(prompt.prompt, prompt.max_tokens)
        
        # Extract the text and metadata from the result
        generated_text = result.get('text', 'No text generated')
        status = result.get('status')
        model = result.get('model', 'unknown')
        tokens_used = result.get('tokens_used', 0)
        
        # Log the result
        logger.info(f"Generated text for prompt {prompt_id} using model {model}, {tokens_used} tokens used")
        
        # Check if there was an error
        if status == 'error':
            prompt.mark_as_failed(generated_text)
            return {"status": "error", "prompt_id": prompt_id, "error": generated_text}
        
        # Update the prompt with the result and metadata
        prompt.mark_as_completed(generated_text, tokens_used=tokens_used, model=model)
        
        logger.info(f"AI prompt {prompt_id} processed successfully")
        return {"status": "success", "prompt_id": prompt_id}
        
    except AIPrompt.DoesNotExist:
        logger.error(f"AI prompt {prompt_id} does not exist")
        return {"status": "error", "error": f"AIPrompt {prompt_id} does not exist"}
        
    except Exception as e:
        logger.error(f"Error processing AI prompt {prompt_id}: {e}")
        logger.error(traceback.format_exc())
        
        # Try to update the prompt with the error
        try:
            prompt = AIPrompt.objects.get(id=prompt_id)
            prompt.mark_as_failed(str(e))
        except Exception:
            pass
        
        return {"status": "error", "error": str(e)}

@shared_task
def process_image_async(image_path, prompt=None):
    """
    Example task that simulates processing an image with AI.
    
    This would typically connect to an image generation/processing API.
    """
    logger.info(f"Processing image at: {image_path}")
    
    # Simulate processing time
    time.sleep(3)
    
    return {
        "status": "completed",
        "image_url": f"{image_path}_processed",  # Simulated output
        "processing_time": 3
    }

@shared_task
def process_pending_prompts():
    """
    Periodic task that processes any pending AI prompts in the database.
    
    This ensures that no prompts are left unprocessed, even if they were created
    while the worker was down or if there were any task failures.
    """
    from apps.ai.models import AIPrompt
    
    # Find all pending or failed prompts
    pending_prompts = AIPrompt.objects.filter(status__in=['pending', 'failed'])
    count = pending_prompts.count()
    
    if count > 0:
        logger.info(f"Found {count} pending AI prompts. Processing...")
        
        for prompt in pending_prompts:
            # Don't process prompts that already have a task running
            if prompt.status == 'processing' and prompt.task_id:
                continue
                
            # Process the prompt
            logger.info(f"Processing pending prompt ID {prompt.id}: {prompt.prompt[:50]}...")
            process_ai_prompt.delay(prompt.id)
        
        return {"status": "success", "processed_count": count}
    else:
        return {"status": "success", "processed_count": 0}

# Register the periodic task to run every minute
celery_app.conf.beat_schedule = {
    'process-pending-ai-prompts': {
        'task': 'apps.ai.tasks.process_pending_prompts',
        'schedule': crontab(minute='*'),  # Every minute
    },
}

# Process pending prompts when the worker starts up
@signals.worker_ready.connect
def process_pending_prompts_on_startup(sender, **kwargs):
    """
    Signal handler that processes pending prompts when the worker starts.
    
    This ensures that any prompts created while the worker was down
    get processed immediately when the worker starts.
    """
    logger.info("Worker starting up. Processing any pending AI prompts...")
    process_pending_prompts.delay()
    return True
