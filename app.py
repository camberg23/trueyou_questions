# import streamlit as st
# import pandas as pd
# from langchain_community.chat_models import ChatOpenAI
# from langchain_community.llms import OpenAI 
# from langchain.prompts import PromptTemplate 
# from langchain.chains import LLMChain
# import io
# from system_messages import *

# # Initialize the chat model with appropriate parameters
# chat_model = ChatOpenAI(openai_api_key=st.secrets['API_KEY'], model_name='gpt-4-1106-preview', temperature=0.2, max_tokens=4096)

# # Load the CSV file
# file_path = 'questions.csv'
# df = pd.read_csv(file_path)

# st.set_page_config(page_title='TrueYou Question Generator', page_icon=None, layout="wide")

# # Streamlit UI setup
# st.title("TrueYou Question Generator")

# # Expander for the current scale questions table
# with st.expander("Click here to see all current scales and questions"):
#     st.dataframe(df)

# # Category dictionary
# cat_dict = {'O': 'Openness', 'C': 'Conscientiousness', 'E': 'Extraversion', 'A': 'Agreeableness', 'R': 'Resilience (Inverse Neuroticism)'}

# # New functionality for generating new scales
# st.markdown("## Generate New Scales")
# st.markdown("Here you can generate entirely new scales from scratch. Select the category and provide any specific details you'd like for the new scale.")

# with st.form("new_scale_form"):
#     # Use the category dictionary for the dropdown
#     selected_cat_key = st.selectbox("Select the category for the new scale:", options=list(cat_dict.keys()), format_func=lambda x: cat_dict[x])
#     selected_cat = cat_dict[selected_cat_key]  # Get the full category name for display and processing
#     scale_details = st.text_area("Provide any specific details for the new scale (optional):", "")
    
#     submit_button = st.form_submit_button("Generate New Scale")

#     if submit_button:
#         # Retrieve full current content for all items in the selected category (using the original category key)
#         cat_content_df = df[df['Cat'] == selected_cat_key]
        
#         # Placeholder for LLM chain (assuming prompt templates and llm initialization are correctly set up)
#         # This is where you would actually call the LLM, but for now, we're simulating the output for demonstration.
#         chat_chain = LLMChain(prompt=PromptTemplate.from_template(new_scales_prompt), llm=chat_model)
#         generated_output = chat_chain.run(TRAIT=selected_cat, SCALE_DETAILS=scale_details, EXISTING_ITEMS=cat_content_df.to_string(index=False))
        
#         # st.write(generated_output)  # Uncomment this line to debug and see the raw output
        
#         # Process the generated scales or questions
#         new_items = []
#         for scale_info in generated_output.split('\n'):
#             values = scale_info.split('|')
#             if len(values) == len(df.columns):
#                 new_row = {col: val.strip().strip("'") for col, val in zip(df.columns, values)}
#                 new_items.append(new_row)

#         if new_items:
#             new_items_df = pd.DataFrame(new_items)
            
#             # Create a subset of the original dataframe that includes only items from the selected category
#             cat_subset_df = df[df['Cat'] == selected_cat_key].copy()
            
#             # Combine the new items with this subset
#             combined_df = pd.concat([cat_subset_df, new_items_df], ignore_index=True)
            
#             # Display updated scales/questions for the selected category
#             st.markdown(f"### Newly Generated Scales/Questions for {selected_cat}")
            
#             # Apply styling to only new rows
#             num_existing_rows = len(cat_subset_df)
#             styled_df = combined_df.style.apply(
#                 lambda x: ['background-color: lightgreen' if x.name >= num_existing_rows else '' for _ in x], axis=1)
#             st.dataframe(styled_df)

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

st.set_page_config(page_title='TrueYou Question Generator', page_icon=None, layout="wide")

# Initialize the DataFrame in session state if it doesn't exist
if 'df' not in st.session_state:
    file_path = 'questions.csv'
    df_initial = pd.read_csv(file_path)
    st.session_state['df'] = df_initial

if 'proposed_changes' not in st.session_state:
    st.session_state['proposed_changes'] = pd.DataFrame()

# Streamlit UI setup
st.title("TrueYou Question Generator")

# Expander for the current scale questions table
with st.expander("Click here to see all current scales and questions"):
    st.dataframe(st.session_state['df'])

# Category dictionary
cat_dict = {'O': 'Openness', 'C': 'Conscientiousness', 'E': 'Extraversion', 'A': 'Agreeableness', 'R': 'Resilience (Inverse Neuroticism)'}

