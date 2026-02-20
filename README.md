# AI Character Creator

Anime character generation system in 3 stages with integrated conversational agent.

## Project Structure

```
project/
│
├── config.py                      # Centralized configurations and API keys
├── main.py                        # Streamlit interface (3 stages)
│
├── models/
│   └── character.py              # Character data model
│
└── services/
    ├── prompt_service.py         # Prompt generation via OpenAI
    ├── image_service.py          # Image generation via Holara
    └── agent_service.py          # Conversational agent (LangChain)
```

## Application Flow

### Stage 1: Appearance
- User fills in basic visual appearance fields
- Fields: species, gender, age, physique, hair, eyes, colors, clothing, art style
- Adjustable creativity (0.1 - 1.0)
- Output: 
  - 2 optimized prompts for image generation
  - 2 generated images
  - Character name
  - Initial personality sketch

### Stage 2: Personality & Review
- Displays the 2 generated images
- Allows editing/adding:
  - Character name
  - Personality traits
  - Skills/powers
  - Occupation
  - Context/universe
  - Marks/scars
  - Backstory (editable)
- Button to regenerate backstory with new creativity
- Output: Complete and detailed character

### Stage 3: Chat with Character
- Integrated chat interface
- Conversational agent that interprets the created character
- Uses LangChain + GPT to maintain context and personality
- Persistent conversation history
- Controls: reset conversation, edit character, create new

## Architecture

### Models (Data Models)

#### CharacterAppearance
Basic appearance fields (Stage 1)

#### CharacterPersonality
Extended personality and context fields (Stage 2)

#### Character
Complete model that combines appearance, personality, images and prompts

### Services

#### PromptGenerationService
- `generate_initial_prompts()`: Stage 1 - generates image prompts + basic info
- `generate_full_backstory()`: Stage 2 - generates detailed backstory
- Uses different system messages for each stage

#### ImageGenerationService
- `generate_image()`: Generates one image via Holara API
- `generate_multiple_images()`: Generates multiple images
- Logging of costs and execution time

#### AgentService
- Manages the CharacterAgent (conversational agent)
- `create_agent()`: Initializes agent with character description
- `chat_with_character()`: Interface to chat with the character

#### CharacterAgent (LangChain)
- Uses ConversationChain with memory
- Prompt template that keeps the character "in character"
- Memory buffer for conversational context

## Configuration

### 1. Install dependencies
```bash
pip install -r requirements.txt
```

**Main dependencies:**
- `streamlit>=1.28.0` - Web interface
- `openai>=1.12.0` - API v1.0+ (updated!)
- `langchain>=0.1.0` - Framework for agents
- `langchain-openai>=0.0.5` - LangChain + OpenAI v1.0+ integration
- `requests>=2.31.0` - HTTP client for Holara API

### 2. Configure API Keys
Edit `config.py`:
```python
OPENAI_API_KEY = "your-openai-key"
HOLARA_API_KEY = "your-holara-key"
OPENAI_MODEL = "gpt-4o-mini"  # Recommended: best cost-effectiveness!
```

**IMPORTANT**: In production, use environment variables:
```bash
# Create a .env file (copy from .env.example)
cp .env.example .env

# Edit .env with your keys
OPENAI_API_KEY=sk-your-key-here
HOLARA_API_KEY=secret-your-key-here
OPENAI_MODEL=gpt-4o-mini
```

**Available OpenAI Models:**
- `gpt-4o-mini` (Recommended) - Best cost/performance ratio ($0.15/1M tokens)
- `gpt-4o` - Best quality ($2.50/1M tokens)
- `gpt-4-turbo` - Most expensive, for complex tasks ($10.00/1M tokens)
- `gpt-3.5-turbo` - Legacy, not recommended

### 3. Run application
```bash
streamlit run main.py
```

## Implemented Improvements

### Separation of Responsibilities
- Centralized configurations (`config.py`)
- Isolated data models (`models/`)
- Business logic in services (`services/`)
- Interface separated from logic

### Staged Flow
- Stage 1: Focus on visual appearance
- Stage 2: Personality and refinement
- Stage 3: Interaction with character

### Conversational Agent
- LangChain integration
- Conversation memory
- Character maintains consistency
- Full character context in prompt

### UX/UI
- Clear navigation between stages
- Visual feedback (spinners, progress)
- Backstory editing
- Images and prompts visualization
- Reset and navigation controls

### Scalability
- Easy to add new fields
- Services can be extended
- Resource caching with `@st.cache_resource`
- Well-organized session state

## Comparison: Before vs After

| Aspect | Before | After |
|---------|-------|--------|
| **Files** | 3 monolithic files | 6 modular files |
| **Stages** | 1 single stage | 3 progressive stages |
| **Interaction** | Generation only | Generation + Interactive Chat |
| **Organization** | Mixed logic | Clear separation (MVC-like) |
| **Configuration** | Hardcoded | Centralized in config |
| **Extensibility** | Difficult | Easy (add services) |
| **Maintenance** | Complicated | Simplified |

## Suggested Next Steps

1. **Security**: Move API keys to environment variables
2. **Persistence**: Save characters to database
3. **Export**: Allow character download (JSON/PDF)
4. **Gallery**: View previously created characters
5. **Sharing**: Share characters between users
6. **Multi-language**: Support multiple languages
7. **Voice**: Integrate TTS for character "voice"
8. **Advanced Chat**: Add tools to agent (search, image generation during chat)

## Debugging

### Important logs:
- `PromptGenerationService`: Shows generated prompts
- `ImageGenerationService`: Shows costs and execution time
- `CharacterAgent`: Verbose mode available for debugging

### Common troubleshooting:
- **API key error**: Check `config.py`
- **Images don't generate**: Check Holara credits
- **Chat doesn't work**: Verify agent initialization
- **Parsing error**: Check GPT response format

## Article Notes

### Key points to highlight:

1. **Architecture evolution**: From procedural to service-oriented
2. **User journey**: How stage division improves experience
3. **LangChain integration**: How to implement conversational agents
4. **Session state**: State management in Streamlit
5. **Prompting strategies**: Different prompts for different stages
6. **Error handling**: Robust error handling in each layer

### Technical concepts covered:
- Dataclasses for models
- Service layer pattern
- Conversational AI with memory
- API integration best practices
- Streamlit advanced features
