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
st.markdown("Here you can generate entirely new scales from scratch. Fill in the parameters below to define the characteristics of the scales you want to generate.")

# Parameters for new scale generation
# For simplicity, these are just placeholders. You'll need to adjust them based on the specifics of your application.
with st.form("new_scale_form"):
    scale_name_hint = st.text_input("Enter a hint for the scale name (optional):", "")
    scale_category = st.selectbox("Select the category for the new scale:", ["Category 1", "Category 2", "Category 3"])
    scale_description = st.text_area("Enter a description for the new scale (optional):", "")
    number_of_scales = st.number_input("Number of new scales to generate:", min_value=1, max_value=10, value=1)
    
    # Submit button for the form
    submit_button = st.form_submit_button("Generate New Scales")
    
    if submit_button:
        # Placeholder for scale generation logic
        st.write("Generating new scales...")
        # Here you will implement the logic to use the inputs above to generate new scales.
        # This could involve calling an LLM or another process.

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
