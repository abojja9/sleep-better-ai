import streamlit as st
from typing import List
from phi.utils.log import logger
from src.agents.main_agent import reasoning_agent, settings

def init_session_state():
    """Initialize session state variables"""
    if "agent" not in st.session_state:
        st.session_state.agent = None
    if "agent_session_id" not in st.session_state:
        st.session_state.agent_session_id = None
    if "messages" not in st.session_state:
        st.session_state.messages = [
            {
                "role": "assistant", 
                "content": "Frodo: Welcome to Sleep Better! I'm Frodo, your personal sleep consultant. How may I assist you today?"
            }
        ]

def restart_agent():
    """Restart the agent and clear session state"""
    logger.debug("---*--- Restarting Agent ---*---")
    st.session_state.agent = None
    st.session_state.agent_session_id = None
    st.session_state.messages = [
        {
            "role": "assistant", 
            "content": "Frodo: Welcome to Sleep Better! I'm Frodo, your personal sleep consultant. How may I assist you today?"
        }
    ]
    st.rerun()

def format_agent_response(response: str) -> str:
    """Format the agent's response to start with 'Frodo:'"""
    if not response.startswith("Frodo:"):
        return f"Frodo: {response}"
    return response

def main():
    st.set_page_config(
        page_title="Sleep Better with Frodo",
        page_icon="🛏️",
        layout="wide"
    )
    
    # Initialize session state
    init_session_state()
    
    # Main title and subtitle
    st.title("🛏️ Sleep Better with Frodo")
    st.markdown("Your AI Sleep Consultant")
    
    # Sidebar configuration
    with st.sidebar:
        st.header("Configuration")
        
        # Get the Agent
        if "agent" not in st.session_state or st.session_state.agent is None:
            logger.info("---*--- Creating New Agent Session ---*---")
            st.session_state.agent = reasoning_agent
            
        # Create Agent session and store session_id
        try:
            if st.session_state.agent_session_id is None:
                st.session_state.agent_session_id = st.session_state.agent.create_session()
                logger.info(f"Created new session: {st.session_state.agent_session_id}")
        except Exception as e:
            st.warning("Could not create Agent session. Is the database running?")
            logger.error(f"Session creation error: {e}")
            return

        # Session Management
        if st.session_state.agent.storage:
            agent_session_ids: List[str] = st.session_state.agent.storage.get_all_session_ids()
            if agent_session_ids:
                new_session_id = st.selectbox(
                    "Session History", 
                    options=agent_session_ids,
                    index=agent_session_ids.index(st.session_state.agent_session_id) if st.session_state.agent_session_id in agent_session_ids else 0
                )
                
                if st.session_state.agent_session_id != new_session_id:
                    logger.info(f"Loading session: {new_session_id}")
                    st.session_state.agent_session_id = new_session_id
                    st.rerun()

        if st.button("New Conversation"):
            restart_agent()
            
        # Agent status indicators
        st.header("Agent Status")
        for agent_name, agent_config in settings['agents'].items():
            status = "✅ Active" if agent_config['enabled'] else "❌ Disabled"
            st.write(f"{agent_name.replace('_', ' ').title()}: {status}")
    
    # Load existing messages from agent memory
    agent_chat_history = st.session_state.agent.memory.get_messages()
    if len(agent_chat_history) > 0:
        logger.debug("Loading chat history")
        messages = []
        for msg in agent_chat_history:
            if msg.get("role") in ["user", "assistant"]:
                if "content" in msg and msg["content"] is not None:
                    messages.append(
                        {
                            "role": msg["role"],
                            "content": format_agent_response(msg["content"]) if msg["role"] == "assistant" else msg["content"]
                        }
                    )
            
        st.session_state.messages = messages
    
    # Display chat history
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("How can I help you today?"):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Get response from reasoning agent
        with st.chat_message("assistant"):
            message_placeholder = st.empty()
            
            # Show spinner while processing
            with st.spinner("Thinking..."):
                response = ""
                for delta in st.session_state.agent.run(message=prompt, stream=True):
                    if delta.content:
                        response += delta.content
                        formatted_response = format_agent_response(response)
                        message_placeholder.markdown(formatted_response)
            
            # After streaming is complete, replace placeholder with final message
            message_placeholder.markdown(format_agent_response(response))
                
            # Add final response to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": format_agent_response(response)
            })

if __name__ == "__main__":
    main()