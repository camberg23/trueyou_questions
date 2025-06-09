new_questions_prompt = """
Your job is to help create {N} new questions for the psychometric scale: {scale}. 
The questions should be varied, accurate, and straightforward in content, using the original questions as inspiration in terms of style, tone, and length. 
Occasionally include reverse scored items.

Existing items to use as inspiration: {existing_items}

Format each new question as follows, with each field separated by a '|' and each question on a new line:

'Scale Key'|'Trait Key'|'Item Text'|'Reverse'

Example:
'A3'|'modest'|'I rarely boast about my achievements'|False
'A3'|'modest'|'I often highlight my own accomplishments'|True
'A3'|'modest'|'I prefer to downplay my successes'|False

Please provide {N} new questions in this EXACT format.
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

'Scale Key'|'Trait Key'|'Item Text'|'Reverse'

Example:
'A10'|'newtraitkey'|'I tend to prioritize others needs over my own'|False
'A10'|'newtraitkey'|'I often put myself first in most situations'|True
'A10'|'newtraitkey'|'I naturally consider how my actions affect others'|False

Please provide 6 new questions in this EXACT format for the SINGLE new scale. Use an appropriate new Scale Key (increment the number from existing ones in this category) and create a meaningful new Trait Key that describes the scale.
"""
