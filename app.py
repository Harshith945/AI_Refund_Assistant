"""
app.py
------
Main Streamlit app for HuggingFace Spaces deployment.
GROQ_API_KEY must be set in Spaces Settings -> Secrets.
"""

import os
import base64
import streamlit as st

# ── GROQ API KEY — set in HuggingFace Spaces > Settings > Secrets ─────────────
GROQ_API_KEY = os.environ.get("GROQ_API_KEY", "")

st.set_page_config(page_title="AI Refund Assistant", page_icon="💸", layout="wide")

if not GROQ_API_KEY:
    st.error(
        "⚠️ **GROQ_API_KEY is not set.**\n\n"
        "Go to your HuggingFace Space → **Settings → Secrets** → Add `GROQ_API_KEY`."
    )
    st.stop()

st.markdown("""
<style>
.block-container { padding-top: 1rem; padding-bottom: 0; }
[data-testid="stExpander"] > div:first-child {
    border-radius: 8px; border: 1px solid #444;
    padding: 2px 10px; width: fit-content; font-size: 1.1rem;
}
</style>
""", unsafe_allow_html=True)

from database        import companies, detect_company_from_query, get_policy_context, \
                            get_process_context, get_combined_context, get_doc_category
from chains          import main_chain, confirmation_chain, llm
from renderers       import render_response, render_confirmation
from image_analysis  import encode_image_to_base64, analyze_proof_image
from utils           import is_greeting, get_query_category, \
                            needs_image_proof_local, detect_proof_category
from langchain_core.messages import HumanMessage

