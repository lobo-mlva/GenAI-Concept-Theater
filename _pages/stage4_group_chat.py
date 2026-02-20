"""
Stage 4: Directed Scene - Characters interact under director's guidance
"""
import streamlit as st
import time
from models.character import Character


def render_stage_4(services, set_current_stage):
    """Render Stage 4: Directed Scene with Both Characters"""
    char1 = st.session_state.characters[0]
    char2 = st.session_state.characters[1]
    
    # Initialize scene state
    if "scene_active" not in st.session_state:
        st.session_state.scene_active = False
    if "scene_instruction" not in st.session_state:
        st.session_state.scene_instruction = ""
    if "scene_paused" not in st.session_state:
        st.session_state.scene_paused = False
    if "scene_running" not in st.session_state:
        st.session_state.scene_running = False
    
    # Check if both characters exist
    if not char1.name or not char2.name:
        st.error("⚠️ Both characters need to be created for directed scenes!")
        if st.button("← Back to Chat"):
            set_current_stage(3)
            st.rerun()
        return
    
    # Ensure director exists
    director = services['agent'].create_director()
    
    # Ensure agents exist for both characters
    if not services['agent'].has_agent(0):
        services['agent'].create_agent(char1.get_full_description(), char1.name, 0)
    if not services['agent'].has_agent(1):
        services['agent'].create_agent(char2.get_full_description(), char2.name, 1)
    
    st.title("🎬 Directed Scene")
    st.markdown(f"*{char1.name} & {char2.name} - Orchestrated by the Director*")
    st.markdown("---")
    
    # Scene Setup Area (when no scene is active)
    if not st.session_state.scene_active:
        _render_scene_setup(services, char1, char2, director)
    else:
        _render_active_scene(services, char1, char2)
    
    # Sidebar controls
    _render_sidebar_controls(services, set_current_stage, char1, char2)


def _render_scene_setup(services, char1, char2, director):
    """Render the scene setup interface"""
    st.subheader("📝 Scene Setup")
    
    col1, col2 = st.columns([3, 1])
    
    with col1:
        scene_input = st.text_area(
            "Describe the scene or situation:",
            placeholder="e.g., 'The characters meet at a coffee shop during a rainy afternoon...'",
            height=100,
            key="scene_input_area"
        )
    
    with col2:
        st.markdown("**Or let the Director suggest:**")
        if st.button("🎲 Suggest Scene", use_container_width=True):
            with st.spinner("Director is thinking..."):
                char1_desc = char1.get_full_description()
                char2_desc = char2.get_full_description()
                suggestion = director.suggest_scene(
                    char1_desc, char1.name,
                    char2_desc, char2.name
                )
                st.session_state.suggested_scene = suggestion
                st.rerun()
    
    # Show suggestion if available
    if "suggested_scene" in st.session_state and st.session_state.suggested_scene:
        st.info(f"🎬 **Director's Suggestion:** {st.session_state.suggested_scene}")
        col_use, col_clear = st.columns(2)
        with col_use:
            if st.button("✓ Use This Scene", use_container_width=True):
                st.session_state.scene_instruction = st.session_state.suggested_scene
                st.session_state.suggested_scene = ""
                _start_scene(services)
                st.rerun()
        with col_clear:
            if st.button("✗ Clear", use_container_width=True):
                st.session_state.suggested_scene = ""
                st.rerun()
    
    # Start scene button
    if scene_input:
        if st.button("🎬 Start Scene", type="primary", use_container_width=True):
            st.session_state.scene_instruction = scene_input
            _start_scene(services)
            st.rerun()


def _start_scene(services):
    """Initialize and start a new scene"""
    st.session_state.scene_active = True
    st.session_state.scene_paused = False
    st.session_state.scene_running = True  # Auto-run enabled
    st.session_state.group_chat_history = []
    services['agent'].reset_director()


