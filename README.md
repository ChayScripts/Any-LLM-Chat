# Any LLM Chat

A versatile Streamlit application designed for seamless interaction with various Language Model (LLM) providers. Whether you're using a local Ollama instance (local or remote) or a cloud-based API like OpenAI, this app provides a unified chat experience, complete with chat history, model selection, and response management.

-----

## ✨ Features

  * **Universal Compatibility**: Connects to any LLM provider that supports the OpenAI-compatible API, including local or remote Ollama instances.
  * **Dynamic Model Discovery**: Automatically fetches and lists available models from your specified API endpoint.
  * **Persistent Chat History**: Saves and loads your conversations locally, ensuring you never lose your progress.
  * **Interactive Chat Interface**: A familiar chat UI for intuitive conversations.
  * **Response Management**:
      * **"Read More/Show Less"**: Truncates long responses for readability with an option to expand.
      * **Copy to Clipboard**: Easily copy assistant responses with a single click.
      * **Delete Messages**: Remove individual user/assistant message pairs from the history.
  * **Streaming Responses**: Enjoy real-time text generation as the LLM responds.
  * **Stop Generation**: Ability to halt ongoing AI responses at any time, helping you save on token usage and costs.
  * **New Chat**: Start new chats if your queries exceed LLM token limits.
  * **Save Chat History**: Persist conversations across sessions for easy reference and continuity.
  * **API URL & Key**: Store custom API endpoints and key locally on disk for seamless integrations — no privacy concerns as data remains on your device.
  * **System Instructions**: Define your custom instructions that you want LLM to follow on every chat.

-----

## 🚀 Getting Started

Follow these steps to get your Any LLM Chat Interface up and running.

### Prerequisites

  * Python 3.8+
  * `pip` package manager

### Installation

1.  **Clone the repository (or save the script):**
    If you have the script as a file, save it as `app.py`. Otherwise, clone the repo:

    ```bash
    git clone https://github.com/ChayScripts/Any-LLM-Chat.git
    cd Any-LLM-Chat
    ```

2.  **Install dependencies:**
    Create a virtual environment in python or install the packages directly.

    ```bash
    pip install streamlit openai httpx requests pyperclip
    ```

### Running the Application

To start the Streamlit application, run the following command in your terminal:

```bash
streamlit run app.py
```

This will open the application in your default web browser.

-----

## 💡 Usage

1.  **Enter Base URL**: In the sidebar, provide the base URL of your LLM provider.

      * For **Ollama (local)**: Typically `http://localhost:11434`
      * For **Ollama (Remote)**: Typically `http://Ollama_Server_FQDN:11434` 
      * For **OpenAI (cloud)** or other compatible APIs: e.g., `https://api.openai.com`
      * **Important**: Do not include a trailing slash.
        
    *For remote Ollama servers, use the server's FQDN or IP address in the API URL. Refer to the [Ollama guide for Windows](https://www.techwithchay.com/posts/ollama-guide-for-windows/#remote-deployment) to configure `OLLAMA_HOST` for remote connections.*

2.  **API Key**: If your chosen provider requires an API key (e.g., OpenAI), enter it in the "API Key" field. For local Ollama instances, an API key is not needed.

3.  **List / Refresh Models**: Click the "List / Refresh Models" button. The application will fetch and display available models from your specified endpoint.

4.  **Select a Model**: Choose your desired model from the "Select a model:" dropdown.

5.  **Start Chatting**: Type your message in the input box at the bottom and press Enter.

Your chat history will be automatically saved and loaded from `chat_history.json` file in the same directory as the script. 

-----

## 🔒 Privacy & Security

This application is designed with your privacy in mind:

**API Key Handling:** Your API key is entered directly into your browser session and is never saved or stored persistently by the application or forwarded to any remote server. It resides in your browser's memory only for the duration of your active session.

**Local Data Storage:** All your chat history is saved locally in a `chat_history.json` file on your machine. No chat data is transmitted to or stored on any external servers, ensuring your conversations remain private.

-----

## ▶️ Run without terminal
To run a Streamlit app in a Python virtual environment without opening a terminal, create and run a shortcut or script that activates the virtual environment and starts the app. Here's how to do it on different platforms:

---

**Windows (.bat file):**

1. Create a `run_streamlit.bat` file with the following content:

```bat
@echo off
call C:\path\to\venv\Scripts\activate.bat
streamlit run C:\path\to\your_app.py
```
Next create a .vbs file (e.g., launch_app.vbs) in the same folder and double click it. It will open browser directly without opening terminal. 

```vbscript
Set WshShell = CreateObject("WScript.Shell")
WshShell.Run chr(34) & "C:\path\to\run_streamlit.bat" & chr(34), 0
Set WshShell = Nothing
```

2. Double-click the `.vbs` file to launch the app. After you close the browser, if it does not close python and streamlit.exe processes, you have to manually kill those processes or they will pile up for every time you launch the app.

---
**macOS/Linux (.sh file):**

1. Create a `run_streamlit.sh` script:

```bash
#!/bin/bash
source /path/to/venv/bin/activate
streamlit run /path/to/your_app.py
```

2. Make it executable:

```bash
chmod +x run_streamlit.sh
```

3. Run it via double-click or from a launcher depending on your desktop environment.

---

## ✍️ Authors

* **Chay** - [ChayScripts](https://github.com/ChayScripts)

-----

## 🤝 Contributing

Contributions are welcome\! If you have suggestions for improvements, bug fixes, or new features, please feel free to:

  * Open an issue to discuss your ideas.
  * Fork the repository and submit a pull request.

-----

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details

