import gradio as gr
import openai
import threading

# Initialize OpenAI API key
openai.api_key = 'your_openai_api_key'

# Global variable to store the conversation history
conversation_history = []

def stream_response(prompt, conversation_history):
    # Append user prompt to conversation history
    conversation_history.append({"role": "user", "content": prompt})

    # Call OpenAI API to get response
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=conversation_history,
        stream=True
    )

    # Stream the response to the UI
    full_response = ""
    for chunk in response:
        if 'choices' in chunk and len(chunk['choices']) > 0:
            content = chunk['choices'][0]['delta'].get('content', '')
            full_response += content
            yield full_response  # Stream the response part by part to the UI

    # Append assistant's response to conversation history
    conversation_history.append({"role": "assistant", "content": full_response})

def respond(prompt):
    return stream_response(prompt, conversation_history)

# Gradio interface
iface = gr.Interface(fn=respond,
                     inputs=gr.Textbox(lines=2, placeholder="Ask me anything..."),
                     outputs=gr.Textbox(),
                     live=True)

# Launch the interface
iface.launch()