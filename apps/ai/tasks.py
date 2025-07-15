from celery import shared_task
import time
import logging

logger = logging.getLogger(__name__)

@shared_task
def generate_text_async(prompt, max_tokens=100):
    """
    Example task that simulates generating text with an AI model.
    
    In a real implementation, this would call the OpenAI API or another AI service.
    For now, it just simulates processing time and returns a placeholder.
    """
    logger.info(f"Received text generation task with prompt: {prompt[:20]}...")
    
    # Simulate processing time
    time.sleep(2)
    
    # This is where you'd actually call the AI API
    # from openai import OpenAI
    # client = OpenAI()
    # response = client.chat.completions.create(...)
    
    return {
        "status": "completed",
        "text": f"This is a simulated response for prompt: '{prompt}'",
        "tokens_used": len(prompt) + 20  # Just a simulation
    }

@shared_task
def process_image_async(image_path, prompt=None):
    """
    Example task that simulates processing an image with AI.
    
    In a real implementation, this might generate image descriptions,
    analyze content, or modify the image using an AI service.
    """
    logger.info(f"Processing image at {image_path}")
    
    # Simulate processing time
    time.sleep(3)
    
    return {
        "status": "completed",
        "description": f"Simulated image description for {image_path}",
        "processed_at": time.strftime("%Y-%m-%d %H:%M:%S")
    }
