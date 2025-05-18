import os
import json
import pandas as pd
import streamlit as st
from dotenv import load_dotenv
from openai import OpenAI
from llm_tools import dispatch, function_schemas

# 1. Config & data
load_dotenv()
client = OpenAI(api_key=os.getenv("OPEN_API_KEY"))
data = pd.read_csv("data/master_df_T20Is_male.csv", low_memory=False)
data['start_date'] = pd.to_datetime(data['start_date'])

st.set_page_config(layout="wide")
st.title("🏏 Cricket Stats Assistant")

# Initialize history and last_df
if "history" not in st.session_state:
    st.session_state.history = []
if "last_df" not in st.session_state:
    st.session_state.last_df = None

# Sidebar
st.sidebar.markdown("Ask about T20I stats. Ex: “Kohli vs Rashid Khan”")
st.sidebar.markdown("You can filter by date. Use dates like 1st May, 2025 or just the Year or month or day, and yyyy/mm//dd if you want to be specific.")


# Layout
col1, col2 = st.columns((1, 2))
with col1:
    with st.form(key="chat_form", clear_on_submit=True):
        user_input = st.text_input("You:")
        send = st.form_submit_button("Send")

        if send and user_input:
            # Append user message
            st.session_state.history.append(("user", user_input))

            # Build LLM messages (only text)
            messages = [{"role": "system", "content": "You are a cricket stats assistant."}]
            for role, txt in st.session_state.history:
                messages.append({"role": role, "content": txt})

            # Call LLM
            resp = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                functions=function_schemas,
                function_call="auto",
                temperature=0.2,
                max_tokens=500
            ).choices[0].message

            # Handle function call
            if resp.function_call:
                name = resp.function_call.name
                args = json.loads(resp.function_call.arguments)
                result = dispatch(name, args, data)
                df = pd.DataFrame(result)

                # Store df separately for rendering
                st.session_state.last_df = df

                # Append only a textual summary into history
                summary = f"Here are the top {len(df)} rows from `{name}`."
                st.session_state.history.append(("assistant", summary))

                # Append function result back into messages for the wrap-up call
                messages.append({
                    "role": "function",
                    "name": name,
                    "content": json.dumps(result)
                })

                # Final wrap-up from the assistant
                wrap = client.chat.completions.create(
                    model="gpt-4o-mini",
                    messages=messages,
                    temperature=0.2,
                    max_tokens=300
                ).choices[0].message.content
                st.session_state.history.append(("assistant", wrap))

            else:
                # Direct text response
                st.session_state.history.append(("assistant", resp.content))

with col2:
    # Render history and last_df
    for role, content in st.session_state.history:
        if role == "user":
            st.markdown(f"**You:** {content}")
        else:  # assistant
            st.markdown(f"**Bot:** {content}")

    # If there's a DataFrame from the last function call, render it below
    if st.session_state.last_df is not None:
        st.table(st.session_state.last_df)
