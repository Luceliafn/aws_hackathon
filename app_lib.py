import streamlit as st
import pandas as pd
import ast
import hmac

def check_password():
    """Returns `True` if the user had a correct password."""

    def login_form():
        
        # Centralizar a imagem usando HTML
        st.markdown(
            """
            <style>
            .center {
                display: flex;
                justify-content: center;
            }
            </style>
            <br/>
            """,
            unsafe_allow_html=True
        )

        hide_decoration_bar_style = '''
            <style>
                header {visibility: hidden;}
            </style>
        '''
        st.markdown(hide_decoration_bar_style, unsafe_allow_html=True)

        with st.form("Credentials"):
            st.text_input("Usuário", key="username")
            st.text_input("Senha", type="password", key="password")
            st.form_submit_button("Login", on_click=password_entered)

    def password_entered():
        """Checks whether a password entered by the user is correct."""
        if st.session_state["username"] in st.secrets[
            "passwords"
        ] and hmac.compare_digest(
            st.session_state["password"],
            st.secrets.passwords[st.session_state["username"]],
        ):
            st.session_state["password_correct"] = True
            del st.session_state["password"]  # Don't store the username or password.
            del st.session_state["username"]
        else:
            st.session_state["password_correct"] = False

    # Return True if the username + password is validated.
    if st.session_state.get("password_correct", False):
        return True

    # Show inputs for username + password.
    login_form()
    if "password_correct" in st.session_state:
        st.error("😕 Usuário não encontrado or senha incorreta")
    return False

