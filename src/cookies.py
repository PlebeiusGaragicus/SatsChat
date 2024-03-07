import os
import uuid

import streamlit as st
# import extra_streamlit_components as stx
from streamlit_cookies_manager import CookieManager



from src.common import (
    ASSETS_PATH,
    is_init,
    not_init,
    get,
    set,
    cprint,
    Colors,
)





# @st.cache_resource(experimental_allow_widgets=True)
# def get_cookie_manager():
#     cm = stx.CookieManager()
#     # import time
#     # time.sleep(1)
#     return cm



# def cookie_sheet():
#     cookie_manager = get_cookie_manager()

#     cookies = cookie_manager.get_all()
#     st.write(cookies)

#     c1, c2, c3 = st.columns(3)
#     with c1:
#         cookie = st.text_input("Cookie", key="0")
#         clicked = st.button("Get")
#         if clicked:
#             value = cookie_manager.get(cookie=cookie)
#             st.write(value)

#     with c2:
#         cookie = st.text_input("Cookie", key="1")
#         val = st.text_input("Value")
#         if st.button("Add"):
#             cookie_manager.set(cookie, val) # Expires in a day by default

#     with c3:
#         cookie = st.text_input("Cookie", key="2")
#         if st.button("Delete"):
#             cookie_manager.delete(cookie)

#     get_all = st.button("Get All")
#     if get_all:
#         cookies = cookie_manager.cookies
#         st.write(cookies)


#     delete_all = st.button("Delete All")
#     if delete_all:
#         while len(cookie_manager.cookies) > 0:
#             c = list(cookie_manager.cookies.keys())[0]
#             cookie_manager.delete(c, key=str(uuid.uuid4()))



# def load_ui_persistance():
    # cookie_manager = get_cookie_manager()

    # if not_init("chosen_pill"):
    #     chosen_pill_cookie = cookie_manager.get("chosen_pill")
    #     if chosen_pill_cookie is None:
    #         cookie_manager.set("chosen_pill", "0", key=str(uuid.uuid4()))
    #         set("chosen_pill", "0")
    #         cprint(f"chosen_pill: 0", Colors.RED)
    #     else:
    #         # TODO - check that loaded value is valid... if < len(pills)...
    #         set("chosen_pill", chosen_pill_cookie)
    #         cprint(f"Loaded chosen_pill: {chosen_pill_cookie}", Colors.YELLOW)


# def set_cookie(key, value):
#     cookie_manager = get_cookie_manager()
#     cookie_manager.set(key, value)



def get_cookie(c):
    return st.session_state.cookie_manager.get(c)


def set_cookie(c, v):
    st.session_state.cookie_manager[c] = v
    st.session_state.cookie_manager.save()
    # TODO cprint debug here


def load_cookies():
    if not_init("cookies"):
        st.session_state.cookie_manager = CookieManager() #TODO make @cache_resource

        if not st.session_state.cookie_manager.ready():
            st.stop()

    for cookie, value in st.session_state.cookie_manager.items():
        st.write(f"`{cookie}`: {value}")


def load_ui_persistance():
    if not_init("chosen_pill"):
        pill = get_cookie("chosen_pill")
        if pill is None:
            set("chosen_pill", "0")
            set_cookie("chosen_pill", 0)
            cprint(f"chosen_pill: 0", Colors.RED)

    # TODO - load other UI persistance here
