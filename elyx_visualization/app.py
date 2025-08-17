import streamlit as st
import json
import pandas as pd
from datetime import datetime

# --- Page Configuration ---
st.set_page_config(
    page_title="Elyx Member Journey Visualization",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Data Loading and Caching ---
@st.cache_data
def load_data():
    """Loads conversations and events data from JSON files."""
    try:
        with open('data/conversations.json', 'r', encoding='utf-8') as f:
            conversations = json.load(f)
        with open('data/events.json', 'r', encoding='utf-8') as f:
            events = json.load(f)
        return conversations, events
    except FileNotFoundError as e:
        st.error(f"ERROR: A data file was not found. Please ensure 'conversations.json' and 'events.json' exist in the 'data/' folder")
        st.error(f"Details: {e}")
        return None, None
    except json.JSONDecodeError as e:
        st.error(f"ERROR: A JSON file is formatted incorrectly. Please validate your JSON files.")
        st.error(f"Details: {e}")
        return None, None

# --- Main Application ---

# Load the data
conversations_data, events_data = load_data()

# Stop the app if data loading fails
if not conversations_data or not events_data:
    st.stop()

# --- Sidebar ---
st.sidebar.title("Elyx Health Journey")
st.sidebar.markdown("### Rohan Patel")
st.sidebar.markdown(
    "This application visualizes the 8-month health journey of Rohan Patel, "
    "allowing for a deep dive into the decisions and conversations that shaped his protocol."
)

# --- Internal Metrics Calculation ---
def calculate_metrics(conv_data):
    """Processes conversation data to extract internal metrics."""
    df = pd.DataFrame(conv_data)
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Ensure 'month' column is created correctly
    if not df.empty:
        df['month'] = df['timestamp'].dt.to_period('M').astype(str)
    else:
        df['month'] = pd.Series(dtype=str)

    member_initiations = df[df['sender_role'] == 'member'].shape[0]
    team_responses = df[df['sender_role'] != 'member'].shape[0]
    
    # Count messages per team member
    team_messages = df[df['sender_role'] != 'member']
    messages_per_expert = team_messages['sender_name'].value_counts().reset_index()
    messages_per_expert.columns = ['Expert', 'Message Count']

    # Member initiations per month
    member_df = df[df['sender_role'] == 'member']
    if not member_df.empty:
        initiations_per_month = member_df.groupby('month').size().reset_index(name='count')
        initiations_per_month = initiations_per_month.set_index('month')
    else:
        initiations_per_month = pd.DataFrame(columns=['count'])

    return {
        "member_initiations": member_initiations,
        "team_responses": team_responses,
        "messages_per_expert": messages_per_expert,
        "initiations_per_month": initiations_per_month
    }

metrics = calculate_metrics(conversations_data)

st.sidebar.markdown("---")
st.sidebar.header("Journey at a Glance")
st.sidebar.metric("Total Member Messages", metrics['member_initiations'])
st.sidebar.metric("Total Team Responses", metrics['team_responses'])

# --- Main Panel with Tabs ---
tab1, tab2 = st.tabs(["Journey Timeline", "Internal Engagement Metrics"])

with tab1:
    st.header("Rohan's Journey Timeline")
    st.markdown("Click on an event below to see the context, rationale, and the exact conversations that led to that decision.")

    # Create a simple timeline using Streamlit components instead of streamlit-timeline
    st.subheader("Key Events")
    
    # Initialize session state for selected event
    if 'selected_event_id' not in st.session_state:
        st.session_state.selected_event_id = None

    # Display events as clickable buttons in chronological order
    events_sorted = sorted(events_data, key=lambda x: datetime.strptime(x['date'], '%Y-%m-%d'))
    
    # Create columns for better layout
    for i, event in enumerate(events_sorted):
        col1, col2, col3 = st.columns([1, 3, 1])
        
        with col1:
            st.write(f"**{event['date']}**")
        
        with col2:
            # Create a button for each event
            button_key = f"event_btn_{event['event_id']}"
            if st.button(
                f"📍 {event['title']}", 
                key=button_key,
                help=event['summary'],
                use_container_width=True
            ):
                st.session_state.selected_event_id = event['event_id']
        
        with col3:
            # Show event type as a badge
            event_color = {
                'Diagnostics': '🔬',
                'Plan Update': '📋',
                'Friction': '⚠️',
                'Insight': '💡'
            }
            st.write(f"{event_color.get(event['type'], '📌')} {event['type']}")

    st.markdown("---")

    # --- "The Why" Feature Display ---
    if st.session_state.selected_event_id:
        # Find the selected event's full details
        selected_event = next(
            (event for event in events_data if event["event_id"] == st.session_state.selected_event_id), 
            None
        )
        
        if selected_event:
            st.subheader(f"🎯 Decision: {selected_event['title']}")
            
            col1, col2 = st.columns(2)
            with col1:
                st.info(f"**📝 Summary:** {selected_event['summary']}")
            with col2:
                st.warning(f"**🤔 Rationale (The 'Why'):** {selected_event['rationale']}")
            
            st.markdown("#### 💬 Source Conversations")
            
            # Filter conversations based on the source_message_ids
            source_messages = [
                msg for msg in conversations_data 
                if msg.get("message_id") in selected_event.get("source_message_ids", [])
            ]
            
            if not source_messages:
                st.write("No source conversations linked for this event.")
            else:
                # Sort messages by timestamp
                source_messages.sort(key=lambda x: pd.to_datetime(x.get('timestamp')))
                
                # Display the chat messages
                for msg in source_messages:
                    # Use a different avatar style for member vs. team
                    if msg.get('sender_role') == 'member':
                        avatar_icon = "👨‍💼"
                        message_type = "user"
                    else:
                        avatar_icon = "👨‍⚕️"
                        message_type = "assistant"
                    
                    with st.chat_message(name=message_type, avatar=avatar_icon):
                        timestamp_str = pd.to_datetime(msg.get('timestamp')).strftime('%Y-%m-%d %H:%M')
                        st.markdown(f"**{msg.get('sender_name', 'Unknown')}** ({msg.get('sender_role', 'Unknown Role')}) - {timestamp_str}")
                        st.write(msg.get('message_text', ''))
    else:
        st.info("👆 Select an event from the timeline above to see the detailed breakdown.")

with tab2:
    st.header("Internal Engagement Metrics")
    st.markdown("Tracking team engagement and member interaction over the 8-month period.")

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Message Volume by Expert")
        if not metrics['messages_per_expert'].empty:
            st.dataframe(metrics['messages_per_expert'], use_container_width=True)
            
            # Add a bar chart for better visualization
            st.bar_chart(
                metrics['messages_per_expert'].set_index('Expert')['Message Count'],
                use_container_width=True
            )
        else:
            st.write("No expert messages to display.")

    with col2:
        st.subheader("Member-Initiated Conversations per Month")
        if not metrics['initiations_per_month'].empty:
            st.bar_chart(metrics['initiations_per_month'], use_container_width=True)
            
            # Show the data table too
            st.dataframe(metrics['initiations_per_month'], use_container_width=True)
        else:
            st.write("No member-initiated conversations to display.")

    # Additional metrics
    st.markdown("---")
    st.subheader("Overall Engagement Summary")
    
    total_messages = len(conversations_data)
    engagement_ratio = metrics['member_initiations'] / total_messages if total_messages > 0 else 0
    
    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric("Total Messages", total_messages)
    with col2:
        st.metric("Member Engagement %", f"{engagement_ratio:.1%}")
    with col3:
        st.metric("Avg Messages/Month", f"{total_messages/8:.1f}")
    with col4:
        st.metric("Team Experts Active", len(metrics['messages_per_expert']))