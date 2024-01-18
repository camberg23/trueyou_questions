import streamlit as st
import pandas as pd
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI 
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain
import io
from system_messages import *

# Initialize the chat model with appropriate parameters
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
N = 5
# Button to generate new questions
if st.button("Generate New Questions"):
    for scale in selected_scales:
        # Filter dataframe for the selected scale
        scale_df = df[df['Scale Name'] == scale]
        chat_chain = LLMChain(prompt=PromptTemplate.from_template(new_questions_prompt), llm=chat_model)
        generated_output = chat_chain.run(N=N, scale=scale, existing_items=scale_df.to_string(index=False)) # Adjust parameters based on your LLM setup

        st.write(generated_output)  # To inspect the output format

        # Process the generated questions
        new_items = []
        for question in generated_output.split(' A|'):  # Split by the delimiter
            if question.strip():  # Check if the line is not empty
                values = ['A'] + question.split('|')  # Add 'A' back to each item and split
                if len(values) == len(df.columns):
                    new_row = {col: val.strip() for col, val in zip(df.columns, values)}
                    new_row['Session'] = ''  # Leave 'Session' column blank
                    new_items.append(new_row)

        # Append new items to the scale DataFrame and apply styling
        if new_items:
            new_items_df = pd.DataFrame(new_items)
            scale_df = pd.concat([scale_df, new_items_df], ignore_index=True)
            st.write(f"Updated Scale Questions for {scale}:")
            st.dataframe(scale_df.style.apply(lambda x: ['background: lightblue' if x.name >= len(scale_df) - len(new_items) else '' for _ in x], axis=1))
