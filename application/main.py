import gradio as gr
import ollama
from logger import setup_logging
import logging
import os 
import datetime
from file_util import append_suffix_if_exists

setup_logging()
logging.getLogger("httpx").setLevel(logging.WARNING)
logger = logging.getLogger(__name__)

DEFAULT_DIR= os.path.dirname(os.path.realpath(__file__))


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
    chat_history = format_history(msg, history, system_prompt)
   
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

def load_save_file(file_path):
    if file_path:
        with open(file_path, "r") as f:
            data = f.read()
        print(data)
        return data
    
def create_save_file(history: list[list[str, str]]):
    current_date = datetime.datetime.now().date()
    formatted_date = current_date.strftime("%Y_%m_%d")
    output_file = f"{formatted_date}_1.json"
    output_file = append_suffix_if_exists(output_file)
    with open(output_file, 'w') as f:
        f.write(history)




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
fname = gr.Textbox("file upload")

file_explore = gr.FileExplorer(
    glob="*.json",
    root_dir="./chat_sessions",
    file_count="single",
    interactive=True)

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
    with gr.Row():
        with gr.Column(scale=4):

            chatbot.render()
            saved_chat = gr.State()


        with gr.Column(scale=1):
            save_btn.render()
            load_btn.render()
            check_btn.render()
            file_explore.render()

            fname.render()

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

            file_explore.change(
                fn=load_save_file,
                inputs=file_explore,
                outputs=fname
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
