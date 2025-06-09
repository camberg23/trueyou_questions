import streamlit as st
import pandas as pd
from langchain_community.chat_models import ChatOpenAI
from langchain_community.llms import OpenAI 
from langchain.prompts import PromptTemplate 
from langchain.chains import LLMChain
import io
import base64
from system_messages import *

# Initialize the chat model with appropriate parameters
chat_model = ChatOpenAI(openai_api_key=st.secrets['API_KEY'], model_name='gpt-4.1', temperature=0.2, max_tokens=4096)

st.set_page_config(page_title='TrueYou Question Generator', page_icon=None, layout="wide")

# Initialize the DataFrame in session state if it doesn't exist
if 'df' not in st.session_state:
    file_path = 'Updated App Test 6_5_25 - Items.csv'
    df_initial = pd.read_csv(file_path)
    st.session_state['df'] = df_initial

if 'proposed_changes' not in st.session_state:
    st.session_state['proposed_changes'] = pd.DataFrame()

if 'proposed_questions' not in st.session_state:
    st.session_state['proposed_questions'] = pd.DataFrame()

# Streamlit UI setup
st.title("TrueYou Question/Scale Generator")

# Expander for the current scale questions table
with st.expander("Click here to see all current scales and questions"):
    st.dataframe(st.session_state['df'])

# Category dictionary - map scale key prefixes to category names
cat_dict = {'O': 'Openness', 'C': 'Conscientiousness', 'E': 'Extraversion', 'A': 'Agreeableness', 'R': 'Resilience (Inverse Neuroticism)'}

# New functionality for generating new scales
st.markdown("## Generate New Scales")
st.markdown("Here you can generate entirely new scales from scratch. Select the category and provide any specific details you'd like for the new scale.")

# Use the category dictionary for the dropdown
selected_cat_key = st.selectbox("Select the Big Five trait for the new scale:", options=list(cat_dict.keys()), format_func=lambda x: cat_dict[x])
selected_cat = cat_dict[selected_cat_key]  # Get the full category name for display and processing
scale_details = st.text_area("Provide any specific details for the new scale (optional):", "")

submit_button = st.button("Generate New Scale", key="generate_new_scale")

if submit_button:
    # Retrieve full current content for all items in the selected category (using scale key prefix)
    cat_content_df = st.session_state['df'][st.session_state['df']['Scale Key'].str.startswith(selected_cat_key)]
    
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

st.write("---")
st.markdown("## Generate New Questions")
st.markdown("Here, you can generate new questions for existing scales.")

# Layout with two columns for generating new questions within a scale
col1, col2 = st.columns([3, 1])

# Column for scale selection
with col1:
    # Load scales info to create better display names
    scales_df = pd.read_csv('Updated App Test 6_5_25 - Scales.csv')
    
    # Create scale options using both Scale Key and Title for better display
    scale_options = []
    for _, scale_row in scales_df.iterrows():
        trait_key = scale_row['Scale']
        title = scale_row['Title']
        # Find corresponding Scale Key from items
        items_with_trait = st.session_state['df'][st.session_state['df']['Trait Key'] == trait_key]
        if not items_with_trait.empty:
            scale_key = items_with_trait.iloc[0]['Scale Key']
            # Extract category from scale key (first letter)
            cat_key = scale_key[0] if scale_key else 'Unknown'
            scale_options.append(f"{title} ({scale_key})")
    
    # Sort scale options by scale key
    def sort_key(option):
        scale_key = option.split(" (")[-1].rstrip(")")
        letter = ''.join(filter(str.isalpha, scale_key))
        number = ''.join(filter(str.isdigit, scale_key))
        return (letter, int(number) if number else 0)
    
    scale_options.sort(key=sort_key)
    selected_scales = st.multiselect("Select which scales you'd like to generate new questions for:", scale_options)

# Column for specifying the number of new questions
with col2:
    N = st.number_input("Number of new questions for each scale:", min_value=1, max_value=25, value=5)

# Button to generate new questions
if st.button("Generate New Questions"):
    all_new_items = []  # To hold all new items for all selected scales
    for scale_option in selected_scales:
        # Extract scale key from display format "Title (Scale Key)"
        scale_key = scale_option.split(' (')[-1].rstrip(')')
        
        # Get trait key for this scale key
        trait_key_row = st.session_state['df'][st.session_state['df']['Scale Key'] == scale_key]
        if not trait_key_row.empty:
            trait_key = trait_key_row.iloc[0]['Trait Key']
            scale_df = st.session_state['df'][st.session_state['df']['Trait Key'] == trait_key].copy()

            # Your existing LLM logic for generating new questions
            chat_chain = LLMChain(prompt=PromptTemplate.from_template(new_questions_prompt), llm=chat_model)
            generated_output = chat_chain.run(N=N, scale=trait_key, existing_items=scale_df.to_string(index=False))

            # Process the generated questions
            new_items = []
            for question in generated_output.split('\n'):
                values = question.split('|')
                if len(values) == len(st.session_state['df'].columns):
                    new_row = {col: val.strip().strip("'") for col, val in zip(st.session_state['df'].columns, values)}
                    new_items.append(new_row)
            if new_items:
                # Store new items temporarily, keyed by scale name
                all_new_items.extend(new_items)  # Extend the list with new items for this scale

    if all_new_items:
        # Update session state with proposed questions for all selected scales
        st.session_state['proposed_questions'] = pd.DataFrame(all_new_items)
        
        # Display proposed changes to the user
        st.markdown("### Proposed New Questions")
        st.dataframe(st.session_state['proposed_questions'])

