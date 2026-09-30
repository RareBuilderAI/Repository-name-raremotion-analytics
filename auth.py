import streamlit as st
from supabase import create_client


class SessionUnavailable(ValueError):
    """No current session belonging to the requested user."""


def bind_authenticated_session(client, user_id):
    """Refresh if needed, then explicitly bind database requests to this user."""
    session = client.auth.get_session()
    if not session or str(session.user.id) != str(user_id) or not session.access_token:
        raise SessionUnavailable("Sign-in session unavailable")
    client.postgrest.auth(session.access_token)
    return session


def get_supabase():
    # Never share an authenticated client across Streamlit user sessions.
    if "supabase_client" not in st.session_state:
        st.session_state.supabase_client = create_client(
            st.secrets["SUPABASE_URL"],
            st.secrets["SUPABASE_KEY"],
        )
    return st.session_state.supabase_client


def show_auth():
    supabase = get_supabase()

    if "user" not in st.session_state:
        st.session_state.user = None

    if st.session_state.user is not None:
        try:
            session = bind_authenticated_session(supabase, st.session_state.user.id)
        except Exception:
            session = None
        if session and session.user.id == st.session_state.user.id:
            return st.session_state.user
        # Existing browser sessions from before this change must sign in again.
        st.session_state.user = None
        st.session_state.pop("analysis_access", None)

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

                    if response.user and response.session:
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
