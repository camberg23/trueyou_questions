new_questions_prompt = """
Your job is to help create {N} new questions for the psychometric scale: {scale}. 
The questions should be varied, accurate, and straightforward in content, using the original questions as inspiration in terms of style and tone. 
Occasionally include reverse scored items.

Existing items to use as inspiration: {existing_items}

Format each new question as follows, with each field separated by a '|' and each question on a new line:

'Category'|'Scale Name'|'Scale #'|'Scale Key'|'Item Text'|'Session'|'Trait Key'|'Reverse'

Example:
'A'|'Accommodating'|1|'A1'|'new question text 1'|0|'accommodating'|False
'A'|'Accommodating'|1|'A1'|'new question text 2'|0|'accommodating'|False
'A'|'Accommodating'|1|'A1'|'new question text 3'|0|'accommodating'|True

Please provide {N} new questions in this EXACT format.
"""
