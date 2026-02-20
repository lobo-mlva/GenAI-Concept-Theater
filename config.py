"""
Configuration file for API keys and constants.
"""
import os
from dotenv import load_dotenv

load_dotenv()

# API Keys - loaded from .env file
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
HOLARA_API_KEY = os.getenv("HOLARA_API_KEY", "")

# Holara API Configuration
HOLARA_API_URL = 'https://holara.ai/holara/api/external/1.0/generate_image'
HOLARA_MODEL = 'Aika'
HOLARA_WIDTH = 768
HOLARA_HEIGHT = 1152
HOLARA_STEPS = 30
HOLARA_CFG_SCALE = 12

# OpenAI Configuration
OPENAI_MODEL = "gpt-4"
MAX_COMPLETION_TOKENS = 1000

# Default values
DEFAULT_CREATIVITY = 0.5
MIN_CREATIVITY = 0.1
MAX_CREATIVITY = 1.0