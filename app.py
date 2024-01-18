import streamlit as st
import pandas as pd
import requests
# from openai import OpenAI
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI 
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain
import io
from system_messages import *

chat_model = ChatOpenAI(openai_api_key=st.secrets['API_KEY'], model_name='gpt-4-1106-preview', temperature=0.2, max_tokens=4096)

# Load the CSV file
file_path = 'questions.csv'
df = pd.read_csv(file_path)

# Streamlit UI setup
st.title("Scale Question Generator")

# Display the existing table
st.write("Current Scale Questions:")
st.dataframe(df)

# Scale selection for generating new questions
scale_options = df['Scale Name'].unique()
selected_scales = st.multiselect("Select scales to generate questions for:", scale_options)

# Button to generate new questions
if st.button("Generate New Questions"):
    new_questions = []
    for scale in selected_scales:
        # Assuming you have a predefined prompt template for question generation
        prompt = f"Generate a new question for the scale: {scale}"
        chat_chain = LLMChain(prompt=PromptTemplate.from_template(prompt), llm=chat_model)
        generated_question = chat_chain.run(scale=scale)  # You might need to adjust the parameters based on your LLM setup

        # Add the new question to the dataframe
        new_row = {
            'Cat': '',  # Set appropriate values
            'Scale Name': scale,
            'Scale #': '',  # Set appropriate values
            'Scale Key': '',  # Set appropriate values
            'Item Text': generated_question,
            'Session': '',  # Set appropriate values
            'Trait Key': '',  # Set appropriate values
            'Reverse': False  # Set appropriate values
        }
        df = df.append(new_row, ignore_index=True)
        new_questions.append(generated_question)

    # Display new questions
    st.write("Newly Generated Questions:")
    for question in new_questions:
        st.markdown(f"* {question}")  # Highlighting new questions

    # Display the updated table
    st.write("Updated Scale Questions:")
    st.dataframe(df)

# Additional code for saving, downloading, etc., as required
