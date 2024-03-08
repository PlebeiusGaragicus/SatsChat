import os
import math

import redis

import streamlit as st
from streamlit_pills import pills


from mistralai.models.chat_completion import ChatMessage

from langchain_core.messages.human import HumanMessage
from langchain_core.messages.ai import AIMessage
from langchain_core.messages.function import FunctionMessage


from src.flows import ChatThread

from src.flows.constructs import ALL_CONSTRUCTS


from src.interface import (
    column_fix,
    center_text,
    centered_button_trick,
    show_new_user,
    show_nuke_button,
)

from src.common import (
    ASSETS_PATH,
    is_init,
    not_init,
    get,
    set,
    cprint,
    Colors,
)

from src.cookies import (
    load_ui_persistance,
    get_cookie,
    load_cookies,
    duke_nuke_em,
    get_cookie_manager,
    set_cookie
)

from src.sats import (
    charge_user,
    load_sats_balance,
    display_invoice_link
)



def run_prompt(prompt, bots_reply_placeholder, sats_left_placeholder):

    sats_left = load_sats_balance()
    total_cost = 0
    st.session_state.token_cost_accumulator = 0

    avatar_filename = f"{AVATAR_PATH}/{get('construct').avatar_filename}"
    with bots_reply_placeholder.chat_message("assistant", avatar=avatar_filename):

        st.session_state.incomplete_stream = ""
        place_holder = st.empty()

        # we don't want to use write_stream because we need to keep track of the cost (and other things), as we go.
        # reply = st.write_stream(get('construct').run(prompt))
        for chunk in get('construct').run(prompt):

            if chunk is None:
                num_tokens = 0
                chunk = ""
            else:
                # TODO - this is not accurate, but it's a start
                num_tokens = len(chunk)
                # num_tokens = num_tokens_from_string(chunk) # nah.... we'll go by chunk count

            # num_tokens = len(chunk) # OpenAI returns a last token of {...content=None}
            cost_for_this_chunk = num_tokens / TOKENS_PER_SAT # tokens charged per satoshi

            st.session_state.token_cost_accumulator += cost_for_this_chunk
            total_cost += cost_for_this_chunk
            sats_left -= cost_for_this_chunk

            if os.getenv("DEBUG", True):
                sats_left_placeholder.markdown(f"⚡️ :red[-{total_cost:,.0f}] / :green[{sats_left:,.0f}]")
            else:
                sats_left_placeholder.markdown(f":red[-{total_cost:,.0f}]")

            if st.session_state.token_cost_accumulator >= 10:
                st.session_state.redis_conn.decrby(st.session_state.username, math.floor(st.session_state.token_cost_accumulator))
                st.session_state.token_cost_accumulator -= 10

            if sats_left < -1000:
                interrupt()

            st.session_state.incomplete_stream += chunk
            place_holder.markdown(st.session_state.incomplete_stream)

        st.session_state.redis_conn.decrby(st.session_state.username, math.ceil(st.session_state.token_cost_accumulator))

        reply = st.session_state.incomplete_stream
        st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=reply))
        return reply



def run_graph(prompt, bots_reply_placeholder):
    # if not hasattr(st.session_state, "redis_conn"):
    #     st.session_state.redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
    if get('construct').graph is None:
        error_reply = "I'm not configured properly... 🥺  Check my settings.  Do I have all my API keys?"
        st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=error_reply))
        return error_reply


    #TODO
    st.session_state.incomplete_stream = "" # so that the interrupt button works... but there's still no token counting!
    st.session_state.token_cost_accumulator = 0
    sats_left = load_sats_balance()

    avatar_filename = f"{AVATAR_PATH}/{get('construct').avatar_filename}"
    with bots_reply_placeholder.chat_message("assistant", avatar=avatar_filename):

        # TODO - this does NOT provide a good enough context for an agent... at least when opening an stale conversation.
        # for node, output in get('construct').run(str(st.session_state.appstate.chat.messages)):
        for node, output in get('construct').invoke(str(st.session_state.appstate.chat.messages)): # TODO - don't typecast to a str() dude.. don't be a noob!

            if node != "__end__":
                try:
                    message = output['messages'][0]
                except KeyError:
                    message = output
                # num_tokens = len(message.content) # function calls have no context... so we have to look at the whole LLM output
                num_tokens = len(str(message)) # NAHH.... # give the user a small discount because some of these tokens are just JSON formatting.
                cost_for_this_chunk = math.ceil(num_tokens / TOKENS_PER_SAT) # tokens charged per satoshi
                st.session_state.token_cost_accumulator += cost_for_this_chunk
                sats_left = st.session_state.redis_conn.decrby(st.session_state.username, cost_for_this_chunk)

                # st.markdown(f":red[{cost_for_this_chunk}]")
                # content = f":red[{cost_for_this_chunk}]"

                if sats_left < -1000:
                    interrupt() # TODO does this interrupt???


                # <class 'langchain_core.messages.ai.AIMessage'>
                # <class 'langchain_core.messages.function.FunctionMessage'>
                # <class 'langchain_core.messages.human.HumanMessage'>

                if type(message) is FunctionMessage:

                    content = f"**Function returned:**\n{message.content}"
                    st.markdown(f"{content}")

                    st.session_state.appstate.chat.messages.append(
                                            ChatMessage(role="assistant",
                                            content=content))

                elif hasattr(message, 'additional_kwargs'):
                    if message.additional_kwargs != {}:
                        print(message.additional_kwargs)
                        print(type(message.additional_kwargs))
                        # {'function_call': {'arguments': '{"query":"weather in San Francisco"}', 'name': 'tavily_search_results_json'}}

                        function_name = message.additional_kwargs['function_call']['name']

                        content = f"**Calling Function:**\n{function_name}({message.additional_kwargs['function_call']['arguments']})"

                        st.markdown(content)
                        st.session_state.appstate.chat.messages.append(
                                            ChatMessage(role="assistant",
                                            content=content))

            else:
                # TODO - FIX THIS.... this logic should be placed inside the Graph class for each chain
                try:
                    message = output['messages'][-1]
                    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=message.content))
                except TypeError:
                    message = output
                    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=message))

    try:
        return message.content
    except AttributeError:
        return message
