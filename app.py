import streamlit as st
from openai import OpenAI
import httpx, requests, re, json, os, pyperclip

INDEX_FILE = "chat_index.json"
SETTINGS_FILE = "settings.json"
SYS_FILE = "systeminstructions.json"
CHAT_DIR = "chats"
os.makedirs(CHAT_DIR, exist_ok=True)

def load_settings():
    if not os.path.exists(SETTINGS_FILE):
        return {"base_url": "", "api_key": ""}
    with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_settings(base_url, api_key):
    with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
        json.dump({"base_url": base_url, "api_key": api_key}, f, indent=2)

def load_sys():
    if not os.path.exists(SYS_FILE):
        return {"system_instructions": ""}
    with open(SYS_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_sys(system_instructions):
    with open(SYS_FILE, "w", encoding="utf-8") as f:
        json.dump({"system_instructions": system_instructions}, f, indent=2)

def load_chat_index():
    if not os.path.exists(INDEX_FILE):
        return {"chats": []}
    with open(INDEX_FILE, "r", encoding="utf-8") as f:
        return json.load(f)

def save_chat_index(data):
    with open(INDEX_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

def load_chat(chat_id):
    p = os.path.join(CHAT_DIR, f"{chat_id}.json")
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_chat(chat_id, messages):
    p = os.path.join(CHAT_DIR, f"{chat_id}.json")
    with open(p, "w", encoding="utf-8") as f:
        json.dump(messages, f, indent=2, ensure_ascii=False)

def delete_chat(chat_id):
    p = os.path.join(CHAT_DIR, f"{chat_id}.json")
    if os.path.exists(p):
        os.remove(p)

def fetch_models(base_url, api_key):
    try:
        if base_url.startswith("http://localhost:11434") or re.match(r"^http://[a-zA-Z0-9.-]+:11434$", base_url):
            r = requests.get(base_url.rstrip("/") + "/api/tags")
            r.raise_for_status()
            d = r.json()
            return sorted([m["name"] for m in d.get("models", [])])
        r = httpx.get(base_url.rstrip("/") + "/models",
                      headers={"Authorization": f"Bearer {api_key}"} if api_key else {},
                      timeout=10)
        r.raise_for_status()
        d = r.json()
        return sorted([m["id"] for m in d.get("data", []) if m.get("id")])
    except:
        return []

def copy_to_clipboard(t):
    try:
        pyperclip.copy(t)
        st.toast("Copied to clipboard!")
    except:
        pass

def trunc(t, n=50):
    w = t.split()
    return " ".join(w[:n]) + "..." if len(w) > n else t

st.set_page_config(page_title="LLM Chat", page_icon="💬")

settings = load_settings()
sysdata = load_sys()

if "base_url" not in st.session_state:
    st.session_state.base_url = settings["base_url"]
if "api_key" not in st.session_state:
    st.session_state.api_key = settings["api_key"]
if "system_instructions" not in st.session_state:
    st.session_state.system_instructions = sysdata["system_instructions"]

if "current_chat" not in st.session_state:
    st.session_state.current_chat = None
if "new_chat_pending" not in st.session_state:
    st.session_state.new_chat_pending = False

index = load_chat_index()

with st.sidebar:
    s = st.selectbox("Select Settings or Chat Below:", ["Chat", "Settings"], key="menu_sel")

    if s == "Settings":
        u = st.text_input("Base URL", value=st.session_state.base_url, key="settings_base")
        k = st.text_input("API Key", type="password", value=st.session_state.api_key, key="settings_key")
        if st.button("Save", key="save_api"):
            st.session_state.base_url = u
            st.session_state.api_key = k
            save_settings(u, k)
            st.rerun()

        si = st.text_area("System Instructions:", value=st.session_state.system_instructions, height=200, key="settings_sys")
        if st.button("Save", key="save_sys"):
            st.session_state.system_instructions = si
            save_sys(si)
            st.rerun()

    if s == "Chat":
        base_url = st.session_state.base_url
        api_key_req = not re.match(r"^http://[a-zA-Z0-9.-]+:11434$", base_url)
        api_key = st.session_state.api_key if api_key_req else ""
        if st.button("List / Refresh Models", use_container_width=True, key="refresh_models"):
            if base_url:
                st.session_state["model_list"] = fetch_models(base_url, api_key)

        chosen_model = st.selectbox("Select a model:",
                                    st.session_state.get("model_list", []),
                                    key="model_selector") if "model_list" in st.session_state else None

        if st.button("Start New Chat", key="new_chat_btn"):
            st.session_state.current_chat = None
            st.session_state.new_chat_pending = True
            st.rerun()

        search = st.text_input("Search chats", key="search_chats")

        for idx, c in enumerate(index["chats"]):
            if search.lower() in c["title"].lower():
                kbtn = f"chatbtn_{c['id']}_{idx}"
                if st.button(c["title"], key=kbtn):
                    st.session_state.current_chat = c["id"]
                    st.session_state.new_chat_pending = False
                    st.rerun()

if st.session_state.menu_sel != "Chat":
    st.stop()

if st.session_state.current_chat:
    messages = load_chat(st.session_state.current_chat)
else:
    messages = []

st.title("Chat")

if st.session_state.base_url and chosen_model:
    base_url = st.session_state.base_url.rstrip("/")
    if not base_url.endswith("/v1"):
        base_url += "/v1"
    client = OpenAI(base_url=base_url, api_key=st.session_state.api_key)

    if st.session_state.current_chat:
        i = 0
        while i < len(messages):
            m = messages[i]
            if m["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(m["content"])
                i += 1
                if i < len(messages) and messages[i]["role"] == "assistant":
                    idx = i
                    txt = messages[idx]["content"]
                    tog = f"read_{idx}"
                    if tog not in st.session_state:
                        st.session_state[tog] = False
                    with st.chat_message("assistant"):
                        w = txt.split()
                        st.markdown(trunc(txt) if len(w) > 50 and not st.session_state[tog] else txt)
                        c1, c2, c3 = st.columns(3)
                        with c1:
                            if len(w) > 50:
                                lbl = "Read More" if not st.session_state[tog] else "Show Less"
                                if st.button(lbl, key=f"t_{idx}"):
                                    st.session_state[tog] = not st.session_state[tog]
                                    st.rerun()
                        with c2:
                            if st.button("Copy Output", key=f"cp_{idx}"):
                                copy_to_clipboard(txt)
                        with c3:
                            if st.button("Delete Response", key=f"del_{idx}"):
                                messages.pop(idx)
                                messages.pop(idx - 1)
                                save_chat(st.session_state.current_chat, messages)
                                st.rerun()
                    i += 1
            else:
                with st.chat_message("assistant"):
                    st.markdown(m["content"])
                i += 1

        if st.button("Delete This Chat", key="delete_chat_btn"):
            index["chats"] = [c for c in index["chats"] if c["id"] != st.session_state.current_chat]
            save_chat_index(index)
            delete_chat(st.session_state.current_chat)
            st.session_state.current_chat = None
            st.session_state.new_chat_pending = False
            st.rerun()

    prompt = st.chat_input("Type your message…")

    if prompt:
        if st.session_state.current_chat is None:
            st.session_state.new_chat_pending = True

        if st.session_state.new_chat_pending:
            new_id = f"chat_{len(index['chats'])+1}"
            title_words = prompt.split()
            title = " ".join(title_words[:4])
            index["chats"].insert(0, {"id": new_id, "title": title})
            save_chat_index(index)
            save_chat(new_id, [])
            st.session_state.current_chat = new_id
            st.session_state.new_chat_pending = False
            messages = []

        messages.append({"role": "user", "content": prompt})

        with st.chat_message("user"):
            st.markdown(prompt)

        messages.append({"role": "assistant", "content": ""})
        aidx = len(messages) - 1

        with st.chat_message("assistant"):
            stop_b = st.empty()
            out = st.empty()
            col = ""
            fl = f"s_{aidx}"
            st.session_state[fl] = False

            def stop():
                st.session_state[fl] = True

            stop_b.button("Stop Response", on_click=stop, key=f"sb_{aidx}")

            try:
                sys_msg = {"role": "system", "content": st.session_state.system_instructions} if st.session_state.system_instructions.strip() else None
                base_msgs = []
                if sys_msg:
                    base_msgs.append(sys_msg)
                for m in messages[:-1]:
                    base_msgs.append(m)
                base_msgs.append({"role": "user", "content": prompt})

                stream = client.chat.completions.create(
                    model=chosen_model,
                    messages=base_msgs,
                    max_tokens=1024,
                    stream=True
                )
                for ch in stream:
                    if st.session_state[fl]:
                        break
                    d = ch.choices[0].delta.content or ""
                    col += d
                    out.markdown(col + "▌")
                    messages[aidx]["content"] = col
            except Exception as e:
                col = messages[aidx]["content"] + f"\n\n<Request failed: {e}>"
                messages[aidx]["content"] = col
            finally:
                out.markdown(col)
                stop_b.empty()
                messages[aidx]["content"] = col
                save_chat(st.session_state.current_chat, messages)
else:
    st.info("Configure and select a model.")
