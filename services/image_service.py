"""
Image generation service using Holara API
"""
import requests
import json
import base64
from typing import Optional, Dict
import config

class ImageGenerationService:
    """Service for generating images with Holara API"""
    
    def __init__(self):
        self.url = config.HOLARA_API_URL
        self.api_key = config.HOLARA_API_KEY
        
    def generate_image(self, prompt: str, negative_prompt: str = "") -> Optional[Dict]:
        """
        Generate a single image from a text prompt
        
        Args:
            prompt: Text description for image generation
            negative_prompt: Things to avoid in the image
            
        Returns:
            Dictionary with image_base64, execution_time, cost, and remaining_gems
            or None if generation fails
        """
        data = {
            'api_key': self.api_key,
            'model': config.HOLARA_MODEL,
            'num_images': 1,
            'prompt': prompt,
            'negative_prompt': negative_prompt,
            'width': 512,  # Reduced width for better UI
            'height': 768, # Reduced height for better UI
            'steps': config.HOLARA_STEPS,
            'cfg_scale': config.HOLARA_CFG_SCALE,
        }

        try:
            response = requests.post(self.url, data=data)
            
            if response.status_code != 200:
                print(f'Error: {response.status_code} {response.content}')
                return None
                
            response_data = json.loads(response.content)
            
            # Log basic information
            print(f"\n{'='*50}")
            print(f"Image Generation Status: {response_data['status']}")
            print(f"Execution Time: {round(response_data['execution_time'], 2)}s")
            print(f"Generation Cost: {response_data['generation_cost']}")
            print(f"Hologems Remaining: {response_data['hologems_remaining']}")
            print(f"Prompt: {prompt[:100]}...")
            print(f"{'='*50}\n")
            
            image_base64 = response_data['images'][0]
            
            return {
                'image_base64': image_base64,
                'execution_time': response_data['execution_time'],
                'cost': response_data['generation_cost'],
                'remaining_gems': response_data['hologems_remaining']
            }
            
        except Exception as e:
            print(f"Error generating image: {str(e)}")
            return None
    
    def generate_single_image(self, prompt: str, negative_prompt: str = "") -> Optional[Dict]:
        """
        Generate a single image from a prompt
        Args:
            prompt: Text prompt for image generation
            negative_prompt: Things to avoid in the image
        Returns:
            Dictionary with image data or None
        """
        print("Generating single image...")
        return self.generate_image(prompt, negative_prompt)