# New functionality for generating new scales
st.markdown("## Generate New Scales")
st.markdown("Here you can generate entirely new scales from scratch. Select the category and provide any specific details you'd like for the new scale.")

# Use the category dictionary for the dropdown
selected_cat_key = st.selectbox("Select the category for the new scale:", options=list(cat_dict.keys()), format_func=lambda x: cat_dict[x])
selected_cat = cat_dict[selected_cat_key]  # Get the full category name for display and processing
scale_details = st.text_area("Provide any specific details for the new scale (optional):", "")

submit_button = st.button("Generate New Scale", key="generate_new_scale")

if submit_button:
    # Retrieve full current content for all items in the selected category (using the original category key)
    cat_content_df = st.session_state['df'][st.session_state['df']['Cat'] == selected_cat_key]
    
    # Placeholder for LLM chain
    chat_chain = LLMChain(prompt=PromptTemplate.from_template(new_scales_prompt), llm=chat_model)
    generated_output = chat_chain.run(TRAIT=selected_cat, SCALE_DETAILS=scale_details, EXISTING_ITEMS=cat_content_df.to_string(index=False))
    
    # Process the generated scales or questions
    new_items = []
    for scale_info in generated_output.split('\n'):
        values = scale_info.split('|')
        if len(values) == len(st.session_state['df'].columns):
            new_row = {col: val.strip().strip("'") for col, val in zip(st.session_state['df'].columns, values)}
            new_items.append(new_row)

    if new_items:
        # Store proposed changes in the session state
        st.session_state['proposed_changes'] = pd.DataFrame(new_items)
        st.markdown("### Proposed Changes")
        st.dataframe(st.session_state['proposed_changes'])

# Display buttons for confirmation only if there are proposed changes
if not st.session_state['proposed_changes'].empty:
    confirm_button = st.button("Confirm and Integrate Changes", key="confirm_new_scale")
    discard_button = st.button("Discard Changes", key="discard_new_scale")

    if confirm_button:
        # Integrate proposed changes with the main DataFrame
        updated_df = pd.concat([st.session_state['df'], st.session_state['proposed_changes']], ignore_index=True)
        st.session_state['df'] = updated_df
        st.session_state['proposed_changes'] = pd.DataFrame()  # Clear proposed changes
        st.success("Changes have been integrated successfully!")
        st.rerun()

    elif discard_button:
        # Clear proposed changes without integrating
        st.session_state['proposed_changes'] = pd.DataFrame()
        st.info("Changes have been discarded.")

# # Layout with two columns (existing functionality for generating new questions within a scale)
# col1, col2 = st.columns([3, 1])

# # Column for scale selection
# with col1:
#     scale_options = [f"{row['Scale Name']} ({row['Cat']})" for _, row in df.drop_duplicates(['Scale Name', 'Cat']).iterrows()]
#     selected_scales = st.multiselect("Select which scales you'd like to generate new questions for:", scale_options)

# # Column for specifying the number of new questions
# with col2:
#     N = st.number_input("Number of new questions for each scale:", min_value=1, max_value=25, value=5)

# # Button to generate new questions
# if st.button("Generate New Questions"):
#     for scale_option in selected_scales:
#         scale, cat = scale_option.split(' (')
#         scale_df = df[df['Scale Name'] == scale].copy()

#         chat_chain = LLMChain(prompt=PromptTemplate.from_template(new_questions_prompt), llm=chat_model)
#         generated_output = chat_chain.run(N=N, scale=scale, existing_items=scale_df.to_string(index=False))

#         # Process the generated questions
#         new_items = []
#         for question in generated_output.split('\n'):
#             values = question.split('|')
#             if len(values) == len(df.columns):
#                 new_row = {col: val.strip().strip("'") for col, val in zip(df.columns, values)}
#                 new_items.append(new_row)

#         if new_items:
#             new_items_df = pd.DataFrame(new_items)
#             combined_df = pd.concat([scale_df, new_items_df], ignore_index=True)
            
#             # Enhanced display of updated scale questions with category
#             st.markdown(f"### Updated Scale Questions for {scale} ({cat.strip(')')})")
            
#             # Apply styling to only new rows
#             styled_df = combined_df.style.apply(
#                 lambda x: ['background-color: lightgreen' if x.name >= num_existing_rows else '' for _ in x], axis=1)
#             st.dataframe(styled_df)
