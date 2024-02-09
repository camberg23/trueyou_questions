new_questions_prompt = """
Your job is to help create {N} new questions for the psychometric scale: {scale}. 
The questions should be varied, accurate, and straightforward in content, using the original questions as inspiration in terms of style, tone, and length. 
Occasionally include reverse scored items.

Existing items to use as inspiration: {existing_items}

Format each new question as follows, with each field separated by a '|' and each question on a new line:

'Category'|'Scale Name'|'Scale #'|'Scale Key'|'Item Text'|'Session'|'Trait Key'|'Reverse'

Example:
'A'|'Accommodating'|1|'A1'|'new question text 1'| |'accommodating'|False
'A'|'Accommodating'|1|'A1'|'new question text 2'| |'accommodating'|False
'A'|'Accommodating'|1|'A1'|'new question text 3'| |'accommodating'|True

Please provide {N} new questions in this EXACT format (for now, please just leave the 'Session' column blank as shown above!).
"""

new_scales_prompt = """
Your job is to help create ONE SINGLE new scale that is meaningfully different and additive amongst numerous existing scales as a subset of the Big Five trait, {TRAIT}. 

The user may or may not have specified a specific requirement related to the creation of this SINGLE new scale. If so, it will appear here: 

{SCALE_DETAILS}

The questions should be varied, accurate, and straightforward in content, using the original questions as inspiration in terms of style, tone, and length. 
Occasionally include reverse scored items.

Here are all the existing items that currently exist under {TRAIT} to use as inspiration both in terms of content and formatting: 
{EXISTING_ITEMS}

Format each new question as follows, with each field separated by a '|' and each question on a new line:

'Category'|'Scale Name'|'Scale #'|'Scale Key'|'Item Text'|'Session'|'Trait Key'|'Reverse'

Example:
'A'|'Accommodating'|1|'A1'|'new question text 1'| |'accommodating'|False
'A'|'Accommodating'|1|'A1'|'new question text 2'| |'accommodating'|False
'A'|'Accommodating'|1|'A1'|'new question text 3'| |'accommodating'|True

Please provide 6 new questions in this EXACT format for the SINGLE new scale (please just leave the 'Session' column blank as shown above, and PLEASE increment the scale number by one, as these questions will be added on as a new scale).
"""
