"""
AI Character Creator - Main Application Router
Refactored for modularity and clean code organization
"""
import streamlit as st
from models.character import Character
from services.prompt_service import PromptGenerationService
from services.image_service import ImageGenerationService
from services.agent_service import AgentService

# Import stage pages
from _pages.stage1_appearance import render_stage_1
from _pages.stage2_personality import render_stage_2
from _pages.stage3_chat import render_stage_3
from _pages.stage4_group_chat import render_stage_4

# Import components
from components.sidebar_navigation import (
    render_character_selector,
    render_navigation_hub,
    render_character_status
)

# ==================== PAGE CONFIGURATION ====================
st.set_page_config(
    page_title="AI Character Creator",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==================== SERVICES INITIALIZATION ====================
@st.cache_resource
def get_services():
    """Initialize and cache services"""
    return {
        'prompt': PromptGenerationService(),
        'image': ImageGenerationService(),
        'agent': AgentService()
    }

services = get_services()

# ==================== SESSION STATE INITIALIZATION ====================
def initialize_session_state():
    """Initialize all required session state variables"""
    if 'stages' not in st.session_state:
        st.session_state.stages = [1, 1]
    if 'characters' not in st.session_state:
        st.session_state.characters = [Character(), Character()]
    if 'current_character_idx' not in st.session_state:
        st.session_state.current_character_idx = 0
    if 'chat_history' not in st.session_state:
        st.session_state.chat_history = [[], []]
    if 'current_chat_idx' not in st.session_state:
        st.session_state.current_chat_idx = 0
    if 'group_chat_history' not in st.session_state:
        st.session_state.group_chat_history = []

initialize_session_state()

# ==================== HELPER FUNCTIONS ====================
def get_current_stage():
    """Get the current stage for active character"""
    return st.session_state.stages[st.session_state.current_character_idx]

def set_current_stage(stage):
    """Set the stage for active character"""
    st.session_state.stages[st.session_state.current_character_idx] = stage

def get_current_character():
    """Get the currently selected character"""
    return st.session_state.characters[st.session_state.current_character_idx]

def set_current_character(char):
    """Update the currently selected character"""
    st.session_state.characters[st.session_state.current_character_idx] = char

def reset_current_character():
    """Reset the current character"""
    set_current_character(Character())

# ==================== SIDEBAR RENDERING ====================
if get_current_stage() in [1, 2]:
    render_character_selector(st.session_state.current_character_idx)
    render_navigation_hub(
        get_current_character(),
        get_current_stage(),
        set_current_stage,
        lambda: services['agent'].create_agent(
            get_current_character().get_full_description(),
            get_current_character().name,
            idx=st.session_state.current_chat_idx
        ),
        reset_current_character
    )
    render_character_status()

# ==================== MAIN ROUTER ====================
current_stage = get_current_stage()

if current_stage == 1:
    render_stage_1(services, get_current_character, set_current_character, set_current_stage)

elif current_stage == 2:
    render_stage_2(services, get_current_character, set_current_character, set_current_stage)

elif current_stage == 3:
    render_stage_3(services)

elif current_stage == 4:
    render_stage_4(services, set_current_stage)
