from flask import Flask, request, send_file, jsonify
from flask_cors import CORS
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from transformers import pipeline
import io
import torch

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

# Load the translation model (Helsinki-NLP/opus-mt-es-en for Spanish to English)
translator = pipeline("translation", model="Helsinki-NLP/opus-mt-es-en", device=0 if torch.cuda.is_available() else -1)

@app.route('/translate', methods=['POST'])
def translate_pdf():
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file.filename.endswith('.pdf'):
        return jsonify({'error': 'File must be PDF'}), 400
    
    # Extract text from input PDF
    text = ''
    with pdfplumber.open(file) as pdf:
        for page in pdf.pages:
            page_text = page.extract_text()
            if page_text:
                text += page_text + '\n\n'
    
    if not text.strip():
        return jsonify({'error': 'No text found in PDF'}), 400
    
    # Translate text in chunks to handle token limits
    max_length = 512
    chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
    translated_chunks = [translator(chunk)[0]['translation_text'] for chunk in chunks]
    translated_text = ' '.join(translated_chunks)
    
    # Create output PDF
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    flowables = []
    for line in translated_text.split('\n'):
        if line.strip():
            flowables.append(Paragraph(line, styles['Normal']))
    doc.build(flowables)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name='translated.pdf', mimetype='application/pdf')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)