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

# Button to generate new questions
if st.button("Generate New Questions"):
    for scale in selected_scales:
        # Filter dataframe for the selected scale
        scale_df = df[df['Scale Name'] == scale]

        # Create a sophisticated prompt for the LLM
        prompt = f"Create five new questions for the scale: {scale}. Existing items:\n{scale_df.to_string(index=False)} ENSURE YOUR OUTPUTS ARE IN THIS EXACT FORMAT!"
        chat_chain = LLMChain(prompt=PromptTemplate.from_template(prompt), llm=chat_model)
        generated_questions = chat_chain.run(scale=scale)  # Adjust parameters based on your LLM setup
        st.write(generated_questions)
        # Process the generated questions
        new_items = []
        for question in generated_questions.split('\n'):
            # Assuming the output format matches the input format
            values = question.split(',')
            if len(values) == len(df.columns):
                new_row = {col: val for col, val in zip(df.columns, values)}
                new_row['Session'] = ''  # Leave 'Session' column blank
                scale_df = scale_df.append(new_row, ignore_index=True)
                new_items.append(new_row)

        # Display the updated table for the scale
        st.write(f"Updated Scale Questions for {scale}:")
        st.dataframe(scale_df.style.apply(lambda x: ['background: lightblue' if x.name in range(len(scale_df)-len(new_items), len(scale_df)) else '' for i in x], axis=1))

# Additional code for saving, downloading, etc., as required
