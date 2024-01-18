new_questions_prompt = """
Your job is to help create new questions for the psychometric scale: {scale}. 
The questions should be varied, accurate, and fairly straightforward in terms of their content and should use the original questions as inspiration in terms of style and tone. 
Be sure to occasionally add in reverse scored items.
Existing items to use as inspiration: {existing_items}
Format each question as a separate line, using '|' as a delimiter between fields.
"""
