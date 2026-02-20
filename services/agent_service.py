"""
Character agent service using modern LangChain (LCEL)
"""
from typing import Optional, List

from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.messages import HumanMessage, AIMessage, BaseMessage

import config


class DirectorAgent:
    """Director agent that orchestrates scenes between characters"""

    def __init__(self):
        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            api_key=config.OPENAI_API_KEY,
        )
        self.scene_history: List[BaseMessage] = []

    def suggest_scene(self, char1_desc: str, char1_name: str, char2_desc: str, char2_name: str) -> str:
        """Suggest an interesting scene for the two characters"""
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a creative director for character interactions. 
Suggest an interesting, engaging scene for these two characters to act out together.
Keep the suggestion brief (2-3 sentences) and focus on the setup/situation.

Character 1: {char1_name}
{char1_desc}

Character 2: {char2_name}
{char2_desc}
"""),
            ("human", "Suggest an interesting scene for these characters.")
        ])
        
        messages = prompt.format_messages(
            char1_name=char1_name, char1_desc=char1_desc,
            char2_name=char2_name, char2_desc=char2_desc
        )
        response = self.llm.invoke(messages)
        return response.content.strip()

    def direct_scene(self, scene_instruction: str, char1_name: str, char1_desc: str, 
                     char2_name: str, char2_desc: str, scene_so_far: str = "", 
                     char1_spoke: bool = False, char2_spoke: bool = False,
                     last_speaker: str = "", previous_narrations: list = None) -> dict:
        """
        Direct how the scene should unfold. Returns direction for the next interaction.
        """
        # FORCE alternation - determine who MUST speak next
        if last_speaker == char1_name:
            forced_next = char2_name
            other_char = char1_name
        elif last_speaker == char2_name:
            forced_next = char1_name
            other_char = char2_name
        elif char1_spoke and not char2_spoke:
            forced_next = char2_name
            other_char = char1_name
        elif char2_spoke and not char1_spoke:
            forced_next = char1_name
            other_char = char2_name
        else:
            forced_next = char1_name  # Default: char1 starts
            other_char = char2_name
        
        # Count exchanges to decide on narration frequency
        exchange_count = len([line for line in scene_so_far.split('\n') if '":' in line or ':"' in line]) if scene_so_far else 0
        
        # Narration every 2-3 exchanges, but varied
        needs_narration = exchange_count == 0 or exchange_count % 3 == 0
        
        # Build list of previous narrations to avoid
        prev_narr_text = ""
        if previous_narrations and len(previous_narrations) > 0:
            prev_narr_text = "PREVIOUS NARRATIONS (DO NOT REPEAT THESE):\n- " + "\n- ".join(previous_narrations[-3:])
        
        prompt = ChatPromptTemplate.from_messages([
            ("system", """You are a STORYTELLER narrating an unfolding tale between two characters.

Your narration style:
- Write as if you're telling a story to an audience: "And so...", "In that moment...", "The tension between them..."
- Focus on EMOTIONS, TENSION, and the RELATIONSHIP between characters
- Describe what's happening BETWEEN them - glances, unspoken feelings, the electricity in the air
- Vary your narration: sometimes focus on a character's internal state, sometimes on the atmosphere, sometimes on a small telling detail
- Keep it to 1-2 sentences max
- NEVER repeat the same imagery or phrases from before

{prev_narrations}

Scene premise: {scene_instruction}

Dialogue so far:
{scene_context}

{narration_instruction}

Now cue {forced_next} to respond to {other_char}.

Return ONLY valid JSON:
{{"narration": "your storyteller narration here", "next_character": "{forced_next}", "prompt_for_character": "emotional cue for {forced_next}"}}
"""),
            ("human", "Continue the story - what happens as {forced_next} responds?")
        ])
        
        if needs_narration:
            narration_instruction = "Write a storyteller-style narration that advances the emotional beat of the scene. Focus on something NEW - a gesture, a feeling, a shift in energy."
        else:
            narration_instruction = "No narration needed this turn - let the dialogue breathe. Set narration to empty string."
        
        scene_context = scene_so_far if scene_so_far else "The scene begins..."
        
        messages = prompt.format_messages(
            scene_instruction=scene_instruction,
            scene_context=scene_context,
            forced_next=forced_next,
            other_char=other_char,
            narration_instruction=narration_instruction,
            prev_narrations=prev_narr_text
        )
        
        response = self.llm.invoke(messages)
        
        # Parse JSON response
        import json
        import re
        
        # Try to extract JSON from response
        content = response.content.strip()
        content = re.sub(r'```json\s*', '', content)
        content = re.sub(r'```\s*', '', content)
        
        try:
            result = json.loads(content)
        except json.JSONDecodeError:
            result = {}
        
        # FORCE the correct next character
        result["next_character"] = forced_next
        
        # Ensure all keys exist
        if "narration" not in result:
            result["narration"] = ""
        if not needs_narration:
            result["narration"] = ""
        if "prompt_for_character" not in result:
            result["prompt_for_character"] = f"Respond to {other_char} with emotion."
        if "scene_complete" not in result:
            result["scene_complete"] = False
        
        # Don't allow scene to complete until enough exchanges
        if exchange_count < 6 or not (char1_spoke and char2_spoke):
            result["scene_complete"] = False
            
        return result

    def reset(self):
        """Reset the director's scene history"""
        self.scene_history = []