def _render_active_scene(services, char1, char2):
    """Render the active scene with director controls"""
    
    # Scene info bar
    col_info, col_controls = st.columns([3, 1])
    with col_info:
        st.caption(f"📜 **Scene:** {st.session_state.scene_instruction[:100]}...")
    with col_controls:
        if st.session_state.scene_paused:
            st.warning("⏸️ Paused")
        elif st.session_state.scene_running:
            st.success("▶️ Running")
        else:
            st.info("⏹️ Stopped")
    
    st.markdown("---")
    
    # Display scene history
    scene_container = st.container()
    with scene_container:
        for message in st.session_state.group_chat_history:
            role = message.get("role", "assistant")
            
            if role == "director":
                # Director narration - styled differently
                st.markdown(f"*🎬 {message['content']}*")
            elif role == "user":
                with st.chat_message("user"):
                    st.markdown(f"**[Direction]** {message['content']}")
            else:
                # Character dialogue
                char_name = message.get("character", "Character")
                with st.chat_message("assistant"):
                    st.markdown(f"**{char_name}:** {message['content']}")
    
    # Scene controls
    st.markdown("---")
    
    if st.session_state.scene_paused:
        _render_paused_controls(services, char1, char2)
    else:
        _render_playing_controls(services, char1, char2)
    
    # Auto-run the scene
    if st.session_state.scene_running and not st.session_state.scene_paused:
        _auto_run_scene(services, char1, char2)


def _render_playing_controls(services, char1, char2):
    """Render controls when scene is playing"""
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        if st.session_state.scene_running:
            if st.button("⏸️ Pause Scene", type="primary", use_container_width=True):
                st.session_state.scene_running = False
                st.session_state.scene_paused = True
                st.rerun()
        else:
            if st.button("▶️ Resume Auto-Play", type="primary", use_container_width=True):
                st.session_state.scene_running = True
                st.rerun()
    
    with col2:
        if st.button("⏭️ Step", use_container_width=True, help="Advance one step manually"):
            st.session_state.scene_running = False
            _advance_scene(services, char1, char2)
            st.rerun()
    
    with col3:
        if st.button("⏹️ End Scene", use_container_width=True):
            st.session_state.scene_active = False
            st.session_state.scene_paused = False
            st.session_state.scene_running = False
            st.rerun()
    
    # Quick user interjection
    if prompt := st.chat_input("Interject or give the director new instructions..."):
        st.session_state.scene_running = False  # Pause when user interjects
        st.session_state.scene_instruction = f"{st.session_state.scene_instruction}\n\nNew direction: {prompt}"
        st.session_state.group_chat_history.append({"role": "user", "content": prompt})
        _advance_scene(services, char1, char2)
        st.session_state.scene_running = True  # Resume after interjection
        st.rerun()


def _render_paused_controls(services, char1, char2):
    """Render controls when scene is paused"""
    st.subheader("⏸️ Scene Paused - Make Adjustments")
    
    # Tweak options
    tweak_input = st.text_area(
        "Adjust the scene direction:",
        placeholder="e.g., 'Make the scene more dramatic' or 'Have Character 1 be more assertive'",
        height=80
    )
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("▶️ Resume Auto-Play", type="primary", use_container_width=True):
            if tweak_input:
                st.session_state.scene_instruction = f"{st.session_state.scene_instruction}\n\nAdjustment: {tweak_input}"
                st.session_state.group_chat_history.append({"role": "user", "content": f"[Adjustment] {tweak_input}"})
            st.session_state.scene_paused = False
            st.session_state.scene_running = True
            st.rerun()
    
    with col2:
        if st.button("🔄 Redo Last", use_container_width=True):
            # Remove last character response and director narration
            if len(st.session_state.group_chat_history) >= 2:
                st.session_state.group_chat_history = st.session_state.group_chat_history[:-2]
            st.session_state.scene_paused = False
            st.session_state.scene_running = True
            st.rerun()
    
    with col3:
        if st.button("⏹️ End Scene", use_container_width=True):
            st.session_state.scene_active = False
            st.session_state.scene_paused = False
            st.session_state.scene_running = False
            st.rerun()


