"""
Sidebar navigation and command hub component
"""
import streamlit as st


def render_character_selector(current_idx):
    """Render character selection buttons in sidebar"""
    st.sidebar.markdown("### 👥 Character Selection")
    char_col1, char_col2 = st.sidebar.columns(2)
    
    with char_col1:
        if st.button(
            f"Character 1\n{'✓' if current_idx == 0 else '○'}",
            use_container_width=True,
            type="primary" if current_idx == 0 else "secondary"
        ):
            st.session_state.current_character_idx = 0
            st.rerun()
    
    with char_col2:
        if st.button(
            f"Character 2\n{'✓' if current_idx == 1 else '○'}",
            use_container_width=True,
            type="primary" if current_idx == 1 else "secondary"
        ):
            st.session_state.current_character_idx = 1
            st.rerun()


def render_navigation_hub(current_char, current_stage, set_stage_fn, init_chat_fn, reset_char_fn):
    """Render the navigation command hub in sidebar"""
    st.sidebar.markdown("---")
    
    # Navigation Hub
    st.sidebar.markdown("### 🧭 Navigation Hub")
    
    # Stage indicators
    st.sidebar.markdown("**Quick Navigation:**")
    nav_col1, nav_col2 = st.sidebar.columns(2)
    
    with nav_col1:
        if st.button("🔙 Stage 1: Appearance", use_container_width=True, 
                     type="secondary" if current_stage != 1 else "primary"):
            set_stage_fn(1)
            st.rerun()
    
    with nav_col2:
        if current_char.name:
            if st.button("🎭 Stage 2: Personality", use_container_width=True, 
                        type="secondary" if current_stage != 2 else "primary"):
                set_stage_fn(2)
                st.rerun()
        else:
            st.button("🎭 Stage 2: Personality", disabled=True, use_container_width=True)
    
    if current_char.name:
        if st.button("💬 Stage 3: Chat", use_container_width=True, type="primary"):
            st.session_state.current_chat_idx = st.session_state.current_character_idx
            init_chat_fn()
            set_stage_fn(3)
            st.rerun()
    
    st.sidebar.markdown("---")
    
    # Quick Actions
    st.sidebar.markdown("### ⚡ Quick Actions")
    if st.button("🔄 Reset Current Character", use_container_width=True):
        reset_char_fn()
        set_stage_fn(1)
        st.rerun()
    
    # Group chat button (only if both characters exist)
    if current_char.name and st.session_state.characters[1].name:
        if st.button("🎬 Stage 4: Directed Scene", use_container_width=True, type="secondary"):
            set_stage_fn(4)
            st.rerun()


def render_character_status():
    """Render character status in sidebar"""
    st.sidebar.markdown("---")
    
    # Character Status
    st.sidebar.caption("📊 **Status**")
    char1 = st.session_state.characters[0]
    char2 = st.session_state.characters[1]
    
    status1 = "✓ Created" if char1.name else "○ Empty"
    status2 = "✓ Created" if char2.name else "○ Empty"
    st.sidebar.caption(f"Char 1: {status1} | Char 2: {status2}")
    
    st.sidebar.markdown("---")
    
    # Current Character Info
    current_char = st.session_state.characters[st.session_state.current_character_idx]
    if current_char.name:
        st.sidebar.markdown("### 📋 Current Character")
        st.sidebar.info(f"**{current_char.name}**")
        if current_char.personality.occupation:
            st.sidebar.caption(f"🎭 {current_char.personality.occupation}")
    else:
        st.sidebar.markdown("### 📋 Current Character")
        st.sidebar.info("No character selected")
