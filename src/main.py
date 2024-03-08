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
    # interrupt,
)

from src.common import (
    ASSETS_PATH,
    AVATAR_PATH,
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
    show_tokens,
    load_sats_balance,
    display_invoice_link,
    display_invoice_pane
)

from src.run_prompt import run_prompt, run_graph

from src.VERSION import VERSION


class ChatAppVars:
    def __init__(self):
        self.chat = ChatThread()

        self.chat_history_depth = 20
        self.chat_history = None # the list of past conversations list of (description, runlog file name)
        # self.load_chat_history()

    def new_thread(self):
        self.chat = ChatThread()

    def increase_chat_history_depth(self):
        self.chat_history_depth += 20
        self.load_chat_history()

    def load_chat_history(self):
        self.chat_history = []





def init_if_needed():
    if not_init('appstate'):
        try:
            st.session_state.appstate: ChatAppVars = ChatAppVars()
        except Exception as e:
            st.error(e)
            st.exception(e)
            st.stop()
    # not sure if this should be here or in main...
    # st.session_state.sats = load_sats_balance()


    # TODO use @st.cache_resource
    st.session_state.redis_conn = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

    user_sats = st.session_state.redis_conn.get(get("user_uuid"))

    if user_sats is None:
        st.session_state.redis_conn.set(get("user_uuid"), 0)
        st.toast("Welcome to the chat app!", icon="🎉")




def load_proper_flow(construct):
    if is_init("construct"):

        if get('construct').name != construct:
            # update_persistance('chosen_pill', [c.name for c in ALL_CONSTRUCTS].index(construct))
            # save to cookies
            set_cookie("chosen_pill", [c.name for c in ALL_CONSTRUCTS].index(construct))

            st.session_state.appstate.new_thread()
        else:
            return


    # Use ALL_CONSTRUCTS to dynamically instantiate the correct construct
    for Construct in ALL_CONSTRUCTS:
        if Construct.name == construct:
            st.session_state["construct"] = Construct()
            st.rerun() # we need this to reload the page with the new construct
    else:
        raise Exception(f"Unknown construct: {construct} - fix this!")




def ensure_uuid():
    if is_init("user_uuid"):
        return

    user_uuid_cookie = get_cookie("user_uuid")
    if user_uuid_cookie is None:
        with st.container(border=True):
            show_new_user()
    else:
        set("user_uuid", user_uuid_cookie)
        # cprint(f"user_uuid: {user_uuid_cookie}", Colors.RED)


def save_chat_history():
    return True

def delete_this_chat():
    pass

def load_convo():
    pass

