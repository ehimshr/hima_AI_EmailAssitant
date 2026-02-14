import streamlit as st
import os
import sys
import uuid
import json
from langchain_core.messages import HumanMessage
from fpdf import FPDF

# Add the project root to sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.core.graph import create_graph
from src.utils.learning import save_email_history

st.set_page_config(page_title="AI Email Assistant", layout="wide")

st.title("✉️ AI-Powered Email Assistant")

# Sidebar for configuration
with st.sidebar:
    st.header("Configuration")
    try:
        with open('src/data/user_profiles.json', 'r') as f:
            profiles = json.load(f)
            profile_names = list(profiles.keys())
    except:
        profile_names = ["default"]
        
    selected_profile = st.selectbox("Select Profile", profile_names)
    
    # Tone Selector
    tone_mode = st.radio("Tone Mode", ["Normal", "Formal", "Casual", "Assertive"])
    
    # Intent Selector
    intent_mode = st.selectbox("Intent (Optional)", ["Auto", "Outreach", "Follow-up", "Reply", "Apology", "Informational"])
    
    # Metadata (Optional)
    with st.expander("Additional Metadata"):
        recipient_override = st.text_input("Recipient Name/Email (Override)")
        extra_constraints = st.text_input("Extra Constraints (e.g., 'no jargon')")
    
    st.markdown("---")
    st.markdown("### Debug Info")
    if st.checkbox("Show Graph State"):
        st.session_state.show_debug = True
    else:
        st.session_state.show_debug = False

# Initialize thread_id if not present
if "thread_id" not in st.session_state:
    st.session_state.thread_id = str(uuid.uuid4())

# Main content
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"]):
        st.markdown(message["content"])
        if "steps" in message and message["steps"]:
            with st.expander("View Agent Steps"):
                for step in message["steps"]:
                    st.caption(f"**Agent: {step['agent']}**")
                    st.write(step['output'])

prompt = st.chat_input("What email would you like to draft?")

if prompt:
    # Add user message to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    # Invoke the graph
    graph = create_graph()
    
    # Configuration for persistence
    config = {"configurable": {"thread_id": st.session_state.thread_id}}
    
    # State update (incremental)
    inputs = {
        "messages": [HumanMessage(content=prompt)],
        "user_info": {
            "profile": selected_profile, 
            "tone_mode": tone_mode,
            "intent_mode": intent_mode,
            "recipient_override": recipient_override,
            "extra_constraints": extra_constraints
        }
    }
    
    with st.spinner("Drafting email..."):
        try:
            # Stream the graph execution
            final_email = ""
            steps_log = []
            
            step_placeholder = st.empty()
            
            # Temporary container to show steps in real-time
            with step_placeholder.container():
                for event in graph.stream(inputs, config=config):
                    # Visualize Agent Steps
                    for node_name, state_update in event.items():
                        steps_log.append({"agent": node_name, "output": state_update})
                        with st.expander(f"Agent: {node_name}", expanded=True):
                            st.write(state_update)
                    
                    # Capture email draft if in final state
                    for key, value in event.items():
                        if "final_email" in value and value["final_email"]:
                             final_email = value["final_email"]
            
            if final_email:
                st.session_state.messages.append({
                    "role": "assistant", 
                    "content": final_email,
                    "steps": steps_log
                })
                st.rerun() # Rerun to show the message in the chat loop above and then show editor below

        except Exception as e:
            st.error(f"Error: {str(e)}")

# Display Editor for the last generated email
if st.session_state.messages and st.session_state.messages[-1]["role"] == "assistant":
    last_email = st.session_state.messages[-1]["content"]
    st.markdown("### 📝 Editor & Actions")
    edited_email = st.text_area("Edit Draft", value=last_email, height=300)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("💾 Save to History (Learn)"):
            save_email_history(edited_email, selected_profile, "User Edited Topic") # Topic extraction simplified here
            st.success("Saved! The agent will learn from this style.")
            
    with col2:
        if st.button("📄 Export to PDF"):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", size=12)
            # Handle unicode slightly better by replacing common non-latin chars if needed, 
            # but standard FPDF has limits. 
            safe_text = edited_email.encode('latin-1', 'replace').decode('latin-1')
            pdf.multi_cell(0, 10, safe_text)
            
            pdf_output = pdf.output(dest='S').encode('latin-1')
            st.download_button(
                label="Download PDF",
                data=pdf_output,
                file_name="email_draft.pdf",
                mime="application/pdf"
            )
            
    with col3:
        if st.button("Refine Draft"):
             st.session_state.messages.append({"role": "user", "content": "Refine this draft based on my edits."})
             st.rerun()
