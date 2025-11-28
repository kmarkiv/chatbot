import streamlit as st
from openai import OpenAI

# Show title and description.
st.title("💬 Dr. Didi — Chatbot for Sexual & Mental Health")
st.write(
    "A chatbot to provide reliable "
    "information for sexual and mental wellness. "
    "V: " + st.secrets["srhr_version"]
)


# Ask user for their OpenAI API key via `st.text_input`.
# Alternatively, you can store the API key in `./.streamlit/secrets.toml` and access it
# via `st.secrets`, see https://docs.streamlit.io/develop/concepts/connections/secrets-management
#openai_api_key = st.text_input("OpenAI API Key", type="password")
openai_api_key = st.secrets["openai_api_key"]
if not openai_api_key:
    st.info("Please add your OpenAI API key to continue.", icon="🗝️")
else:

    # Create an OpenAI client.
    client = OpenAI(api_key=openai_api_key)

    # Create a session state variable to store the chat messages. This ensures that the
    # messages persist across reruns.
    if "messages" not in st.session_state:
        st.session_state.messages = []

    # Display the existing chat messages via `st.chat_message`.
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Create a chat input field to allow the user to enter a message. This will display
    # automatically at the bottom of the page.
    if prompt := st.chat_input("What is up?"):

        # Store and display the current prompt.
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # Generate a response using the OpenAI API.
        stream = client.responses.create(
            #prompt={ "id": "pmpt_688a0932291c81979cdf4f746bd3017906dee59b395d64c8", "version": "5" },
            prompt={ "id": st.secrets["srhr_prompt_id"], "version": st.secrets["srhr_version"] },
            input=[
                {"role": m["role"], "content": m["content"]}
                for m in st.session_state.messages
            ],
            stream=False,
        )
        #print(stream)
        #assistant_response = stream.output[0].content[0].text
        for item in stream.output:
            if item.__class__.__name__ == "ResponseOutputMessage":
                for content in item.content:
                    if content.__class__.__name__ == "ResponseOutputText":
                        assistant_response = content.text

        # Stream the response to the chat using `st.write_stream`, then store it in 
        # session state.
        with st.chat_message("assistant"):
            st.session_state.messages.append({"role": "assistant", "content": assistant_response})
            st.markdown(assistant_response)
        #st.session_state.messages.append({"role": "assistant", "content": response})
