import yaml
import pathlib
import streamlit as st



# def save_user_preferences(update_key=None, toggle_key=None):
#     print(f"save_user_preferences({update_key}, {toggle_key})")

#     if update_key is None and toggle_key is None:
#         raise ValueError("Either key_to_save or toggle_key must be set")


#     if toggle_key is not None:
#         st.session_state.user_preferences[toggle_key] = False if st.session_state.user_preferences[toggle_key] is True else True
        

#     if update_key is not None:
#         st.session_state.user_preferences[update_key] = st.session_state[update_key]

#     preferences_file = PREFERENCES_PATH / f"{st.session_state.username}.yaml"
#     with open(preferences_file, "w") as f:
#         yaml.dump(st.session_state.user_preferences, f)

#     del st.session_state.user_preferences
#     st.toast("User preferences saved!")

#     # we need to ensure we destory the old client so a new one with the new settings is init'd
#     if 'model' in st.session_state:
#         del st.session_state.model
