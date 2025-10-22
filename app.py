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
    file_path = 'All App Test Items as of Oct 25 - Sheet1.csv'
    df_initial = pd.read_csv(file_path)
    st.session_state['df'] = df_initial

if 'proposed_changes' not in st.session_state:
    st.session_state['proposed_changes'] = pd.DataFrame()

if 'proposed_questions' not in st.session_state:
    st.session_state['proposed_questions'] = pd.DataFrame()

if 'changes_confirmed' not in st.session_state:
    st.session_state['changes_confirmed'] = False

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
    
    st.write(f"LLM OUTPUT: {generated_output}")
    
    # Process the generated questions
    new_items = []
    for question in generated_output.split('\n'):
        values = question.split('|')
        
        if len(values) == len(st.session_state['df'].columns):
            new_row = {col: val.strip().strip("'") for col, val in zip(st.session_state['df'].columns, values)}
            new_items.append(new_row)

    if new_items:
        # Store proposed changes in the session state
        st.session_state['proposed_changes'] = pd.DataFrame(new_items)

# Display proposed changes OUTSIDE the button conditional (so it persists across reruns)
if not st.session_state['proposed_changes'].empty:
    st.markdown("### Proposed Changes")
    st.session_state['proposed_changes'] = st.data_editor(
        st.session_state['proposed_changes'],
        num_rows="dynamic",
        use_container_width=True,
        key="edit_proposed_changes"
    )
    
    col_confirm, col_discard = st.columns(2)
    with col_confirm:
        confirm_button = st.button("Confirm and Integrate Changes", key="confirm_new_scale", use_container_width=True)
    with col_discard:
        discard_button = st.button("Discard Changes", key="discard_new_scale", use_container_width=True)

    if confirm_button:
        # Integrate proposed changes with the main DataFrame
        updated_df = pd.concat([st.session_state['df'], st.session_state['proposed_changes']], ignore_index=True)
        st.session_state['df'] = updated_df
        st.session_state['proposed_changes'] = pd.DataFrame()  # Clear proposed changes
        st.session_state['changes_confirmed'] = True
        st.success("Changes have been integrated successfully!")

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
        else:
            st.write(f"❌ No trait key found for scale key: {scale_key}")
    
    if all_new_items:
        # Update session state with proposed questions for all selected scales
        st.session_state['proposed_questions'] = pd.DataFrame(all_new_items)

# Display proposed questions OUTSIDE the button conditional (so it persists across reruns)
if not st.session_state['proposed_questions'].empty:
    st.markdown("### Proposed New Questions")
    st.session_state['proposed_questions'] = st.data_editor(
        st.session_state['proposed_questions'],
        num_rows="dynamic",  # Allows deleting rows
        use_container_width=True,
        key="edit_proposed_questions"
    )
    
    col_confirm, col_discard = st.columns(2)
    with col_confirm:
        confirm_button = st.button("Confirm and Integrate Questions", key="confirm_new_questions", use_container_width=True)
    with col_discard:
        discard_button = st.button("Discard Questions", key="discard_new_questions", use_container_width=True)

    if confirm_button:
        # Integrate proposed questions with the main DataFrame
        updated_df = pd.concat([st.session_state['df'], st.session_state['proposed_questions']], ignore_index=True)
        st.session_state['df'] = updated_df
        # Clear proposed questions after integration
        st.session_state['proposed_questions'] = pd.DataFrame()
        st.session_state['changes_confirmed'] = True
        st.success("New questions have been integrated successfully!")

    elif discard_button:
        # Clear proposed questions without integrating
        st.session_state['proposed_questions'] = pd.DataFrame()
        st.info("Proposed questions have been discarded.")

st.markdown("---")
    
# Only show download button if changes were confirmed or there are no pending changes
if st.session_state['changes_confirmed'] or (st.session_state['proposed_changes'].empty and st.session_state['proposed_questions'].empty):
    if not st.session_state['df'].empty:
        csv = st.session_state['df'].to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download updated questions as a CSV",
            data=csv,
            file_name='updated_questions.csv',
            mime='text/csv')
        # Reset the flag after showing download button
        if st.session_state['changes_confirmed']:
            st.session_state['changes_confirmed'] = False
else:
    st.info("⚠️ Please confirm or discard your pending changes before downloading.")
