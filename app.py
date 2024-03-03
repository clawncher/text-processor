from language_tool_python import LanguageTool
from pathlib import Path
from loguru import logger
from flask import Flask, render_template, request, jsonify
from transformers import pipeline
import os
from werkzeug.utils import secure_filename
from PyPDF2 import PdfReader
from docx.document import Document

UPLOAD_FOLDER = os.environ.get('UPLOAD_FOLDER')

app = Flask(__name__)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

ALLOWED_EXTENSIONS = {'pdf', 'txt', 'doc', 'docx'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

class ModelLoader:
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    translator_de = pipeline(task="translation", model="Helsinki-NLP/opus-mt-en-de")
    translator_hi = pipeline(task="translation", model="Helsinki-NLP/opus-mt-en-hi")
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    qa_model = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')

model_loader = ModelLoader()

def extract_text_from_pdf(pdf_path):
    try:
        with open(pdf_path, 'rb') as file:
            reader = PdfReader(file)
            text = ''.join(page.extract_text() for page in reader.pages)
        return text
    except Exception as e:
        logger.error(f"Failed to extract text from PDF: {e}")
        return None

def extract_text_from_docx(docx_path):
    try:
        doc = Document(docx_path)
        text = ''
        for para in doc.paragraphs:
            text += para.text + '\n'
        return text
    except Exception as e:
        logger.error(f"Error reading DOCX file: {e}")
        return ""

def summarize_document_file(file_path):
    file_extension = file_path.rsplit('.', 1)[1].lower()

    if file_extension not in ALLOWED_EXTENSIONS:
        return "Unsupported file format."

    try:
        if file_extension == 'pdf':
            text = extract_text_from_pdf(file_path)
        elif file_extension in {'txt', 'doc', 'docx'}:
            text = extract_text_from_docx(file_path)
        else:
            return "Unsupported file format."

        return summarize_text(text)

    except Exception as e:
        logger.error(f"Error processing file: {e}")
        return "Error processing file."


def reformat_text(text):
    reformatted_text = text.lower()
    return reformatted_text

def grammar_check(text):
    tool = LanguageTool('en-US')
    corrected_text = tool.correct(text)
    return corrected_text

def summarize_text(text, summarizer):
    max_length = 200
    summary = summarizer(text, max_length=max_length, do_sample=False)
    return summary[0]['summary_text']

def translate_text(text, target_language):
    if target_language == 'de':
        translated_text = translator_de(text, max_length=1000, return_text=True)[0]['translation_text']
    elif target_language == 'hi':
        translated_text = translator_hi(text, max_length=1000, return_text=True)[0]['translation_text']
    else:
        translated_text = "Error: Invalid target language"
    return translated_text

def additional_capabilities(text, sentiment_analyzer, qa_model):
    sentiment_result = sentiment_analyzer(text)[0]
    sentiment = sentiment_result['label']
    sentiment_score = sentiment_result['score']
    question = "What is the main idea of the text?"
    answer = qa_model(question=question, context=text)['answer']
    return sentiment, sentiment_score, answer

def load_models():
    global summarizer, translator_de, translator_hi, sentiment_analyzer, qa_model
    summarizer = pipeline("summarization", model="sshleifer/distilbart-cnn-12-6")
    translator_de = pipeline(task="translation", model="Helsinki-NLP/opus-mt-en-de")
    translator_hi = pipeline(task="translation", model="Helsinki-NLP/opus-mt-en-hi")
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    qa_model = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')

load_models()

def process_text_choice_1(user_input):
    reformatted_text = reformat_text(user_input)
    return jsonify({'result': reformatted_text})

def process_text_choice_2(user_input):
    corrected_text = grammar_check(user_input)
    return jsonify({'result': corrected_text})

def process_text_choice_3(user_input):
    reformatted_text = reformat_text(user_input)
    grammar_checked_text = grammar_check(reformatted_text)
    summary = summarize_text(grammar_checked_text, summarizer)
    return jsonify({
        'summary': summary
    })

def process_text_choice_4(user_input):
    reformatted_text = reformat_text(user_input)
    grammar_checked_text = grammar_check(reformatted_text)
    
    # Check if target_language parameter exists in the request
    target_language = request.form.get('target_language')

    if target_language not in {'de', 'hi'}:
        return jsonify({'error': 'Invalid target language'})

    translated_text = translate_text(grammar_checked_text, target_language)
    return jsonify({
        'translated_text': translated_text
    })

def process_text_choice_5(user_input):
    sentiment_analyzer = pipeline("sentiment-analysis", model="distilbert-base-uncased-finetuned-sst-2-english")
    qa_model = pipeline('question-answering', model='distilbert-base-cased-distilled-squad')
    sentiment, sentiment_score, answer = additional_capabilities(user_input, sentiment_analyzer, qa_model)
    return jsonify({
        'original_text': user_input,
        'sentiment': sentiment,
        'sentiment_score': sentiment_score,
        'answer': answer
    })

def process_text_choice_6(user_input):
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']
    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        document_summary = summarize_document_file(file_path)
        os.remove(file_path)
        return jsonify({'document_summary': document_summary})
    else:
        return jsonify({'error': 'Unsupported file format'})

process_text_choices = {
    '1': process_text_choice_1,
    '2': process_text_choice_2,
    '3': process_text_choice_3,
    '4': process_text_choice_4,
    '5': process_text_choice_5,
    '6': process_text_choice_6,
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/process_text', methods=['POST'])
def process_text():
    user_input = request.form['user_input']
    choice = request.form['choice']

    if choice in process_text_choices:
        return process_text_choices[choice](user_input)

    return jsonify({'error': 'Invalid choice'})

if __name__ == '__main__':
    logger.add("app.log", level="INFO")
    app.run(debug=True)