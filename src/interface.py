import uuid

import streamlit as st


from src.chat_history import (
    save_chat_history,
)


def column_fix():
    st.write("""<style>
[data-testid="column"] {
    width: calc(33.3333% - 1rem) !important;
    flex: 1 1 calc(33.3333% - 1rem) !important;
    min-width: calc(33% - 1rem) !important;
}
</style>""", unsafe_allow_html=True)



def center_text(type, text, size=None):
    if size == None:
        st.write(f"<{type} style='text-align: center;'>{text}</{type}>", unsafe_allow_html=True)
    else:
        st.write(f"<{type} style='text-align: center; font-size: {size}px;'>{text}</{type}>", unsafe_allow_html=True)


def centered_button_trick():
    """ Use this in a `with` statement to center a button.
    
    Example:
    ```python
    with centered_button_trick():
        st.button(
            "👈 back",
            on_click=go_to_main_page,
            use_container_width=True)
    ```
    """
    columns = st.columns((1, 2, 1))
    with columns[0]:
        st.empty()
    # with columns[1]:
        # normally the button logic would go here
    with columns[2]:
        st.empty()

    return columns[1]




def show_new_user():
    st.markdown("## Welcome to Pleb Chat!")
    st.write("You are being registered as a new user")
    st.write("All data will be stored in your browser")
    st.write("If you clear your cookies, you will lose your data")
    st.write("Enjoy your stay!")

    I_read_it_1 = st.checkbox("I read it")

    if I_read_it_1:
        st.write("Please read the following")
        st.write("DO NOT PAY MORE SATS THAN YOU WILL USE")

        I_accept = st.button("I accept")

        if I_accept:
            st.session_state.cookie_manager["user_uuid"] = str(uuid.uuid4())
            st.session_state.cookie_manager.save()# (key=str(uuid.uuid4()))
            st.write("UUID set, please refresh the page")
            st.rerun()

    st.stop()


def show_nuke_button():
    # pass
    # nuke = st.sidebar.button("Nuke")

    # if st.sidebar.button(":red[Delete all data]"):
    if st.sidebar.button(f":red[NUKE DATA 🔥]"):
        # duke_nuke_em()
        # st.session_state.cookie_manager.clear()
        # st.session_state.cookie_manager.clear()
        for c in st.session_state.cookie_manager:
            del st.session_state.cookie_manager[c]

        st.session_state.cookie_manager.save()

        for k in st.session_state:
            print(k)
            del st.session_state[k]

        # st.rerun()
        st.stop()

