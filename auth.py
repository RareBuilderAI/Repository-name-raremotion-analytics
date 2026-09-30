import streamlit as st
from supabase import create_client


def get_supabase():
    return create_client(
        st.secrets["SUPABASE_URL"],
        st.secrets["SUPABASE_KEY"],
    )


def show_auth():
    supabase = get_supabase()

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is not None:
        return st.session_state.user

    st.title("📊 Raremotion Analytics")
    st.write("Sign in to analyze your business data.")

    login_tab, signup_tab = st.tabs(["Login", "Create Account"])

    with login_tab:
        login_email = st.text_input(
            "Email",
            key="login_email",
        )

        login_password = st.text_input(
            "Password",
            type="password",
            key="login_password",
        )

        if st.button("Login", type="primary"):
            if not login_email or not login_password:
                st.warning("Enter your email and password.")
            else:
                try:
                    response = supabase.auth.sign_in_with_password(
                        {
                            "email": login_email,
                            "password": login_password,
                        }
                    )

                    if response.user:
                        st.session_state.user = response.user
                        st.success("Login successful.")
                        st.rerun()

                except Exception as error:
                    st.error(f"Login failed: {error}")

    with signup_tab:
        signup_email = st.text_input(
            "Email",
            key="signup_email",
        )

        signup_password = st.text_input(
            "Password",
            type="password",
            key="signup_password",
        )

        confirm_password = st.text_input(
            "Confirm Password",
            type="password",
            key="confirm_password",
        )

        if st.button("Create Account"):
            if not signup_email or not signup_password:
                st.warning("Enter an email and password.")

            elif signup_password != confirm_password:
                st.error("Passwords do not match.")

            elif len(signup_password) < 6:
                st.error("Password must contain at least 6 characters.")

            else:
                try:
                    response = supabase.auth.sign_up(
                        {
                            "email": signup_email,
                            "password": signup_password,
                        }
                    )

                    if response.user:
                        st.success(
                            "Account created. Check your email if confirmation is required, then log in."
                        )

                except Exception as error:
                    st.error(f"Account creation failed: {error}")

    st.stop()
