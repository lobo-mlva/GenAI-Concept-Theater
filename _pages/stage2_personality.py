"""
Stage 2: Character Personality - Edit and enhance character personality & backstory
"""
import streamlit as st
import base64
from models.character import Character


def render_stage_2(services, get_current_character, set_current_character, set_current_stage):
    """Render Stage 2: Character Personality & Review"""
    char = get_current_character()
    
    st.title(f"🌟 Stage 2: {char.name}")
    st.markdown(f"*Review and enhance Character {st.session_state.current_character_idx + 1}*")
    
    # Display generated image (if it exists)
    if char.images_base64 and len(char.images_base64) > 0:
        st.image(base64.b64decode(char.images_base64[0]), caption="Character Concept", use_container_width=True)
        with st.expander("View Prompt"):
            st.code(char.image_prompts[0])
    else:
        st.warning("⚠️ No image generated yet. Redirecting to Stage 1...")
        set_current_stage(1)
        st.rerun()
    
    st.markdown("---")
    
    # Personality editing section
    with st.expander("✏️ Edit Personality & Background", expanded=True):
        st.markdown("### Character Details")
        
        col1, col2 = st.columns(2)
        
        with col1:
            char.name = st.text_input("Character Name", char.name)
            char.personality.personality_traits = st.text_area(
                "Personality Traits", 
                char.personality.personality_traits,
                placeholder="e.g., Brave, impulsive, loyal, has trust issues"
            )
            char.personality.skills_powers = st.text_area(
                "Skills/Powers", 
                char.personality.skills_powers,
                placeholder="e.g., Fire magic, master swordsman, can read minds"
            )
            char.personality.occupation = st.text_input(
                "Occupation", 
                char.personality.occupation,
                placeholder="e.g., Wandering mercenary, Royal knight"
            )
        
        with col2:
            char.personality.context_universe = st.text_area(
                "Context/Universe", 
                char.personality.context_universe,
                placeholder="e.g., Post-apocalyptic world, Fantasy kingdom"
            )
            char.personality.social_context = st.text_input(
                "Social Context", 
                char.personality.social_context,
                placeholder="e.g., Outcast, Noble family, Rebel leader"
            )
            char.personality.deformation_mark = st.text_input(
                "Marks/Scars", 
                char.personality.deformation_mark,
                placeholder="e.g., Dragon tattoo on left arm, Scar across eye"
            )
            char.personality.extras = st.text_area(
                "Extras", 
                char.personality.extras,
                placeholder="Additional details..."
            )
        
        st.markdown("### Backstory")
        char.personality.backstory = st.text_area(
            "Character Backstory (editable)",
            char.personality.backstory,
            height=200,
            help="You can edit the AI-generated backstory or write your own"
        )
        
        personality_creativity = st.slider(
            "Backstory Creativity",
            min_value=0.1,
            max_value=1.0,
            value=0.7,
            step=0.1
        )
        st.session_state.personality_creativity = personality_creativity
        
        if st.button("🔄 Regenerate Backstory", use_container_width=True):
            if _regenerate_backstory(char, services, set_current_character):
                st.success("Backstory updated!")
                st.rerun()
    
    # Update character
    set_current_character(char)
    
    # Action buttons
    st.markdown("---")
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        if st.button("← Back to Appearance", use_container_width=True):
            set_current_stage(1)
            st.rerun()
    with col2:
        if st.button("🔄 Reset Character", use_container_width=True):
            set_current_character(Character())
            set_current_stage(1)
            st.rerun()
    with col3:
        if st.button("💬 Chat with Character", type="primary", use_container_width=True):
            st.session_state.current_chat_idx = st.session_state.current_character_idx
            # Initialize chat agent
            char_desc = char.get_full_description()
            services['agent'].create_agent(char_desc, char.name, idx=st.session_state.current_chat_idx)
            set_current_stage(3)
            st.rerun()


def _regenerate_backstory(char, services, set_current_character):
    """Helper function to regenerate backstory"""
    appearance_str = char.appearance.to_prompt_string()
    personality_str = char.personality.to_prompt_string()
    
    with st.spinner("✍️ Creating detailed backstory..."):
        backstory = services['prompt'].generate_full_backstory(
            appearance_str, 
            personality_str, 
            char.name,
            creativity=st.session_state.get('personality_creativity', 0.7)
        )
        
        if backstory:
            char.personality.backstory = backstory
            set_current_character(char)
            return True
        return False
