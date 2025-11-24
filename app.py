import streamlit as st
import json
import os
from datetime import datetime
from dotenv import load_dotenv
from generator import ResearchGenerator
from utils import (
    load_conversation_history,
    save_conversation_history,
    load_account_plan,
    save_account_plan,
    export_plan_to_json,
    format_plan_display
)

# Load environment variables from .env file
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Company Research Assistant",
    page_icon="🔍",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        margin-bottom: 1rem;
    }
    .chat-message {
        padding: 1rem;
        border-radius: 0.5rem;
        margin-bottom: 1rem;
    }
    .user-message {
        background-color: #000000;
        margin-left: 20%;
    }
    .assistant-message {
        background-color: #000000;
        margin-right: 20%;
    }
    .plan-section {
        background-color: #000000;
        border: 1px solid #e0e0e0;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
    }
    .status-message {
        padding: 0.5rem;
        border-radius: 0.3rem;
        background-color: #000000;
        color: #856404;
        margin-bottom: 1rem;
    }
    </style>
""", unsafe_allow_html=True)

# Initialize session state
if 'messages' not in st.session_state:
    st.session_state.messages = load_conversation_history()
if 'current_plan' not in st.session_state:
    st.session_state.current_plan = load_account_plan()
if 'research_data' not in st.session_state:
    st.session_state.research_data = None
if 'generator' not in st.session_state:
    st.session_state.generator = None
if 'editing_section' not in st.session_state:
    st.session_state.editing_section = None

# Get API key from environment
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Initialize generator if API key exists
if GEMINI_API_KEY and not st.session_state.generator:
    try:
        st.session_state.generator = ResearchGenerator(GEMINI_API_KEY)
    except Exception as e:
        st.error(f"Failed to initialize AI: {str(e)}")

# Sidebar
with st.sidebar:
    # Plan status
    st.subheader("📊 Current Status")
    if st.session_state.current_plan:
        st.success("✅ Account Plan Generated")
        
        # Export button
        if st.button("📥 Export Plan", use_container_width=True):
            plan_json = export_plan_to_json(st.session_state.current_plan)
            st.download_button(
                label="Download JSON",
                data=plan_json,
                file_name=f"account_plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json",
                mime="application/json",
                use_container_width=True
            )
    else:
        st.info("ℹ️ No plan generated yet")
    
    st.divider()
    
    # Action buttons
    st.subheader("🔧 Actions")
    
    if st.button("🗑️ Clear Chat", use_container_width=True):
        st.session_state.messages = []
        save_conversation_history([])
        st.rerun()
    
    if st.button("🔄 Clear Plan", use_container_width=True):
        st.session_state.current_plan = None
        st.session_state.research_data = None
        save_account_plan(None)
        st.rerun()
    
    st.divider()
    with st.expander("📖 How to Use"):
        st.markdown("""
        **Steps:**
        1. Ask to research a company (e.g., "Research Tesla")
        2. Review the research findings
        3. Request to generate an account plan
        4. Move to the "Account Plan" tab to view and edit
        5. Click on the edit buttons to modify sections as needed
        6. Export the plan as JSON using the sidebar button
        
        **Example Queries:**
        - "Research Microsoft"
        - "Generate account plan"
        - "Find information on Apple Inc"
        """)
    

# Main content
st.markdown('<p class="main-header">🔍 Company Research Assistant</p>', unsafe_allow_html=True)
st.markdown("AI-powered company research and account plan generation")

# Check if API key is available
if not GEMINI_API_KEY:
    st.error("⚠️ API Key Not Found!")
    st.info("Please create a .env file in your project directory with:")
    st.code("GEMINI_API_KEY=your_actual_api_key_here")
    st.info("Get your free API key from: https://makersuite.google.com/app/apikey")
    st.stop()

# Create tabs
tab1, tab2 = st.tabs(["💬 Chat", "📄 Account Plan"])

with tab1:
    # Chat interface
    chat_container = st.container()
    
    with chat_container:
        # Display chat messages
        for message in st.session_state.messages:
            role = message.get('role', 'assistant')
            content = message.get('content', '')
            msg_type = message.get('type', 'text')
            
            if role == 'user':
                st.markdown(f'<div class="chat-message user-message"><strong>You:</strong><br>{content}</div>', 
                           unsafe_allow_html=True)
            else:
                if msg_type == 'status':
                    st.markdown(f'<div class="status-message">🔄 {content}</div>', 
                               unsafe_allow_html=True)
                elif msg_type == 'research':
                    with st.expander("🔍 Research Results", expanded=True):
                        st.markdown(content)
                else:
                    st.markdown(f'<div class="chat-message assistant-message"><strong>Assistant:</strong><br>{content}</div>', 
                               unsafe_allow_html=True)
    
    # Chat input
    st.divider()
    
    col1, col2 = st.columns([5, 1])
    
    with col1:
        user_input = st.text_input(
            "Message",
            placeholder="Type your message here... (e.g., 'Research Tesla')",
            label_visibility="collapsed",
            key="user_input"
        )
    
    with col2:
        send_button = st.button("Send 📤", use_container_width=True)
    
    # Handle user input
    if send_button and user_input and st.session_state.generator:
        # Add user message
        st.session_state.messages.append({
            'role': 'user',
            'content': user_input,
            'timestamp': datetime.now().isoformat()
        })
        save_conversation_history(st.session_state.messages)
        
        # Process the request
        with st.spinner("Processing..."):
            # Check if it's a research request
            if any(keyword in user_input.lower() for keyword in ['research', 'tell me about', 'find information', 'search']):
                # Research mode
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': '🔍 Starting research...',
                    'type': 'status',
                    'timestamp': datetime.now().isoformat()
                })
                
                # Perform research
                research_result = st.session_state.generator.research_company(user_input)
                st.session_state.research_data = research_result
                
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': research_result,
                    'type': 'research',
                    'timestamp': datetime.now().isoformat()
                })
                
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': '📊 Research complete! Would you like me to generate an account plan based on this research?',
                    'type': 'text',
                    'timestamp': datetime.now().isoformat()
                })
                
            elif any(keyword in user_input.lower() for keyword in ['generate', 'create plan', 'yes', 'account plan']):
                # Generate plan
                if st.session_state.research_data:
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': '📝 Generating account plan...',
                        'type': 'status',
                        'timestamp': datetime.now().isoformat()
                    })
                    
                    plan = st.session_state.generator.generate_account_plan(
                        st.session_state.research_data
                    )
                    
                    if plan:
                        st.session_state.current_plan = plan
                        save_account_plan(plan)
                        
                        st.session_state.messages.append({
                            'role': 'assistant',
                            'content': '✅ Account plan generated successfully! Check the "Account Plan" tab to view and edit.',
                            'type': 'text',
                            'timestamp': datetime.now().isoformat()
                        })
                    else:
                        st.session_state.messages.append({
                            'role': 'assistant',
                            'content': '❌ Failed to generate account plan. Please try again.',
                            'type': 'text',
                            'timestamp': datetime.now().isoformat()
                        })
                else:
                    st.session_state.messages.append({
                        'role': 'assistant',
                        'content': 'Please provide research data first by asking me to research a company.',
                        'type': 'text',
                        'timestamp': datetime.now().isoformat()
                    })
            else:
                # General conversation
                response = st.session_state.generator.chat(user_input)
                st.session_state.messages.append({
                    'role': 'assistant',
                    'content': response,
                    'type': 'text',
                    'timestamp': datetime.now().isoformat()
                })
        
        save_conversation_history(st.session_state.messages)
        st.rerun()
    
    elif send_button and not st.session_state.generator:
        st.error("⚠️ AI not initialized. Check your .env file for GEMINI_API_KEY!")

with tab2:
    # Account Plan display and editing
    if st.session_state.current_plan:
        st.subheader("📄 Generated Account Plan")
        
        # Display each section
        for section_key, section_value in st.session_state.current_plan.items():
            section_title = section_key.replace('_', ' ').title()
            
            with st.container():
                col1, col2 = st.columns([5, 1])
                
                with col1:
                    st.markdown(f"### {section_title}")
                
                with col2:
                    if st.button(f"✏️ Edit", key=f"edit_{section_key}"):
                        st.session_state.editing_section = section_key
                
                # Show edit mode or display mode
                if st.session_state.editing_section == section_key:
                    new_content = st.text_area(
                        "Edit content",
                        value=section_value,
                        height=200,
                        key=f"textarea_{section_key}",
                        label_visibility="collapsed"
                    )
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("💾 Save", key=f"save_{section_key}", use_container_width=True):
                            st.session_state.current_plan[section_key] = new_content
                            save_account_plan(st.session_state.current_plan)
                            st.session_state.editing_section = None
                            st.success(f"✅ Updated {section_title}")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Cancel", key=f"cancel_{section_key}", use_container_width=True):
                            st.session_state.editing_section = None
                            st.rerun()
                else:
                    st.markdown(f'<div class="plan-section">{section_value}</div>', 
                               unsafe_allow_html=True)
                
                st.divider()
    else:
        st.info("ℹ️ No account plan generated yet. Start by researching a company in the Chat tab!")
        
        # Quick start guide
        with st.expander("🚀 Quick Start Guide"):
            st.markdown("""
            ### Getting Started:
            
            1. **Go to Chat tab**
            2. **Enter a research query**, for example:
               - "Research Tesla"
               - "Tell me about Microsoft"
               - "Find information on Apple"
            
            3. **Review the research** results
            
            4. **Generate the plan** by typing:
               - "Generate account plan"
               - "Create plan"
               - "Yes"
            
            5. **Come back to this tab** to view and edit your plan!
            """)

# Footer
st.divider()
st.markdown(
    '<p style="text-align: center; color: #666; font-size: 0.9rem;">Powered by Google Gemini (FREE) | Built with Streamlit</p>',
    unsafe_allow_html=True
)