def _auto_run_scene(services, char1, char2):
    """Automatically advance the scene with visual feedback"""
    # Use a placeholder to show progress
    progress_placeholder = st.empty()
    
    with progress_placeholder.container():
        with st.spinner("🎬 Director is orchestrating the next moment..."):
            time.sleep(0.5)  # Brief pause for visual flow
            _advance_scene(services, char1, char2)
    
    # Clear placeholder and rerun to show new content
    progress_placeholder.empty()
    st.rerun()


def _advance_scene(services, char1, char2):
    """Advance the scene by one interaction"""
    director = services['agent'].get_director()
    
    # Build scene context from history and track who has spoken
    scene_so_far = ""
    char1_spoke = False
    char2_spoke = False
    last_speaker = ""
    previous_narrations = []
    
    for msg in st.session_state.group_chat_history:
        if msg["role"] == "director":
            # Collect previous narrations to avoid repetition
            previous_narrations.append(msg['content'])
        elif msg["role"] == "user":
            scene_so_far += f"[Direction: {msg['content']}]\n"
        else:
            char_name = msg.get('character', '')
            scene_so_far += f"{char_name}: \"{msg['content']}\"\n"
            last_speaker = char_name
            # Track which characters have spoken
            if char_name == char1.name:
                char1_spoke = True
            elif char_name == char2.name:
                char2_spoke = True
    
    # Get director's direction
    char1_desc = char1.get_full_description()
    char2_desc = char2.get_full_description()
    
    direction = director.direct_scene(
        st.session_state.scene_instruction,
        char1.name, char1_desc,
        char2.name, char2_desc,
        scene_so_far,
        char1_spoke=char1_spoke,
        char2_spoke=char2_spoke,
        last_speaker=last_speaker,
        previous_narrations=previous_narrations
    )
    
    # Add director narration only if it's meaningful and not empty
    narration = direction.get("narration", "").strip()
    if narration and len(narration) > 3:
        st.session_state.group_chat_history.append({
            "role": "director",
            "content": narration
        })
    
    # Get character response
    next_char = direction.get("next_character", char1.name)
    char_prompt = direction.get("prompt_for_character", "Continue the scene.")
    
    # Determine which character and get response
    if next_char == char2.name:
        idx = 1
        other_name = char1.name
    else:
        idx = 0
        other_name = char2.name
    
    response = services['agent'].scene_response(
        char_prompt, idx, other_name, scene_so_far
    )
    
    if response:
        st.session_state.group_chat_history.append({
            "role": "assistant",
            "character": next_char,
            "content": response
        })
    
    # Check if scene is complete
    if direction.get("scene_complete", False):
        st.session_state.group_chat_history.append({
            "role": "director",
            "content": "🎬 *The scene reaches its natural conclusion.*"
        })
        st.session_state.scene_paused = True


def _render_sidebar_controls(services, set_current_stage, char1, char2):
    """Render sidebar controls for the directed scene"""
    with st.sidebar:
        st.subheader("🎬 Scene Controls")
        
        if st.button("🔄 New Scene", use_container_width=True):
            st.session_state.scene_active = False
            st.session_state.scene_paused = False
            st.session_state.scene_running = False
            st.session_state.group_chat_history = []
            st.session_state.scene_instruction = ""
            if "suggested_scene" in st.session_state:
                st.session_state.suggested_scene = ""
            services['agent'].reset_director()
            st.rerun()
        
        if st.button("← Back to Individual Chat", use_container_width=True):
            st.session_state.scene_running = False
            set_current_stage(3)
            st.rerun()
        
        st.markdown("---")
        st.caption("**Cast**")
        st.caption(f"• {char1.name}")
        st.caption(f"• {char2.name}")
        st.caption(f"• 🎬 Director (AI)")
        
        st.markdown("---")
        st.caption(f"**Scene Events:** {len(st.session_state.group_chat_history)}")