# Display buttons for confirmation only if there are proposed questions
if not st.session_state['proposed_questions'].empty:
    confirm_button = st.button("Confirm and Integrate Questions", key="confirm_new_questions")
    discard_button = st.button("Discard Questions", key="discard_new_questions")

    if confirm_button:
        # Integrate proposed questions with the main DataFrame
        updated_df = pd.concat([st.session_state['df'], st.session_state['proposed_questions']], ignore_index=True)
        st.session_state['df'] = updated_df
        # Clear proposed questions after integration
        st.session_state['proposed_questions'] = pd.DataFrame()
        st.success("New questions have been integrated successfully!")
        st.rerun()

    elif discard_button:
        # Clear proposed questions without integrating
        st.session_state['proposed_questions'] = pd.DataFrame()
        st.info("Proposed questions have been discarded.")

st.markdown("")
st.markdown("")
    
if not st.session_state['df'].empty:
    csv = st.session_state['df'].to_csv(index=False).encode('utf-8')
    st.download_button(
        label="Download updated questions as a CSV",
        data=csv,
        file_name='updated_questions.csv',
        mime='text/csv')

# import streamlit as st
# import pandas as pd
# from langchain_community.chat_models import ChatOpenAI
# from langchain_community.llms import OpenAI 
# from langchain.prompts import PromptTemplate 
# from langchain.chains import LLMChain
# import io
# import base64
# from system_messages import *

# # Initialize the chat model with appropriate parameters
# chat_model = ChatOpenAI(openai_api_key=st.secrets['API_KEY'], model_name='gpt-4-1106-preview', temperature=0.2, max_tokens=4096)

# st.set_page_config(page_title='TrueYou Question Generator', page_icon=None, layout="wide")

# # Initialize the DataFrame in session state if it doesn't exist
# if 'df' not in st.session_state:
#     file_path = 'questions.csv'
#     df_initial = pd.read_csv(file_path)
#     st.session_state['df'] = df_initial

# if 'proposed_changes' not in st.session_state:
#     st.session_state['proposed_changes'] = pd.DataFrame()

# if 'proposed_questions' not in st.session_state:
#     st.session_state['proposed_questions'] = pd.DataFrame()

# # Streamlit UI setup
# st.title("TrueYou Question/Scale Generator")

# # Expander for the current scale questions table
# with st.expander("Click here to see all current scales and questions"):
#     st.dataframe(st.session_state['df'])

# # Category dictionary
# cat_dict = {'O': 'Openness', 'C': 'Conscientiousness', 'E': 'Extraversion', 'A': 'Agreeableness', 'R': 'Resilience (Inverse Neuroticism)'}

# # New functionality for generating new scales
# st.markdown("## Generate New Scales")
# st.markdown("Here you can generate entirely new scales from scratch. Select the category and provide any specific details you'd like for the new scale.")

# # Use the category dictionary for the dropdown
# selected_cat_key = st.selectbox("Select the Big Five trait for the new scale:", options=list(cat_dict.keys()), format_func=lambda x: cat_dict[x])
# selected_cat = cat_dict[selected_cat_key]  # Get the full category name for display and processing
# scale_details = st.text_area("Provide any specific details for the new scale (optional):", "")

# submit_button = st.button("Generate New Scale", key="generate_new_scale")

# if submit_button:
#     # Retrieve full current content for all items in the selected category (using the original category key)
#     cat_content_df = st.session_state['df'][st.session_state['df']['Cat'] == selected_cat_key]
    
#     # Placeholder for LLM chain
#     chat_chain = LLMChain(prompt=PromptTemplate.from_template(new_scales_prompt), llm=chat_model)
#     generated_output = chat_chain.run(TRAIT=selected_cat, SCALE_DETAILS=scale_details, EXISTING_ITEMS=cat_content_df.to_string(index=False))
    
