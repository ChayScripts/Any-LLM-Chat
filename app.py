import streamlit as st
from openai import OpenAI
import httpx
import requests
import re
import json
import os
import pyperclip

# --- Helper to fetch model list ---
def fetch_models(base_url: str, api_key: str):
    try:
        if base_url.startswith("http://localhost:11434") or re.match(r"^http://[a-zA-Z0-9.-]+:11434$", base_url):
            res = requests.get(base_url.rstrip("/") + "/api/tags")
            res.raise_for_status()
            data = res.json()
            return sorted([m["name"] for m in data.get("models", [])])
        else:
            endpoint = base_url.rstrip("/") + "/models"
            headers = {"Authorization": f"Bearer {api_key}"} if api_key else {}
            r = httpx.get(endpoint, headers=headers, timeout=10)
            r.raise_for_status()
            data = r.json()
            models = [m["id"] for m in data.get("data", []) if m.get("id")]
            return sorted(models)
    except Exception as e:
        st.error(f"Could not fetch models: {e}")
        return []

# --- Save chat history to JSON ---
def save_chat_history(messages, filename="chat_history.json"):
    try:
        with open(filename, "w", encoding="utf-8") as f:
            json.dump(messages, f, indent=2, ensure_ascii=False)
    except Exception as e:
        st.error(f"Error saving chat history: {e}")

# --- Load from JSON ---
def load_chat_history(filename="chat_history.json"):
    try:
        if os.path.exists(filename):
            with open(filename, "r", encoding="utf-8") as f:
                return json.load(f)
    except Exception as e:
        st.error(f"Error loading chat history: {e}")
    return []

# --- Clipboard copy helper ---
def copy_to_clipboard(text):
    try:
        pyperclip.copy(text)
        st.toast("Copied to clipboard!")
    except Exception as e:
        st.error(f"Could not copy to clipboard: {e}")

# --- Text truncation helper ---
def get_truncated_text(text, word_limit=50):
    words = text.split()
    if len(words) > word_limit:
        return ' '.join(words[:word_limit]) + "..."
    return text

# --- Page config ---
st.set_page_config(page_title="Custom LLM Chat", page_icon="💬")
st.title("💬 Chat with Any Model Provider")

# --- Sidebar: credentials & model list ---
with st.sidebar:
    st.header("Connect")
    base_url = st.text_input("Base URL (no trailing slash) & Hit Enter", value=st.session_state.get("base_url", ""))
    api_key_required = not re.match(r"^http://[a-zA-Z0-9.-]+:11434$", base_url)
    api_key = st.text_input("API Key", type="password", value=st.session_state.get("api_key", "")) if api_key_required else ""

    if st.button("List / Refresh Models", use_container_width=True):
        if base_url:
            with st.spinner("Fetching models…"):
                model_list = fetch_models(base_url, api_key)
            st.session_state["model_list"] = model_list
            st.session_state["base_url"] = base_url
            st.session_state["api_key"] = api_key
        else:
            st.error("Please enter Base URL")

    if "model_list" in st.session_state:
        chosen_model = st.selectbox(
            "Select a model:",
            st.session_state["model_list"],
            key="chosen_model",
        )
    else:
        chosen_model = None

# --- Chat area ---
if chosen_model and "base_url" in st.session_state:
    if "messages" not in st.session_state:
        st.session_state.messages = load_chat_history()

    base_url = st.session_state["base_url"].rstrip("/")
    if not base_url.endswith("/v1"):
        base_url += "/v1"

    client = OpenAI(
        base_url=base_url,
        api_key=st.session_state.get("api_key", ""),
    )

    st.subheader("Chat History")

    i = 0
    while i < len(st.session_state.messages):
        msg = st.session_state.messages[i]
        if msg["role"] == "user":
            with st.chat_message("user"):
                st.markdown(msg["content"])
            i += 1
            if i < len(st.session_state.messages) and st.session_state.messages[i]["role"] == "assistant":
                assistant_idx = i
                response_text = st.session_state.messages[assistant_idx]["content"]
                toggle_key = f"read_more_{assistant_idx}"
                if toggle_key not in st.session_state:
                    st.session_state[toggle_key] = False

                with st.chat_message("assistant"):
                    words = response_text.split()
                    if len(words) > 50 and not st.session_state[toggle_key]:
                        st.markdown(get_truncated_text(response_text, 50))
                    else:
                        st.markdown(response_text)

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        if len(words) > 50:
                            label = "Read More" if not st.session_state[toggle_key] else "Show Less"
                            if st.button(label, key=f"toggle_{assistant_idx}"):
                                st.session_state[toggle_key] = not st.session_state[toggle_key]
                                st.rerun()
                    with col2:
                        if st.button("Copy Output", key=f"copy_{assistant_idx}"):
                            copy_to_clipboard(response_text)
                    with col3:
                        if st.button("🗑️ Delete Response", key=f"delete_{assistant_idx}"):
                            st.session_state.messages.pop(assistant_idx)   # assistant
                            st.session_state.messages.pop(assistant_idx - 1)  # user
                            save_chat_history(st.session_state.messages)
                            st.rerun()
                i += 1
        else:
            with st.chat_message("assistant"):
                st.markdown(msg["content"])
            i += 1

    # --- Input box for new message ---
    if prompt := st.chat_input("Type your message…"):
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        st.session_state.messages.append({"role": "assistant", "content": ""})
        current_assistant_message_idx = len(st.session_state.messages) - 1

        with st.chat_message("assistant"):
            stop_button_placeholder = st.empty()
            response_placeholder = st.empty()

            collected_text = ""
            stop_flag_key = f"stop_flag_{current_assistant_message_idx}"
            st.session_state[stop_flag_key] = False
            st.session_state["is_streaming"] = True

            def stop_stream_callback():
                st.session_state[stop_flag_key] = True
                st.session_state["is_streaming"] = False

            stop_button_placeholder.button("Stop Response", on_click=stop_stream_callback, key=f"stop_button_{current_assistant_message_idx}")

            try:
                stream = client.chat.completions.create(
                    model=chosen_model,
                    messages=[
                        {"role": m["role"], "content": m["content"]}
                        for m in st.session_state.messages[:-1]
                    ] + [{"role": "user", "content": prompt}],
                    max_tokens=20000,
                    stream=True,
                )
                for chunk in stream:
                    if st.session_state[stop_flag_key]:
                        break
                    delta = chunk.choices[0].delta.content or ""
                    collected_text += delta
                    response_placeholder.markdown(collected_text + "▌")
                    st.session_state.messages[current_assistant_message_idx]["content"] = collected_text

            except Exception as e:
                st.error(f"Request failed: {e}")
                collected_text = st.session_state.messages[current_assistant_message_idx]["content"] + f"\n\n<Request failed: {e}>"
                st.session_state.messages[current_assistant_message_idx]["content"] = collected_text
            finally:
                response_placeholder.markdown(collected_text)
                stop_button_placeholder.empty()
                st.session_state["is_streaming"] = False
                st.session_state.messages[current_assistant_message_idx]["content"] = collected_text
                save_chat_history(st.session_state.messages)

elif "model_list" not in st.session_state:
    st.info("👈 Use the sidebar to enter your credentials and load available models.")
else:
    st.info("Please pick a model from the sidebar.")
