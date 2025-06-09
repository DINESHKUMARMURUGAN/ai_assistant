import gradio as gr
import sqlite3
from load_llm import load_model

# Load the model once
model_name = "mistralai/Mistral-7B-Instruct-v0.1"
generator = load_model(model_name)

# Ensure database and tables exist
def initialize_database():
    conn = sqlite3.connect("chat_sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT UNIQUE
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id INTEGER,
            user_message TEXT,
            assistant_message TEXT,
            FOREIGN KEY(session_id) REFERENCES sessions(id)
        )
    """)
    conn.commit()
    conn.close()

# Get or create session ID
def get_or_create_session(session_name):
    conn = sqlite3.connect("chat_sessions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sessions WHERE name = ?", (session_name,))
    row = cursor.fetchone()
    if row:
        session_id = row[0]
    else:
        cursor.execute("INSERT INTO sessions (name) VALUES (?)", (session_name,))
        session_id = cursor.lastrowid
        conn.commit()
    conn.close()
    return session_id

# Save a message to the database
def save_message(session_id, user_message, assistant_message):
    conn = sqlite3.connect("chat_sessions.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT INTO messages (session_id, user_message, assistant_message)
        VALUES (?, ?, ?)
    """, (session_id, user_message, assistant_message))
    conn.commit()
    conn.close()

# Load chat history for a session
def load_session_history(session_name):
    conn = sqlite3.connect("chat_sessions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM sessions WHERE name = ?", (session_name,))
    row = cursor.fetchone()
    if not row:
        conn.close()
        return [], None
    session_id = row[0]
    cursor.execute("""
        SELECT user_message, assistant_message FROM messages
        WHERE session_id = ?
    """, (session_id,))
    messages = cursor.fetchall()
    history = [(f"You: {user}", f"LLM: {assistant}") for user, assistant in messages]
    conn.close()
    return history, session_id

# Get all session names
def get_all_session_names():
    conn = sqlite3.connect("chat_sessions.db")
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sessions")
    names = [row[0] for row in cursor.fetchall()]
    conn.close()
    return names

# Chat function
def chat_with_llm(session_name, intro, message, history):
    if not session_name:
        session_name = "default_session"
    session_id = get_or_create_session(session_name)

    formatted_history = "\n".join(f"{user}\n{assistant}" for user, assistant in history)
    prompt = f"{intro}\n\n{formatted_history}\nYou: {message}\nAssistant:"
    output = generator(prompt, max_new_tokens=500, return_full_text=False)
    response = output[0]["generated_text"] if isinstance(output, list) else output

    history.append((f"You: {message}", f"LLM: {response}"))
    save_message(session_id, message, response)
    return history, history, ""

# Load history when session changes
def on_session_change(session_name):
    if not session_name:
        session_name = "default_session"
    history, _ = load_session_history(session_name)
    return history, history

# Initialize database
initialize_database()

# Gradio UI
with gr.Blocks(css="""
html, body, #root, .gradio-container {
    height: 100%;
    margin: 0;
}
#main-container {
    display: flex;
    flex-direction: column;
    height: 100%;
}
#chatbot-container {
    flex-grow: 1;
    overflow-y: auto;
    border: 1px solid #ccc;
    border-radius: 8px;
    padding: 10px;
}
.input-wrapper {
    position: relative;
    width: 100%;
}
#user-input {
    width: 100%;
    padding-right: 40px;
}
#send-button {
    position: absolute;
    right: 5px;
    bottom: 5px;
    height: 30px;
    width: 30px;
    font-size: 16px;
    padding: 0;
    border-radius: 5px;
}
""") as demo:
    with gr.Column(elem_id="main-container"):
        gr.Markdown("## 🤖 Chat with Your LLM")

        with gr.Row():
            session_names = get_all_session_names()
            session_input = gr.Dropdown(choices=session_names, label="Session Name", interactive=True, allow_custom_value=True)
            intro_input = gr.Textbox(label="📝 Intro Message", placeholder="Enter system prompt or intro message here...")

        chatbot = gr.Chatbot(label="💬 Conversation History", elem_id="chatbot-container", render_markdown=True)

        gr.HTML("""
        <script>
          const observer = new MutationObserver(() => {
            const container = document.querySelector('#chatbot-container');
            if (container) {
              container.scrollTop = container.scrollHeight;
            }
          });
          const target = document.querySelector('#chatbot-container');
          if (target) {
            observer.observe(target, { childList: true, subtree: true });
          }
        </script>
        """)

        with gr.Row():
            with gr.Column(scale=1, elem_classes="input-wrapper"):
                user_input = gr.Textbox(placeholder="Type your message here...", elem_id="user-input", show_label=False)
                send_button = gr.Button("➡️", elem_id="send-button")

        state = gr.State([])

        send_button.click(
            chat_with_llm,
            inputs=[session_input, intro_input, user_input, state],
            outputs=[chatbot, state, user_input]
        )

        user_input.submit(
            chat_with_llm,
            inputs=[session_input, intro_input, user_input, state],
            outputs=[chatbot, state, user_input]
        )

        session_input.change(
            on_session_change,
            inputs=session_input,
            outputs=[chatbot, state]
        )

demo.launch()