def main():
    cprint("\n\n>> main()\n", Colors.YELLOW)
    st.set_page_config(
        page_title="DEBUG!" if os.getenv("DEBUG", False) else "Pleb Chat",
        page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
        layout="centered",
        initial_sidebar_state="auto",
    )

    load_cookies()
    ensure_uuid()  ## <--- execution stops here for new users
    init_if_needed()

    load_ui_persistance()
    # show_nuke_button()

    ## SHOW COOKIES
    # with st.container(border=True):
    #     for cookie, value in st.session_state.cookie_manager.items():
    #         st.write(f"`{cookie}`: {value}")



    # st.stop()

    appstate = st.session_state.appstate



    ################### TOP OF MAIN CHAT ###################
    column_fix()
    center_text("p", "🗣️🤖💬", size=60) # or h1, whichever

    construct_names = [c.name for c in ALL_CONSTRUCTS]
    construct_icons = [c.emoji for c in ALL_CONSTRUCTS]
    # pill_index = get("persistance")['chosen_pill']
    # load from cookie
    pill_index = int(get_cookie("chosen_pill"))
    # if we play around in debug and switch to production, we need to make sure we don't go out of bounds
    if pill_index >= len(construct_names):
        pill_index = 0
    construct = pills(label="Choose an AI workflow:",
                    options=construct_names,
                    icons=construct_icons,
                    index=pill_index
                )

    try:
        load_proper_flow(construct)
    except Exception as e:
        st.error(e)
        st.exception(e)
        # st.stop()

    cols2 = st.columns((1, 1, 1))

    with cols2[2]:
        show_tokens()


    ### info card
    with st.expander("Information about this AI workflow", expanded=False):
        get('construct').display_model_card()

    st.header("", divider="rainbow")



    if os.getenv("DEBUG", False):
        with st.expander(":red[Debug] ❤️‍🩹", expanded=False):
            debug_placeholder = st.container()
            debug_placeholder.write(get("construct"))
            debug_placeholder.write(st.session_state.appstate.chat.messages)
    ####### CONVERSATION #######



    # TODO - turn this into a settings
    if os.getenv("DEBUG", False):
        human_avatar = f"{AVATAR_PATH}/user69.png"
    else:
        human_avatar = f"{AVATAR_PATH}/user0.png"

    # ai_avatar = f"{AVATAR_PATH}/assistant.png"
    ai_avatar = f"{AVATAR_PATH}/{get('construct').avatar_filename}"

    for message in appstate.chat.messages:
        with st.chat_message(message.role, avatar=ai_avatar if message.role == "assistant" else human_avatar):
            st.markdown(message.content)

    # This is so that we can later populate with the users' next prompt
    # and the bots reply and allows the input field (or start recording button)
    # to be at the bottom of the page
    my_next_prompt_placeholder = st.empty()
    cols2 = st.columns((1, 1))
    with cols2[0]:
        interrupt_button_placeholder = st.empty()
    with cols2[1]:
        sats_left_placeholder = st.empty()
    # thinking_placeholder = st.empty()
    bots_reply_placeholder = st.empty()
    before_speech_placeholder = st.empty()

    # if len(appstate.chat.messages) > 0:
    #     st.header("", divider="rainbow")






    ################### TOP OF SIDEBAR ###################
    construct_settings_placeholder = st.sidebar.empty()


    #### USER PROMPT AND ASSOCIATED LOGIC
    prompt = None
    if 'speech_draft' not in st.session_state:
        st.session_state.speech_draft = None
        st.session_state.speech_confirmed = False



    sats = load_sats_balance()
    if sats <= 0:
        st.error("You are out of tokens! Please add more to continue.")
        prompt = None
    else:
        prompt = st.chat_input("Ask a question.")

    if prompt:
        st.session_state.speech_confirmed = False

        interrupt_button_placeholder.button("🛑 Interrupt", on_click=interrupt, key="button_interrupt")

        my_next_prompt_placeholder.chat_message("user", avatar=human_avatar).markdown(prompt)
        st.session_state.appstate.chat.messages.append( ChatMessage(role="user", content=prompt) )


        if get("construct").agentic:
            reply = run_graph(prompt, bots_reply_placeholder)
        else:
            with st.spinner("🧠 Thinking..."):
                reply = run_prompt(prompt, bots_reply_placeholder, sats_left_placeholder)



        #### AFTER-PROMPT PROCESSING ####
        new_chat = save_chat_history() # dummy variable for readability
        if new_chat:
            # A new chat thread has just been created, so we must update our list of past conversations
            appstate.load_chat_history()






    ### NEW / DELETE BUTTONS
    with before_speech_placeholder:
        if len(appstate.chat.messages) > 0:
            col2 = st.columns((1, 1, 1))
            col2[1].button("🌱 :green[New]", on_click=lambda: appstate.new_thread(), use_container_width=True)
            col2[0].button("🗑️ :red[Delete]", on_click=delete_this_chat, key="button_delete", use_container_width=True)



    appstate.load_chat_history()
    

    with st.sidebar:
        st.header("", divider="rainbow")
        # st.write("## :rainbow[Past Conversations]")
        st.write("## :orange[Past Conversations]")

        if len(appstate.chat.messages) > 0:
            sidebar_new_button_placeholder = st.columns((1, 1))
            sidebar_new_button_placeholder[0].button("🗑️ :red[Delete]", on_click=delete_this_chat, key="delbutton2", use_container_width=True)
            sidebar_new_button_placeholder[1].button("🌱 :green[New]", on_click=lambda: appstate.new_thread(), use_container_width=True, key="newbutton2")
            center_text('p', "---", size=9)

        if len(appstate.chat_history) == 0:
            st.caption("No past conversations... yet")
        for description, runlog in appstate.chat_history:
            st.button(f"{description}", on_click=load_convo, args=(runlog,), use_container_width=True, key=runlog.split('.')[0])
        # if appstate.truncated:
        #     st.caption(f"Only showing last {appstate.chat_history_depth} conversations")
        #     st.button("Load more...", use_container_width=True, key="load_more_button", on_click=appstate.increase_chat_history_depth)

        st.header("", divider="rainbow")

        display_invoice_pane()

        show_nuke_button()


        caption = f"Version :green[{VERSION}] | "
        if os.getenv("DEBUG", False):
            caption += ":orange[DEBUG] | "
        caption += "by PlebbyG 🧑🏻‍💻"
        st.caption(caption)



    # we don't use an expander becuase the construct settings may need to have one
    # with construct_settings_placeholder.expander("Construct settings", expanded=True):
    with construct_settings_placeholder.container(border=False):
        st.write("## :orange[Configuration]")
        get('construct').display_settings()







def interrupt():
    """ callback for the interrupt button """
    st.session_state.appstate.chat.messages.append(ChatMessage(role="assistant", content=st.session_state.incomplete_stream))
    st.session_state.appstate.chat.messages.append(ChatMessage(role="user", content="<INTERRUPTS>"))

    st.session_state.redis_conn.decrby(st.session_state.username, st.session_state.token_cost_accumulator)
    st.session_state.token_cost_accumulator = 0

    if save_chat_history():
        st.session_state.appstate.load_chat_history()
