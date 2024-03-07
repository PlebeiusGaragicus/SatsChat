

import os
import uuid

import streamlit as st

# from streamlit.runtime.scriptrunner import get_script_run_ctx
# import extra_streamlit_components as stx


from src.common import (
    ASSETS_PATH,
    is_init,
    not_init,
    get,
    set,
    cprint,
    Colors,
)

from src.cookies import load_ui_persistance, get_cookie, load_cookies




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
            st.session_state.cookie_manager.save()
            st.write("UUID set, please refresh the page")
            st.rerun()

    st.stop()


        # st.toast("No UUID found, creating new one")
        # new_uuid = uuid.uuid4()
        # st.session_state.cookie_manager["user_uuid"] = str(new_uuid)
        # st.session_state.cookie_manager.save()

        # set("user_uuid", new_uuid) # INIT user_uuid
        # st.toast(f"New UUID: {new_uuid}")
        # cprint(f"New UUID: {new_uuid}", Colors.YELLOW)
        # st.rerun()



def ensure_uuid():
    if is_init("user_uuid"):
        return

    user_uuid_cookie = get_cookie("user_uuid")
    if user_uuid_cookie is None:
        with st.container(border=True):
            show_new_user()



def main():
    st.set_page_config(
        page_title="DEBUG!" if os.getenv("DEBUG", False) else "Pleb Chat",
        page_icon=os.path.join(ASSETS_PATH, "favicon.ico"),
        layout="centered",
        initial_sidebar_state="auto",
    )

    load_cookies()
    ensure_uuid()
    load_ui_persistance()
    st.write("245205b9-8482-4a35-a7e5-ea7c3972e014")

    show_nuke_button()


    # Write cookies
    # cookies["a-cookie"] = 1
    # del st.session_state.cookie_manager["a-cookie"]
    # st.session_state.cookie_manager.save()


def show_nuke_button():
    # nuke = st.sidebar.button("Nuke")
    if st.sidebar.button("Nuke"):
        # st.session_state.cookie_manager.nuke()
        st.write("Nuked")
