"""Explicit, session-scoped authorization before the V5 dashboard runs."""

import hashlib
import logging

import streamlit as st

from auth import get_supabase, bind_authenticated_session, SessionUnavailable

logger = logging.getLogger(__name__)


def read_usage(client, user_id):
    bind_authenticated_session(client, user_id)
    rows = (client.table("profiles")
            .select("free_analyses_used,paid_credits")
            .eq("id", str(user_id)).limit(1).execute().data)
    if not rows:
        raise LookupError("Profile not readable for current user")
    used, credits = rows[0]["free_analyses_used"], rows[0]["paid_credits"]
    if type(used) is not int or type(credits) is not int or used < 0 or credits < 0:
        raise ValueError("Invalid usage counters")
    return used, credits


def consume_analysis(client):
    """Fail closed unless the authenticated RPC explicitly grants access."""
    result = client.rpc("consume_analysis").execute().data
    if isinstance(result, list) and len(result) == 1:
        result = result[0]
    if not isinstance(result, dict) or type(result.get("allowed")) is not bool:
        raise ValueError("Unexpected analysis authorization response")
    return result["allowed"]


def show_usage(client, user_id):
    try:
        used, credits = read_usage(client, user_id)
    except SessionUnavailable:
        st.warning("Your sign-in session is unavailable. Please reload and sign in again.")
        return
    except LookupError:
        st.warning("Your profile could not be read for this signed-in account. Please sign in again; if this continues, contact support.")
        return
    except Exception as error:
        # Never log JWTs, profile data, or raw server exception messages.
        code = str(getattr(error, "code", "unknown"))
        logger.warning("Usage read failed: %s code=%s", type(error).__name__,
                       code if code.isalnum() else "unknown")
        st.caption("Usage status is temporarily unavailable.")
        return
    st.caption(f"Free analyses remaining: {max(0, 2 - used)} · Paid credits: {credits}")


def require_analysis_access(user, csv_bytes):
    client = get_supabase()
    identity = (user.id, hashlib.sha256(csv_bytes).hexdigest())
    access = st.session_state.get("analysis_access")
    if not access or access["identity"] != identity:
        access = {"identity": identity, "status": "ready"}
        st.session_state.analysis_access = access

    # A completed upload cannot be charged again by queued clicks or widget reruns.
    clicked = st.button("Analyze Data", type="primary",
                        disabled=access["status"] != "ready")
    if clicked and access["status"] == "ready":
        access["status"] = "pending"
        try:
            bind_authenticated_session(client, user.id)
            allowed = consume_analysis(client)
            access["status"] = "allowed" if allowed else "blocked"
        except Exception:
            # A timeout can happen AFTER a charge. Never automatically retry it.
            access["status"] = "uncertain"

    show_usage(client, user.id)
    if access["status"] == "allowed":
        st.caption("This dataset is ready. Exploring it or asking questions uses no additional analysis.")
        if st.button("Start another analysis"):
            st.session_state.analysis_access = {"identity": identity, "status": "ready"}
            st.rerun()
        return
    if access["status"] == "blocked":
        st.error("Payment required: you have used your 2 free analyses and have no paid credits remaining. Add credits to continue. Payments are not available in the app yet.")
    elif access["status"] in ("pending", "uncertain"):
        st.error("We could not confirm the analysis result. Your allowance may have been used. Analysis has stopped; check your usage before starting another analysis.")
    else:
        st.info("Click Analyze Data to use one free analysis or one paid credit.")
    if access["status"] != "ready" and st.button("Start another analysis"):
        st.session_state.analysis_access = {"identity": identity, "status": "ready"}
        st.rerun()
    st.stop()
