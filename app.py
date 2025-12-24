import os
import base64
import json
from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import openai
from pathlib import Path

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_chart_with_ai(image_path):
    """
    Analyze trading chart using OpenAI GPT-4 Vision
    Returns structured analysis with trade setup
    """
    try:
        # Read and encode the image
        base64_image = encode_image(image_path)
        
        # Create the prompt for analysis
        prompt = """You are an expert technical analyst. Analyze this trading chart image and provide a structured trade setup.

Your analysis should include:
1. Market type identification (crypto/forex/stocks)
2. Identified chart patterns (e.g., head and shoulders, double top, triangles, flags, etc.)
3. Key technical indicators visible (e.g., moving averages, RSI, MACD, support/resistance levels)
4. Suggested trade setup:
   - Trade direction (Long/Short)
   - Entry price level
   - Stop loss level
   - Take profit level(s)
5. Pattern explanation (brief, 2-3 sentences)
6. Trading reasoning (why this setup, key factors)
7. Confidence score (0-100%)

Important guidelines:
- Only analyze what is clearly visible in the chart
- Be specific with price levels when visible
- Use neutral, educational tone
- Include risk factors
- Emphasize this is educational analysis, not financial advice

Format your response as JSON with this structure:
{
  "market_type": "string",
  "patterns": ["array", "of", "patterns"],
  "indicators": ["array", "of", "indicators"],
  "trade_setup": {
    "direction": "Long or Short",
    "entry": "price level or description",
    "stop_loss": "price level or description",
    "take_profit": ["one or more targets"]
  },
  "pattern_explanation": "string",
  "reasoning": "string",
  "confidence_score": number,
  "risk_factors": ["array", "of", "risks"]
}"""

        # Call OpenAI API
        client = openai.OpenAI(api_key=openai.api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            }
                        }
                    ]
                }
            ],
            max_tokens=1500,
            response_format={"type": "json_object"}
        )
        
        # Parse the response
        analysis = json.loads(response.choices[0].message.content)
        
        return {
            'success': True,
            'analysis': analysis
        }
        
    except Exception as e:
        return {
            'success': False,
            'error': str(e)
        }


@app.route('/')
def index():
    """Serve the main HTML page"""
    return send_from_directory('static', 'index.html')


@app.route('/api/analyze', methods=['POST'])
def analyze_chart():
    """
    Endpoint to analyze uploaded chart image
    Expects: multipart/form-data with 'chart' file
    Returns: JSON with analysis results
    """
    # Check if file is present
    if 'chart' not in request.files:
        return jsonify({'success': False, 'error': 'No file uploaded'}), 400
    
    file = request.files['chart']
    
    # Check if file is selected
    if file.filename == '':
        return jsonify({'success': False, 'error': 'No file selected'}), 400
    
    # Check if file type is allowed
    if not allowed_file(file.filename):
        return jsonify({
            'success': False,
            'error': f'Invalid file type. Allowed types: {", ".join(ALLOWED_EXTENSIONS)}'
        }), 400
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the chart
        result = analyze_chart_with_ai(filepath)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        if result['success']:
            return jsonify(result), 200
        else:
            return jsonify(result), 500
            
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'service': 'Trading Chart Analyzer'
    }), 200


if __name__ == '__main__':
    # Check if API key is set
    if not openai.api_key:
        print("WARNING: OPENAI_API_KEY not set in environment variables")
        print("Please create a .env file with your OpenAI API key")
    
    # Get debug mode from environment (default to False for security)
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    if debug_mode:
        print("WARNING: Running in debug mode. This should NOT be used in production!")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
