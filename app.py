import streamlit as st
import tiktoken
import requests
from openai import OpenAI
from langchain.chat_models import ChatOpenAI
from langchain.llms import OpenAI 
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain
from system_messages import *

chat_model = ChatOpenAI(openai_api_key=st.secrets['API_KEY'], model_name='gpt-4-1106-preview', temperature=0.2, max_tokens=4096)

# Streamlit UI
st.title("TypeFinder Blog Post Generator")

# Title input
st.write("**This tool will generate blogs for all 16 TypeFinder types given a fixed topic.** When you write your title, **use the placeholder 'Xs'** for where the types (eg, INTPs, ENFJs) will go.")
st.write("*Examples: The Best Paying Careers for Xs, Best Jobs for Xs That Don't Require a College Degree, etc.*")
title = st.text_input("Blog Title:")

# Button to generate topics based on the title
if st.button("Generate Skeleton for This Blog"):
    with st.spinner("Generating blog skeleton, please standby..."):
        # Generate topics using GPT
        chat_chain = LLMChain(prompt=PromptTemplate.from_template(topic_system_message), llm=chat_model)
        topics = chat_chain.run(TITLE=title)

    # Initialize session state for headers
    st.session_state['generated_headers'] = topics

# Editable text area for headers
st.write("Next, edit the generated skeleton as needed, or regenerate the skeleton entirely if you don't like this structure.")
st.write("(Note: please don't replace or modify the markdown (###, **, etc) or '{TYPE}s' notation)")
edited_headers = st.text_area("**Generated skeleton:**", value=st.session_state.get('generated_headers', ''), height=400)

typefinders = ["ISTJ", "ISFJ", "INFJ", "INTJ", "ISTP", "ISFP", "INFP", "INTP", "ESTP", "ESFP", "ENFP", "ENTP", "ESTJ", "ESFJ", "ENFJ", "ENTJ"]
typefinders = ["ISTJ", "ISFJ"]

# When the user is ready to generate the blog post
if st.button("**Generate blog posts for all TypeFinder types with the skeleton as it appears above**"):
    blogs = {}
    my_bar = st.progress(0)
    for i, typefinder in enumerate(typefinders):
        # Update progress bar
        my_bar.progress(i / len(typefinders))
        
        # Generate the blog post
        chat_chain = LLMChain(prompt=PromptTemplate.from_template(system_message), llm=chat_model)
        blog = chat_chain.run(TITLE=title, HEADERS=edited_headers, TYPE=typefinder, LOWER_TYPE=typefinder.lower())
        
        # Store the blog post
        blogs[typefinder] = blog

    # Display the generated blog posts in expanders
    for typefinder, blog in blogs.items():
        with st.expander(f"{title.replace('Xs', f'{typefinder}s')}"):
            st.markdown(blog, unsafe_allow_html=True)

    # Reset progress bar
    my_bar.empty()
