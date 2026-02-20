"""
Stage 3: Individual Character Chat - Talk one-on-one with created character
"""
import streamlit as st
import base64


def render_stage_3(services):
    """Render Stage 3: Chat with Individual Character"""
    char = st.session_state.characters[st.session_state.current_chat_idx]
    
    # Main layout: chat on left, character info on right
    col_chat, col_info = st.columns([2, 1])
    
    with col_chat:
        st.title(f"💬 Chat with {char.name}")
        st.markdown("---")
        
        # Chat interface
        chat_container = st.container()
        
        with chat_container:
            # Display chat history
            for message in st.session_state.chat_history[st.session_state.current_chat_idx]:
                with st.chat_message(message["role"]):
                    st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input(f"Talk to {char.name}..."):
            # Add user message to history
            st.session_state.chat_history[st.session_state.current_chat_idx].append({"role": "user", "content": prompt})
            
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get character response
            with st.chat_message("assistant"):
                with st.spinner(f"{char.name} is thinking..."):
                    response = services['agent'].chat_with_character(prompt, idx=st.session_state.current_chat_idx)
                    st.markdown(response)
            
            # Add assistant response to history
            st.session_state.chat_history[st.session_state.current_chat_idx].append({"role": "assistant", "content": response})
    
    with col_info:
        st.subheader("📋 Character Info")
        
        # Display character image
        if char.images_base64:
            st.image(base64.b64decode(char.images_base64[0]), use_container_width=True)
        
        st.markdown("---")
        
        # Character details
        st.markdown(f"**Name:** {char.name}")
        st.markdown(f"**Occupation:** {char.personality.occupation or 'Unknown'}")
        st.markdown(f"**Personality:** {char.personality.personality_traits or 'To be discovered...'}")
        st.markdown(f"**Universe:** {char.personality.context_universe or 'Unknown'}")
        st.markdown(f"**Messages:** {len(st.session_state.chat_history[st.session_state.current_chat_idx])}")
        
        st.markdown("---")
        
        # Backstory expander
        with st.expander("📖 Backstory"):
            st.markdown(char.personality.backstory)
    
    # Sidebar controls
    with st.sidebar:
        st.subheader("Chat Controls")
        
        if st.button("🔄 Reset Conversation"):
            services['agent'].reset_agent(idx=st.session_state.current_chat_idx)
            st.session_state.chat_history[st.session_state.current_chat_idx] = []
            st.rerun()
        
        if st.button("← Edit Character"):
            st.session_state.current_character_idx = st.session_state.current_chat_idx
            st.session_state.stages[st.session_state.current_character_idx] = 2
            st.rerun()
        
        if st.button("📝 Create/Edit Another"):
            # Switch to the other character slot
            st.session_state.current_character_idx = 1 - st.session_state.current_character_idx
            st.session_state.stages[st.session_state.current_character_idx] = 1
            st.rerun()
        
        st.markdown("---")
        st.subheader("Available Characters")
        char1 = st.session_state.characters[0]
        char2 = st.session_state.characters[1]
        
        if char1.name:
            if st.button(f"💬 {char1.name}", use_container_width=True):
                st.session_state.current_chat_idx = 0
                st.rerun()
        
        if char2.name:
            if st.button(f"💬 {char2.name}", use_container_width=True):
                st.session_state.current_chat_idx = 1
                st.rerun()
        
        # Group chat button if both characters exist
        if char1.name and char2.name:
            st.markdown("---")
            if st.button(f"👥 Group Chat: {char1.name} & {char2.name}", use_container_width=True, type="primary"):
                st.session_state.stages[st.session_state.current_character_idx] = 4
                st.rerun()