class CharacterAgent:
    """Conversational agent that roleplays as the created character"""

    def __init__(self, character_description: str, character_name: str):
        self.character_name = character_name
        self.character_description = character_description
        self.history: List[BaseMessage] = []

        self.llm = ChatOpenAI(
            model="gpt-5-mini",
            api_key=config.OPENAI_API_KEY,
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                (
                    "system",
                    """You are roleplaying as the following character. Stay in character at all times.

{character_description}

IMPORTANT INSTRUCTIONS:
- Respond as this character would, using their personality, background, and speech patterns
- Reference your backstory and experiences naturally in conversation
- Show emotions and reactions consistent with your personality
- If asked about things outside your character knowledge, respond as the character would
- Never break character or mention that you're an AI

You are: {character_name}
""",
                ),
                ("placeholder", "{history}"),
                ("human", "{input}"),
            ]
        )
    
    def scene_response(self, direction: str, other_char_name: str, scene_context: str) -> str:
        """Respond to a director's scene direction"""
        scene_prompt = ChatPromptTemplate.from_messages([
            ("system", """You are roleplaying as the following character in a directed scene WITH ANOTHER CHARACTER.

{character_description}

You are: {character_name}
You are interacting with: {other_char_name}

SCENE SO FAR:
{scene_context}

CRITICAL DIALOGUE INSTRUCTIONS:
- You are having a CONVERSATION with {other_char_name} - speak TO them directly
- If they just said something, RESPOND to what they said
- Use their name naturally in your dialogue when appropriate
- Show your character's personality through HOW you talk to them
- Express emotions, reactions, and opinions about what {other_char_name} says/does
- Keep response brief: 1-3 sentences of dialogue + optional *brief action*
- Your dialogue should invite a response from {other_char_name}

FORMAT: Speak as your character. Use *asterisks* only for brief physical actions.
Example: "That's ridiculous!" *crosses arms* "You can't possibly believe that, {other_char_name}."
"""),
            ("placeholder", "{history}"),
            ("human", "Director's cue: {direction}")
        ])
        
        messages = scene_prompt.format_messages(
            character_description=self.character_description,
            character_name=self.character_name,
            other_char_name=other_char_name,
            scene_context=scene_context,
            history=self.history,
            direction=direction
        )
        
        response = self.llm.invoke(messages)
        self.history.append(HumanMessage(content=direction))
        self.history.append(AIMessage(content=response.content))
        
        return response.content.strip()

    def chat(self, user_message: str) -> str:
        """Send a message to the character and get a response"""
        try:
            # Monta mensagens
            messages = self.prompt.format_messages(
                character_description=self.character_description,
                character_name=self.character_name,
                history=self.history,
                input=user_message,
            )

            # Chamada do modelo
            response = self.llm.invoke(messages)

            # Atualiza histórico
            self.history.append(HumanMessage(content=user_message))
            self.history.append(AIMessage(content=response.content))

            return response.content.strip()

        except Exception as e:
            print(f"Error in character conversation: {e}")
            return f"*{self.character_name} seems distracted and didn't respond*"

    def reset_conversation(self):
        """Clear conversation history"""
        self.history = []

    def get_conversation_history(self) -> List[BaseMessage]:
        """Get the full conversation history"""
        return self.history



class AgentService:
    """Service for managing one or more character agents"""

    def __init__(self):
        self.agents: list[Optional[CharacterAgent]] = [None, None]
        self.director: Optional[DirectorAgent] = None

    def create_agent(self, character_description: str, character_name: str, idx: int = 0) -> CharacterAgent:
        agent = CharacterAgent(character_description, character_name)
        self.agents[idx] = agent
        return agent

    def create_director(self) -> DirectorAgent:
        """Create or get the director agent"""
        if not self.director:
            self.director = DirectorAgent()
        return self.director

    def get_director(self) -> Optional[DirectorAgent]:
        """Get existing director or None"""
        return self.director

    def chat_with_character(self, message: str, idx: int = 0) -> Optional[str]:
        agent = self.agents[idx]
        if not agent:
            return None
        return agent.chat(message)

    def scene_response(self, direction: str, idx: int, other_char_name: str, scene_context: str) -> Optional[str]:
        """Get a character's response to a director's scene direction"""
        agent = self.agents[idx]
        if not agent:
            return None
        return agent.scene_response(direction, other_char_name, scene_context)

    def reset_agent(self, idx: int = None):
        if idx is None:
            for agent in self.agents:
                if agent:
                    agent.reset_conversation()
            if self.director:
                self.director.reset()
        else:
            if self.agents[idx]:
                self.agents[idx].reset_conversation()

    def reset_director(self):
        """Reset only the director's scene history"""
        if self.director:
            self.director.reset()

    def has_agent(self, idx: int = 0) -> bool:
        return self.agents[idx] is not None

    def group_chat(self, user_message: str) -> tuple[str, str]:
        """
        Simulate a group chat: user sends a message, agent1 responds, then agent2 responds to both user and agent1.
        Returns (agent1_reply, agent2_reply)
        """
        agent1, agent2 = self.agents[0], self.agents[1]
        if not agent1 or not agent2:
            return ("", "")
        # Agent 1 responds to user
        agent1_reply = agent1.chat(user_message)
        # Agent 2 sees both user and agent1's reply
        agent2_input = f"User: {user_message}\n{agent1.character_name}: {agent1_reply}"
        agent2_reply = agent2.chat(agent2_input)
        # Optionally, agent1 can see agent2's reply and respond again (for more turns)
        return agent1_reply, agent2_reply
