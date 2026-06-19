# app_streamlit.py — STEP F: a web UI for NutriCoach
#
# Streamlit turns a Python script into a web page. Run it with:
#   streamlit run app_streamlit.py
# (run from inside the nutricoach/ folder, with the venv active.)

import streamlit as st
from agent import decide, run

st.set_page_config(page_title="NutriCoach", page_icon="🥗")

st.title("🥗 NutriCoach")
st.caption("AI nutrition advisor — RAG + agent. General info, not medical advice.")

question = st.text_input("Ask a nutrition or health question:")

if st.button("Ask") and question:
    # Show the agent's decision FIRST — this is the "explain its decisions"
    # requirement, made visible to whoever is watching your demo.
    with st.spinner("🧠 Deciding how to answer..."):
        decision = decide(question)

    st.info(
        f"**Agent decision:** `{decision.get('action', 'rag')}`  \n"
        f"**Reasoning:** {decision.get('reasoning', '(none)')}"
    )

    # Then run the full pipeline (reusing the SAME decision) and show the answer.
    with st.spinner("Thinking..."):
        st.write(run(question, decision=decision))