#     # Process the generated scales or questions
#     new_items = []
#     for scale_info in generated_output.split('\n'):
#         values = scale_info.split('|')
#         if len(values) == len(st.session_state['df'].columns):
#             new_row = {col: val.strip().strip("'") for col, val in zip(st.session_state['df'].columns, values)}
#             new_items.append(new_row)

#     if new_items:
#         # Store proposed changes in the session state
#         st.session_state['proposed_changes'] = pd.DataFrame(new_items)
#         st.markdown("### Proposed Changes")
#         st.dataframe(st.session_state['proposed_changes'])

# # Display buttons for confirmation only if there are proposed changes
# if not st.session_state['proposed_changes'].empty:
#     confirm_button = st.button("Confirm and Integrate Changes", key="confirm_new_scale")
#     discard_button = st.button("Discard Changes", key="discard_new_scale")

#     if confirm_button:
#         # Integrate proposed changes with the main DataFrame
#         updated_df = pd.concat([st.session_state['df'], st.session_state['proposed_changes']], ignore_index=True)
#         st.session_state['df'] = updated_df
#         st.session_state['proposed_changes'] = pd.DataFrame()  # Clear proposed changes
#         st.success("Changes have been integrated successfully!")
#         st.rerun()

#     elif discard_button:
#         # Clear proposed changes without integrating
#         st.session_state['proposed_changes'] = pd.DataFrame()
#         st.info("Changes have been discarded.")

# st.write("---")
# st.markdown("## Generate New Questions")
# st.markdown("Here, you can generate new questions for existing scales.")

# # Layout with two columns for generating new questions within a scale
# col1, col2 = st.columns([3, 1])

# # Column for scale selection
# with col1:
#     # Sort the DataFrame by 'Cat' and then 'Scale Name', and generate scale options
#     sorted_df = st.session_state['df'].sort_values(by=['Cat', 'Scale Name'])
#     scale_options = [f"{row['Scale Name']} ({row['Cat']})" for _, row in sorted_df.drop_duplicates(['Scale Name', 'Cat']).iterrows()]
#     selected_scales = st.multiselect("Select which scales you'd like to generate new questions for:", scale_options)

# # Column for specifying the number of new questions
# with col2:
#     N = st.number_input("Number of new questions for each scale:", min_value=1, max_value=25, value=5)

# # Button to generate new questions
# if st.button("Generate New Questions"):
#     all_new_items = []  # To hold all new items for all selected scales
#     for scale_option in selected_scales:
#         scale, cat = scale_option.split(' (')
#         cat = cat.rstrip(')')
#         scale_df = st.session_state['df'][st.session_state['df']['Scale Name'] == scale].copy()

#         # Your existing LLM logic for generating new questions
#         chat_chain = LLMChain(prompt=PromptTemplate.from_template(new_questions_prompt), llm=chat_model)
#         generated_output = chat_chain.run(N=N, scale=scale, existing_items=scale_df.to_string(index=False))

#         # Process the generated questions
#         new_items = []
#         for question in generated_output.split('\n'):
#             values = question.split('|')
#             if len(values) == len(st.session_state['df'].columns):
#                 new_row = {col: val.strip().strip("'") for col, val in zip(st.session_state['df'].columns, values)}
#                 new_items.append(new_row)
#         if new_items:
#             # Store new items temporarily, keyed by scale name
#             all_new_items.extend(new_items)  # Extend the list with new items for this scale

#     if all_new_items:
#         # Update session state with proposed questions for all selected scales
#         st.session_state['proposed_questions'] = pd.DataFrame(all_new_items)
        
#         # Display proposed changes to the user
#         st.markdown("### Proposed New Questions")
#         st.dataframe(st.session_state['proposed_questions'])

# # Display buttons for confirmation only if there are proposed questions
# if not st.session_state['proposed_questions'].empty:
#     confirm_button = st.button("Confirm and Integrate Questions", key="confirm_new_questions")
#     discard_button = st.button("Discard Questions", key="discard_new_questions")

#     if confirm_button:
#         # Integrate proposed questions with the main DataFrame
#         updated_df = pd.concat([st.session_state['df'], st.session_state['proposed_questions']], ignore_index=True)
#         st.session_state['df'] = updated_df
#         # Clear proposed questions after integration
#         st.session_state['proposed_questions'] = pd.DataFrame()
#         st.success("New questions have been integrated successfully!")
#         st.rerun()

#     elif discard_button:
#         # Clear proposed questions without integrating
#         st.session_state['proposed_questions'] = pd.DataFrame()
#         st.info("Proposed questions have been discarded.")

# st.markdown("")
# st.markdown("")
    
# if not st.session_state['df'].empty:
#     csv = st.session_state['df'].to_csv(index=False).encode('utf-8')
#     st.download_button(
#         label="Download updated questions as a CSV",
#         data=csv,
#         file_name='updated_questions.csv',
#         mime='text/csv')
