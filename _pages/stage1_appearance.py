"""
Stage 1: Character Appearance - Generate character from visual appearance
"""
import streamlit as st
import base64
from models.character import Character


def render_stage_1(services, get_current_character, set_current_character, set_current_stage):
    """Render Stage 1: Character Appearance"""
    st.title("🎨 Stage 1: Character Appearance")
    st.markdown(f"*Create Character {st.session_state.current_character_idx + 1}'s visual concept*")
    
    col1, col2 = st.columns([1, 2])
    
    with col1:
        st.subheader("⚙️ Settings")
        creativity = st.slider(
            "🔥 Creativity Level",
            min_value=0.1,
            max_value=1.0,
            value=0.5,
            step=0.1,
            help="Higher = more AI creativity"
        )
        st.session_state.creativity = creativity
        
        st.markdown("---")
        st.subheader("👤 Basic Appearance")
        
        char = get_current_character()
        char.appearance.species = st.text_input("Species", char.appearance.species, 
                                                placeholder="e.g., Human, Elf, Android")
        char.appearance.sex_gender = st.text_input("Sex/Gender", char.appearance.sex_gender,
                                                   placeholder="e.g., Female, Male, Non-binary")
        char.appearance.age = st.text_input("Age", char.appearance.age,
                                           placeholder="e.g., 16, Ancient, Unknown")
        char.appearance.physical_shape = st.text_input("Physical Shape", char.appearance.physical_shape,
                                                       placeholder="e.g., Athletic, Petite, Muscular")
        
        st.markdown("---")
        st.subheader("🎨 Visual Details")
        
        char.appearance.hair_details = st.text_input("Hair Details", char.appearance.hair_details,
                                                     placeholder="e.g., Long silver hair, ponytail")
        char.appearance.eye_details = st.text_input("Eye Details", char.appearance.eye_details,
                                                    placeholder="e.g., Bright blue eyes, cat-like")
        char.appearance.main_colors = st.text_input("Main Colors", char.appearance.main_colors,
                                                    placeholder="e.g., Blue and white, Red and gold")
        char.appearance.clothing = st.text_area("Clothing", char.appearance.clothing,
                                               placeholder="e.g., Black kimono with golden details")
        char.appearance.artstyle = st.text_input("Art Style", char.appearance.artstyle,
                                                placeholder="e.g., Studio Ghibli, Cyberpunk anime")
        
        st.markdown("---")
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("✨ Generate Character", type="primary", use_container_width=True):
                if _generate_character(char, services, set_current_character):
                    set_current_stage(2)
                    st.rerun()
        
        # Show "Continue to Personality" button if character already generated
        with col_btn2:
            char = get_current_character()
            if char.name:  # Character has been generated
                if st.button("→ Continue to Personality", use_container_width=True):
                    set_current_stage(2)
                    st.rerun()
    
    with col2:
        char = get_current_character()
        
        # Show generated image if it exists
        if char.images_base64 and len(char.images_base64) > 0:
            st.subheader("🖼️ Current Character Concept")
            st.image(base64.b64decode(char.images_base64[0]), use_container_width=True)
            with st.expander("View Prompt"):
                st.code(char.image_prompts[0])
        else:
            # Show instructions only if no character generated yet
            st.subheader("📖 Instructions")
            st.info("""
            **Welcome to the AI Character Creator!**
            
            ### 📝 How to Use:
            
            **Stage 1 - Appearance** (Current)
            - Fill in appearance details on the left
            - Click "Generate Character" to create your character
            - Adjust creativity level for different AI styles
            
            **Stage 2 - Personality**
            - Review and edit character details
            - Fine-tune personality, backstory, and background
            - Regenerate backstory with different creativity levels
            
            **Stage 3 - Chat**
            - Talk one-on-one with your character
            - Characters maintain their personality and context
            
            **Stage 4 - Group Chat** (Unlocked after creating 2 characters)
            - Chat with both characters simultaneously
            - Agents interact with each other and you!
            
            ### 💡 Tips:
            - You can create up to 2 characters independently
            - Each character maintains separate chat history
            - Edit appearance anytime without regenerating
            - Use the sidebar navigation hub for quick access
            
            Ready? Fill in the fields and click "Generate Character"!
            """)


def _generate_character(char, services, set_current_character):
    """Helper function to generate character from appearance"""
    appearance_str = char.appearance.to_prompt_string()
    
    if not appearance_str:
        st.error("Please fill in at least one appearance field!")
        return False
    
    with st.spinner("🎨 Generating character concept..."):
        # Generate prompt and basic info
        creativity = st.session_state.creativity
        result = services['prompt'].generate_initial_prompts(appearance_str, creativity)
        
        if not result:
            st.error("Failed to generate prompt. Please try again.")
            return False
        
        # Store prompt and name
        char.image_prompts = result['prompts']
        char.name = result['name']
        char.personality.backstory = result.get('personality_sketch', '')
        
        # Generate image
        with st.spinner("🖼️ Creating character image..."):
            image_result = services['image'].generate_single_image(char.image_prompts[0])
            if not image_result:
                st.error("Failed to generate image. Please try again.")
                return False
            char.images_base64 = [image_result['image_base64']]
        
        set_current_character(char)
        return True
