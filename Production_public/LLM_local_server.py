#this is backup incase you can't use open AI for summarising
from flask import Flask, request, jsonify
from transformers import pipeline, AutoTokenizer, AutoModelForSeq2SeqLM
import torch

app = Flask(__name__)

device = "cuda" if torch.cuda.is_available() else "cpu"
model_name = "facebook/bart-large-cnn"
tokenizer = AutoTokenizer.from_pretrained(model_name)
model = AutoModelForSeq2SeqLM.from_pretrained(model_name)
summarizer = pipeline("summarization", model=model, tokenizer=tokenizer, device=0 if device == "cuda" else -1)

@app.route('/summarize', methods=['POST'])
def summarize():
    data = request.json
    text = data['text']
    max_input_length = data.get('max_input_length', 400)
    max_output_length = data.get('max_output_length', 80)
    min_output_length = data.get('min_output_length', 12)
    
    if len(text) > max_input_length:
        end_index = text[:max_input_length].rfind(' ')
        if end_index == -1:
            end_index = max_input_length
        text = text[:end_index]
    
    summary = summarizer(text, max_length=max_output_length, min_length=min_output_length, do_sample=False)
    headline = summary[0]['summary_text']
    
    return jsonify({'headline': headline})

def run():
    app.run(host='0.0.0.0', port=5000)

run()