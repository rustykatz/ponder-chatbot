import gradio as gr
import ollama
from logger import setup_logging
import logging

setup_logging()
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def format_history(msg: str, history: list[list[str, str]], system_prompt: str):
    chat_history = [
        {
            "role": "system",
            "content": system_prompt,
        }
    ]
    for query, response in history:
        chat_history.append({"role": "user", "content": query})
        chat_history.append({"role": "assistant", "content": response})
    chat_history.append({"role": "user", "content": msg})
    return chat_history


def generate_response(msg: str, history: list[list[str, str]], system_prompt: str):
    # chat_history = format_history(msg, history, system_prompt)
    chat_history = [
        {
            "role": "system",
            "content": "This is a test system prompt",
        },
        {
            "role": "user",
            "content": "This is some fake query",
        },
        {
            "role": "assistant",
            "content": "This is some fake response",
        },
        {
            "role": "user",
            "content": msg,
        },
    ]

    response = ollama.chat(
        model="llama3",
        messages=chat_history,
        stream=True,
    )
    message = ""
    for token in response:
        message += token["message"]["content"]
        # Messages yielded to create type writer effect
        yield message
    
    logger.info(message)


#! Todo: can we clean this up? very messy
input_txt = gr.Textbox(label="Input Text")

output_txt = gr.Textbox(label="Output Text")

submit_btn = gr.Button(
    value="Submit",
    variant="primary",
)

save_btn = gr.Button("Save")
load_btn = gr.Button("Load")
check_btn = gr.Button("Check")

cbot = gr.Chatbot(
        height=800,
        show_copy_button=True
)

#! TODO: not a fan of chat interface component, doesn't work well with custom load/ save 
#! I'll replace with a normal chatbot so i have more control over UI 

chatbot = gr.ChatInterface(
    fn=generate_response,
    chatbot=cbot,
    additional_inputs=[
        gr.Textbox("Behave as a mature woman.", label="System Prompt")
    ],
    submit_btn="Submit",
    retry_btn="Regenerate Response",
    undo_btn="Delete Previous Response",
    clear_btn="Clear Chat",
    stop_btn="HALT",
    fill_height=True,
)

with gr.Blocks(theme=gr.themes.Default(
        primary_hue=gr.themes.colors.red,
        secondary_hue=gr.themes.colors.orange,
        font=[gr.themes.GoogleFont("Open Sans"), "Arial", "sans-serif"],
    ),
    title="Ponder Ai Chatbot Demo",
) as demo:
    big_block = gr.Markdown(
        """
    # Ponder - Ai Chatbot Demo
    ### Current Model: Meta Llama 3 - 8B
    """
    )
    # with gr.Row():
    chatbot.render()
    saved_chat = gr.State()

    save_btn.render()
    load_btn.render()
    check_btn.render()

    save_btn.click(
        fn=lambda x:x,
        inputs=cbot,
        outputs=saved_chat
    )

    load_btn.click(
        fn=lambda x:x,
        inputs=saved_chat,
        outputs=cbot
    )

    check_btn.click(
        fn=lambda x: print('state:',x),
        inputs=saved_chat,
        outputs=None
    )

if __name__ == "__main__":
    demo.launch(
        server_port=5000,
        server_name="127.0.0.1",
        debug=True,
        show_error=True,
        ssl_verify=False,
        share=False,
    )