# ── SESSION STATE ──────────────────────────────────────────────────────────────
for key, default in {
    "history":        [],
    "awaiting_proof": False,
    "proof_claim":    "",
    "proof_category": "",
    "uploader_key":   0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# ── SIDEBAR ────────────────────────────────────────────────────────────────────
with st.sidebar:
    st.title("💸 Refund Assistant")
    selected_company = st.selectbox("🏢 Select Company", ["All"] + companies)
    st.divider()

    if st.button("🗑️ Clear Chat"):
        st.session_state.history        = []
        st.session_state.awaiting_proof = False
        st.session_state.proof_claim    = ""
        st.session_state.proof_category = ""
        st.rerun()

    if st.session_state.awaiting_proof:
        st.divider()
        _cat = st.session_state.proof_category
        _proof_label = (
            "Upload a **screenshot** of the billing/activation issue."
            if _cat == "digital"
            else "Upload a **clear photo** of the item."
        )
        st.warning(
            f"📸 **Proof pending**\n\n*\"{st.session_state.proof_claim[:80]}\"*\n\n"
            f"{_proof_label}\n\nUse **➕ Attach image** beside the chat box."
        )
        if st.button("❌ Cancel"):
            st.session_state.awaiting_proof = False
            st.session_state.proof_claim    = ""
            st.session_state.proof_category = ""
            st.rerun()

# ── CHAT HISTORY ───────────────────────────────────────────────────────────────
st.title("💸 Refund AI Assistant")

for msg in st.session_state.history:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        if msg.get("image_b64"):
            st.image(base64.b64decode(msg["image_b64"]), width=200)
        if msg.get("image_ctx"):
            with st.expander("📎 Evidence context"):
                st.caption(msg["image_ctx"])

# ── INPUT ──────────────────────────────────────────────────────────────────────
with st.expander("➕  Attach image"):
    uploaded_image = st.file_uploader(
        "Upload photo or screenshot",
        type=["jpg", "jpeg", "png", "webp"],
        label_visibility="collapsed",
        key=f"uploader_{st.session_state.uploader_key}",
    )
    if uploaded_image:
        st.image(uploaded_image, width=200)

query = st.chat_input("Describe your issue or ask a refund question…")

# ── MAIN FLOW ──────────────────────────────────────────────────────────────────
if query:
    image_b64      = None
    media_type_img = None
    proof_result   = None
    saved_b64      = None
    img_ctx_out    = ""

    if uploaded_image is not None:
        mime_map       = {"jpg": "image/jpeg", "jpeg": "image/jpeg",
                          "png": "image/png",  "webp": "image/webp"}
        ext            = uploaded_image.name.rsplit(".", 1)[-1].lower()
        media_type_img = mime_map.get(ext, "image/jpeg")
        image_b64      = encode_image_to_base64(uploaded_image)
        saved_b64      = image_b64

    with st.chat_message("user"):
        st.markdown(query)
        if saved_b64:
            st.image(base64.b64decode(saved_b64), width=200)

    st.session_state.history.append({
        "role": "user", "content": query, "image_b64": saved_b64
    })

    response = ""

    try:
        # ── Analyze image if attached ──────────────────────────────────────────
        if image_b64 is not None:
            with st.spinner("Analyzing image…"):
                cat          = st.session_state.proof_category or detect_proof_category(query)
                proof_result = analyze_proof_image(image_b64, media_type_img, cat)
                img_ctx_out  = proof_result["description"]

        # ── PATH A: Image proof for a pending claim ────────────────────────────
        if proof_result is not None and st.session_state.awaiting_proof:
            resolved_company = detect_company_from_query(
                st.session_state.proof_claim, selected_company
            )
            context = get_combined_context(resolved_company, st.session_state.proof_claim)
            parsed  = confirmation_chain.invoke({
                "claim":          st.session_state.proof_claim,
                "image_analysis": proof_result["description"],
                "verdict":        proof_result["verdict"],
                "context":        context,
            })
            response = render_confirmation(parsed)
            st.session_state.awaiting_proof = False
            st.session_state.proof_claim    = ""
            st.session_state.proof_category = ""

        # ── PATH B: Greeting ───────────────────────────────────────────────────
        elif is_greeting(query) and image_b64 is None:
            response = (
                "Hello! 👋 Welcome to the Refund Assistant.\n\n"
                "I can help you with:\n"
                "- Checking refund / exchange eligibility\n"
                "- Understanding return and cancellation policies\n"
                "- Step-by-step refund, exchange, or cancellation process\n\n"
                "Just describe your issue or ask any question about your order!"
            )

        # ── PATH C: All refund queries ─────────────────────────────────────────
        else:
            resolved_company = detect_company_from_query(query, selected_company)
            category         = get_doc_category(resolved_company, query)
            query_category   = get_query_category(query)

            if (selected_company != "All"
                    and category and query_category
                    and query_category != category):
                response = (
                    f"⚠️ This doesn't seem related to **{selected_company}**.\n\n"
                    f"{selected_company} handles **{category}** products. "
                    "Please check the company selection or rephrase your query."
                )
            else:
                policy_context  = get_policy_context(resolved_company, query)
                process_context = get_process_context(resolved_company)

                parsed   = None
                raw_text = ""
                for attempt in range(2):
                    try:
                        parsed = main_chain.invoke({
                            "policy_context":  policy_context,
                            "process_context": process_context,
                            "question":        query,
                        })
                        break
                    except Exception:
                        if attempt == 0:
                            continue
                        try:
                            raw_text = llm.invoke([HumanMessage(content=(
                                f"You are a Refund Policy Assistant.\n\n"
                                f"POLICY:\n{policy_context}\n\n"
                                f"PROCESS:\n{process_context}\n\n"
                                f"Answer this question clearly: {query}"
                            ))]).content
                        except Exception as e2:
                            raw_text = f"I encountered an issue. Please try again. ({e2})"

                if parsed is not None:
                    response    = render_response(parsed, query)
                    needs_proof = (
                        parsed.needs_image_proof or needs_image_proof_local(query)
                    )
                    if (needs_proof
                            and parsed.response_type == "eligibility"
                            and parsed.verdict != "Not Eligible"):
                        st.session_state.awaiting_proof = True
                        st.session_state.proof_claim    = query
                        st.session_state.proof_category = detect_proof_category(
                            query, resolved_company
                        )
                        cat = st.session_state.proof_category
                        if cat == "digital":
                            proof_msg = (
                                "📸 **Please upload a screenshot as proof.**\n\n"
                                "Click **➕ Attach image** above, upload a screenshot "
                                "showing the billing issue or activation error, then send any message."
                            )
                        elif cat == "food":
                            proof_msg = (
                                "📸 **Please upload a photo of the food item as proof.**\n\n"
                                "Click **➕ Attach image** above, upload a clear photo "
                                "showing the spoilage, expiry label, or incorrect item received."
                            )
                        elif cat == "clothing":
                            proof_msg = (
                                "📸 **Please upload a photo of the clothing item as proof.**\n\n"
                                "Click **➕ Attach image** above, upload a clear photo "
                                "showing the damage, defect, or incorrect item received."
                            )
                        else:
                            proof_msg = (
                                "📸 **Please upload a photo of the item as proof.**\n\n"
                                "Click **➕ Attach image** above, upload a clear photo "
                                "showing the damage, defect, or incorrect item received."
                            )
                        response += f"\n\n---\n{proof_msg}"
                else:
                    response = raw_text

    except Exception as e:
        response = f"⚠️ Something went wrong: {e}"

    with st.chat_message("assistant"):
        st.markdown(response)
        if img_ctx_out:
            with st.expander("📎 Evidence context"):
                st.caption(img_ctx_out)

    st.session_state.history.append({
        "role": "assistant", "content": response, "image_ctx": img_ctx_out,
    })
    st.session_state.uploader_key += 1
    st.rerun()
