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

st.set_page_config(page_title='TrueYou Question Generator', page_icon=None, layout="wide")

# Streamlit UI setup
st.title("TrueYou Question Generator")

# Expander for the current scale questions table
with st.expander("Click here to see all current scales and questions"):
    st.dataframe(df)

# New functionality for generating new scales
st.markdown("## Generate New Scales")
st.markdown("Here you can generate entirely new scales from scratch. Select the category and provide any specific details you'd like for the new scale.")

# Getting unique categories from the dataframe
unique_cats = df['Cat'].unique().tolist()

# Form for new scale generation
with st.form("new_scale_form"):
    selected_cat = st.selectbox("Select the category for the new scale:", unique_cats)
    scale_details = st.text_area("Provide any specific details for the new scale (optional):", "")
    
    submit_button = st.form_submit_button("Prepare New Scale Information")
    
    if submit_button:
        # Retrieve full current content for all items in the selected category
        cat_content_df = df[df['Cat'] == selected_cat]
        
        # Displaying the user's inputs and the content of the selected category
        st.write(f"Selected Category: {selected_cat}")
        st.write("Specific Details for the New Scale (if provided):")
        st.write(scale_details)
        st.write("Current Content for All Items in Selected Category:")
        st.write(cat_content_df.to_string(index=False))

# Layout with two columns (existing functionality for generating new questions within a scale)
col1, col2 = st.columns([3, 1])

# Column for scale selection
with col1:
    scale_options = [f"{row['Scale Name']} ({row['Cat']})" for _, row in df.drop_duplicates(['Scale Name', 'Cat']).iterrows()]
    selected_scales = st.multiselect("Select which scales you'd like to generate new questions for:", scale_options)

# Column for specifying the number of new questions
with col2:
    N = st.number_input("Number of new questions for each scale:", min_value=1, max_value=25, value=5)

# Button to generate new questions
if st.button("Generate New Questions"):
    for scale_option in selected_scales:
        scale, cat = scale_option.split(' (')
        scale_df = df[df['Scale Name'] == scale].copy()

        chat_chain = LLMChain(prompt=PromptTemplate.from_template(new_questions_prompt), llm=chat_model)
        generated_output = chat_chain.run(N=N, scale=scale, existing_items=scale_df.to_string(index=False))

        # Process the generated questions
        new_items = []
        for question in generated_output.split('\n'):
            values = question.split('|')
            if len(values) == len(df.columns):
                new_row = {col: val.strip().strip("'") for col, val in zip(df.columns, values)}
                new_items.append(new_row)

        if new_items:
            new_items_df = pd.DataFrame(new_items)
            combined_df = pd.concat([scale_df, new_items_df], ignore_index=True)
            
            # Enhanced display of updated scale questions with category
            st.markdown(f"### Updated Scale Questions for {scale} ({cat.strip(')')})")
            
            # Apply styling to only new rows
            styled_df = combined_df.style.apply(
                lambda x: ['background-color: lightgreen' if x.name >= num_existing_rows else '' for _ in x], axis=1)
            st.dataframe(styled_df)
