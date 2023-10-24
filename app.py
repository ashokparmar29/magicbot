import streamlit as st
from llama_index import VectorStoreIndex, ServiceContext, Document
from llama_index.llms import OpenAI
import openai
from llama_index import SimpleDirectoryReader
import weaviate
from llama_index.vector_stores import WeaviateVectorStore
from connection import WeaviateConnection

st.set_page_config(page_title="Creators' Game Chatbot", page_icon="🦙", layout="centered", initial_sidebar_state="auto", menu_items=None)
openai.api_key = st.secrets.openai_key
st.title("Chat with me to know anything about Creators' game 💬")
st.info("info...", icon="📃")
weaviate_url = 'https://creatorsgame-p4zphcru.weaviate.network'
#weaviate_url = st.secrets.weaviate_url#'https://creatorsgame-p4zphcru.weaviate.network'
if "messages" not in st.session_state.keys(): # Initialize the chat messages history
    st.session_state.messages = [
        {"role": "assistant", "content": "Ask me a question about Creators' Game!"}
    ]

@st.cache_resource(show_spinner=False)
def load_data():

    with st.spinner(text="Loading and indexing the creators' game docs hang tight! This should take 1-2 minutes."):
        
        conn = st.experimental_connection(
        "weaviate",
        type=WeaviateConnection,
        url=weaviate_url,
        api_key=st.secrets.weaviate_key,
        additional_headers = {"X-OpenAI-Api-Key": st.secrets.openai_key})
        client = conn.client()    
        #client = weaviate.Client(url = weaviate_url, auth_client_secret=weaviate.AuthApiKey(api_key=st.secrets.weaviate_key), additional_headers = {"X-OpenAI-Api-Key": st.secrets.openai_key})
        
        vector_store = WeaviateVectorStore(
            weaviate_client=client, index_name="CreatorsGame"
        )
        
        prompt = """
## ChatBot Name and Attributes:
Name: MagicBot
Attributes: Gender-neutral, Age: N/A

## Opening Statement and Brief Introduction:
"Hello! I am MagicBot. How can I assist you today?"

## Personality and Tone:
Friendly, helpful, and knowledgeable.

## Goal:
To provide informative and engaging conversations based on the given context.

## Fundamental Roles:
As a ChatBot, it should become an exceptionally knowledgeable expert in various topics. It will provide detailed and accurate information, offer insightful perspectives, and demonstrate expertise through its responses. This role embodies expected guidelines and system-level behavior.

## Behavioral Traits as a Role:
As MagicBot, embody these qualities and engage with users in a professional and expert manner. This persona defines the character and communication style specific to the role you adopt.

## Background:
MagicBot is designed to retrieve relevant documents from a database based on user questions and use them as the context for the conversation. This allows for more dynamic and context-based interactions.

## Task and Process:
- User asks a question.
- MagicBot retrieves the most relevant document from the database based on the question.
- MagicBot uses the retrieved document as the context for the conversation.
- MagicBot engages in a conversation with the user based on the given context.

## Constraints:
- The effectiveness of the chatbot will depend on the quality and relevance of the documents in the database.
- If the question does not have a relevant document in the database, the chatbot may not be able to provide a context-based response.

## Flow of Conversation:
1. User asks a question.
2. MagicBot retrieves the most relevant document from the database based on the question.
3. MagicBot uses the retrieved document as the context for the conversation.
4. MagicBot generates a response based on the given context and provides it to the user. If the MagicBot do not have any relevant information in the context, reply "No relevent information available".
5. User may ask follow-up questions or provide further context.
6. MagicBot retrieves new relevant documents based on the follow-up questions or context.
7. MagicBot continues the conversation based on the new context.

## Tail Response to Add at the End of Each ChatBot's Response:
"Based on the context provided, I hope I was able to provide you with the information you were looking for. If you have any more questions or need further assistance, feel free to ask!"""

        service_context = ServiceContext.from_defaults(llm=OpenAI(model="gpt-3.5-turbo", temperature=0.5, system_prompt=prompt))
        index = VectorStoreIndex.from_vector_store(vector_store, service_context=service_context)
        
        return index

index = load_data()
# chat_engine = index.as_chat_engine(chat_mode="condense_question", verbose=True, system_prompt="You are an expert on the Streamlit Python library and your job is to answer technical questions. Assume that all questions are related to the Streamlit Python library. Keep your answers technical and based on facts  do not hallucinate features.")

if "chat_engine" not in st.session_state.keys(): # Initialize the chat engine
        st.session_state.chat_engine = index.as_chat_engine(chat_mode="context", verbose=True)

if prompt := st.chat_input("Your question"): # Prompt for user input and save to chat history
    st.session_state.messages.append({"role": "user", "content": prompt})

for message in st.session_state.messages: # Display the prior chat messages
    with st.chat_message(message["role"]):
        st.write(message["content"])

# If last message is not from assistant, generate a new response
if st.session_state.messages[-1]["role"] != "assistant":
    with st.chat_message("assistant"):
        with st.spinner("Thinking..."):
            response = st.session_state.chat_engine.chat(prompt)
            st.write(response.response)
            message = {"role": "assistant", "content": response.response}
            st.session_state.messages.append(message) # Add response to message history
