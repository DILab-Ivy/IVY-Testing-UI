import openai
from typing import List

# OpenAI Response Function
def get_openai_response(question: str) -> str:
    client = openai.OpenAI()
    ASSISTANT_ID = "asst_iMCg2aqO343Sik6YWP3BDADq"

    class EventHandler(openai.AssistantEventHandler):
        def on_event(self, event: openai.types.beta.AssistantStreamEvent) -> None:
            pass

        def on_text_delta(self, delta: openai.types.beta.TextDelta, snapshot: openai.types.beta.threads.Text) -> None:
            pass

    thread = client.beta.threads.create(
        messages=[
            {
                "role": "user",
                "content": question,
            },
        ]
    )