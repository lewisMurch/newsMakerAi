#This is a test for the Local LLM
import requests
text = """
Biden ends election campaign and endorses Harris as Democratic nominee
US President Joe Biden and Vice-President Kamala Harris
Summary

    US President Joe Biden withdraws from the presidential race after weeks of mounting pressure from Democrats

    He says it's "in the best interest of my party and the country" – but will stay on for the final six months of his term
"""

response = requests.post('http://localhost:5000/summarize', json={
    'text': text,
    'max_input_length': 400,
    'max_output_length': 80,
    'min_output_length': 10
})
summary = response.json()

print('\n\n', summary, '\n\n')