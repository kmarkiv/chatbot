import streamlit as st
import json
from openai import OpenAI

st.title("💬 Mann Sakhi — Chatbot")
st.write(
    "A chatbot to provide reliable information for sexual and mental wellness. "
    "V: " + st.secrets["srhr_version"]
)

language_options = {
    "हिन्दी (Hindi)": "Hindi",
    "English": "English",
    "தமிழ் (Tamil)": "Tamil"
}

selected_label = st.selectbox(
    "Choose language / भाषा चुनें / மொழியைத் தேர்ந்தெடுக்கவும்",
    list(language_options.keys())
)

language = language_options[selected_label]

openai_api_key = st.secrets["openai_api_key"]

if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")

else:
    client = OpenAI(api_key=openai_api_key)

    if "messages" not in st.session_state:
        st.session_state.messages = []

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if prompt := st.chat_input("अपना सवाल लिखें / Ask your question / உங்கள் கேள்வியை எழுதுங்கள்"):

        st.session_state.messages.append({
            "role": "user",
            "content": prompt
        })

        with st.chat_message("user"):
            st.markdown(prompt)

        response = client.responses.create(
            prompt={
                "id": st.secrets["srhr_prompt_id"],
                "version": st.secrets["srhr_version"]
            },
            input=[
                {
                    "role": "system",
                    "content": (
                        f"Respond only in {language}. "
                        "Keep the Mann Sakhi tone. "
                        "Return only one JSON object. "
                        "Keep JSON keys in English."
                    )
                },
                *[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            ],
            stream=False,
        )

        raw_text = response.output_text.strip()

        try:
            parsed = json.loads(raw_text)

            assistant_response = parsed.get("response", raw_text)
            confidence = parsed.get("confidence", None)
            sources = parsed.get("sources", [])
            theme = parsed.get("theme", "")
            in_kb = parsed.get("in_knowledge_base", False)

        except json.JSONDecodeError:
            assistant_response = raw_text
            confidence = None
            sources = []
            theme = ""
            in_kb = False

        with st.chat_message("assistant"):
            st.markdown(assistant_response)

            with st.expander("Response details"):
                st.write("Theme:", theme)
                st.write("Confidence:", confidence)
                st.write("In knowledge base:", in_kb)
                st.write("Sources:", sources)

        st.session_state.messages.append({
            "role": "assistant",
            "content": assistant_response
        })
