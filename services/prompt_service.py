"""
Prompt generation service using OpenAI API (v1.x compatible)
"""
from typing import Dict, Optional
from openai import OpenAI
import config

# Cliente OpenAI (API nova)
client = OpenAI(api_key=config.OPENAI_API_KEY)


class PromptGenerationService:
    """Service for generating image prompts and character descriptions"""

    STAGE1_SYSTEM_MESSAGE = {
        "role": "system",
        "content": (
            "You are a professional prompt engineer for anime art generation. "
            "Based on character appearance details, create ONE detailed prompt for an AI art generator. "
            "Use the formula: (subject/character description)(artistic medium)"
            "(style references)(lighting)(colors)(composition). "
            "Speak naturally without brackets. Be specific and vivid. "
            "After the prompt, create a brief character name and initial personality sketch. "
            "Output format: "
            "'Prompt: <prompt>\\n"
            "Name: <name>\\n"
            "Personality: <brief description>'"
        )
    }

    STAGE2_SYSTEM_MESSAGE = {
        "role": "system",
        "content": (
            "You are a creative character development specialist. "
            "Based on the character's appearance and new personality/background details provided, "
            "create a rich, detailed backstory that ties everything together. "
            "Include: character's origins, key life events, motivations, relationships, "
            "and how they became who they are. "
            "Make it engaging and narratively coherent. Write 3–4 paragraphs. "
            "Output only the backstory text, no additional formatting."
        )
    }

    def __init__(self):
        # Modelo definido no config (ex: gpt-4o-mini)
        self.model = config.OPENAI_MODEL

    def generate_initial_prompts(
        self,
        appearance_string: str,
        creativity: float = 0.5
    ) -> Optional[Dict]:
        """
        Generate initial image prompts and basic character info (Stage 1)
        """

        messages = [
            self.STAGE1_SYSTEM_MESSAGE,
            {"role": "user", "content": appearance_string},
        ]
        try:
            print("[GPT-LOG] Sending Stage 1 prompt to OpenAI:")
            print(f"Model: {self.model}")
            print(f"Creativity (temperature): {creativity}")
            print(f"Max tokens: {config.MAX_COMPLETION_TOKENS}")
            print(f"Messages: {messages}")
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=config.MAX_COMPLETION_TOKENS,
                temperature=creativity,
            )
            print("[GPT-LOG] OpenAI response received.")
            print(f"Raw response: {response}")
            reply = response.choices[0].message.content.strip()
            print(f"[GPT-LOG] Parsed reply: {reply}")
            return self._parse_stage1_response(reply)
        except Exception as e:
            print(f"[GPT-LOG] OpenAI API error: {str(e)}")
            return None

    def generate_full_backstory(
        self,
        appearance_string: str,
        personality_string: str,
        character_name: str,
    ) -> Optional[str]:
        """
        Generate detailed backstory (Stage 2)
        """

        user_message = f"""
Character Name: {character_name}

APPEARANCE:
{appearance_string}

PERSONALITY & BACKGROUND:
{personality_string}

Create a detailed, engaging backstory for this character.
"""

        messages = [
            self.STAGE2_SYSTEM_MESSAGE,
            {"role": "user", "content": user_message},
        ]

        try:
            print("[GPT-LOG] Sending Stage 2 prompt to OpenAI:")
            print(f"Model: {self.model}")
            print(f"Max tokens: {getattr(config, 'MAX_COMPLETION_TOKENS', getattr(config, 'MAX_TOKENS', None))}")
            print(f"Messages: {messages}")
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=getattr(config, 'MAX_COMPLETION_TOKENS', getattr(config, 'MAX_TOKENS', None)),
            )
            print("[GPT-LOG] OpenAI response received (Stage 2).")
            print(f"Raw response: {response}")
            reply = response.choices[0].message.content.strip()
            print(f"[GPT-LOG] Parsed reply: {reply}")
            return reply
        except Exception as e:
            print(f"[GPT-LOG] OpenAI API error (stage 2): {e}")
            return None

    def _parse_stage1_response(self, response: str) -> Dict:
        """Parse Stage 1 response into structured data"""

        lines = response.split("\n")
        prompt = ""
        name = "Unnamed Character"
        personality = ""

        for line in lines:
            line = line.strip()
            if line.startswith("Prompt:"):
                prompt = line.replace("Prompt:", "").strip()
            elif line.startswith("Name:"):
                name = line.replace("Name:", "").strip()
            elif line.startswith("Personality:"):
                personality = line.replace("Personality:", "").strip()

        # Fallback se o parsing falhar
        if not prompt:
            prompt = response.strip()

        return {
            "prompts": [prompt],
            "name": name,
            "personality_sketch": personality,
        }
