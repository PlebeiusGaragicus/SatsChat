import os
import json

from pydantic import BaseModel

import streamlit as st

from src.flows import StreamingLLM
from src.common import get, set
from src.cookies import set_cookie, get_cookie



# https://platform.openai.com/docs/models/gpt-3-5-turbo
# TODO - too many choices... also, should I provide pricing/info for each model...? model info card?
OPENAI_MODELS = [
        # "gpt-4-0125-preview",
        "gpt-4-turbo-preview",
        # "gpt-4-1106-preview",
        # "gpt-4-vision-preview",
        "gpt-4",
        # "gpt-4-0314",
        # "gpt-4-0613",
        # "gpt-4-32k",
        # "gpt-4-32k-0314",
        # "gpt-4-32k-0613",
        "gpt-3.5-turbo",
        # "gpt-3.5-turbo-16k",
        # "gpt-3.5-turbo-0301",
        # "gpt-3.5-turbo-0613",
        # "gpt-3.5-turbo-1106",
        # "gpt-3.5-turbo-0125",
        # "gpt-3.5-turbo-16k-0613",
    ]



class LLM_SETTINGS_OPENAI_GPT(BaseModel):
    model: str = OPENAI_MODELS[0]
    # temperature: float = 0.7


class LLM_OPENAI_GPT(StreamingLLM):
    """
        https://platform.openai.com/docs/api-reference/chat
    """

    emoji = "💫"
    name = "OpenAI"
    avatar_filename = "chatgpt.png"
    preamble = "Closed source and ready to take your money."

    def __init__(self):
        super().__init__()

    def setup(self):
        self._is_setup = True

        # load settings from file
        try:
            self.settings = LLM_SETTINGS_OPENAI_GPT(**json.loads(get_cookie(f'{self.name}_settings')))
        except:
            self.settings = LLM_SETTINGS_OPENAI_GPT()



    def run(self, prompt, **kwargs):
        if not self._is_setup:
            raise Exception("StreamingLLM.run(): not setup yet! Run `setup()` first!")

        import openai
        # from openai import OpenAI
        # client = openai.OpenAI(api_key=self.settings.api_key)
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

        try:
            generator = client.chat.completions.create(
                model=self.settings.model,
                messages=st.session_state.appstate.chat.messages,
                stream=True,
            )
        # except openai._exceptions.OpenAIError:
        # except E
        except openai._exceptions.APIConnectionError:
            # yield "Connection failed - double check your API key?"
            yield "🥺 Oops... my connection failed."
            return
        except openai._exceptions.AuthenticationError:
            yield "🔑 Invalid API key."
            return

        for chunk in generator:
            # print(chunk)
            yield chunk.choices[0].delta.content



    
    def display_settings(self):
        def update(key):
            new_value = st.session_state[key]
            self.settings.__dict__[key] = new_value

            set(f'{self.name}_settings', self.settings.model_dump())
            set_cookie(f'{self.name}_settings', json.dumps(self.settings.model_dump()))

        try:
            st.selectbox("Model", options=OPENAI_MODELS, key="model", index=OPENAI_MODELS.index(self.settings.model), on_change=update, args=("model",))
            # st.slider("Temperature", min_value=0.0, max_value=1.0, key="temperature", value=self.settings.temperature, on_change=update, args=("temperature",))

        except Exception as e:
            st.exception(e)
            self.settings = LLM_SETTINGS_OPENAI_GPT()
            set(f'{self.name}_settings', self.settings.model_dump())
            set_cookie(f'{self.name}_settings', json.dumps(self.settings.model_dump()))
            # self.display_settings()
