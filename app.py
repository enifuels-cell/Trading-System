import os
import base64
import json
from datetime import datetime, timedelta
from flask import Flask, request, jsonify, send_from_directory, redirect, url_for, session
from flask_cors import CORS
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from dotenv import load_dotenv
import openai
from pathlib import Path

# Load environment variables
load_dotenv()

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///trading_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

app = Flask(__name__, static_folder='static', static_url_path='')
CORS(app)

# Secret key for session management
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', 'dev-secret-key-change-in-production')

# Database configuration
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///trading_system.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize extensions
db = SQLAlchemy(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login_page'

# Configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
FREE_USER_DAILY_LIMIT = 5  # Daily analysis limit for free users

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = MAX_FILE_SIZE

# Create uploads directory if it doesn't exist
Path(UPLOAD_FOLDER).mkdir(exist_ok=True)

# OpenAI API key
openai.api_key = os.getenv('OPENAI_API_KEY')


# Database Models
class User(UserMixin, db.Model):
    """User account model"""
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    full_name = db.Column(db.String(120))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_premium = db.Column(db.Boolean, default=False)
    
    # Relationships
    analyses = db.relationship('TradeAnalysis', backref='user', lazy=True, cascade='all, delete-orphan')
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
    
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def get_today_analysis_count(self):
        """Get number of analyses done today"""
        today = datetime.utcnow().date()
        return TradeAnalysis.query.filter(
            TradeAnalysis.user_id == self.id,
            db.func.date(TradeAnalysis.created_at) == today
        ).count()
    
    def can_analyze(self):
        """Check if user can perform analysis (considering daily limit)"""
        if self.is_premium:
            return True
        return self.get_today_analysis_count() < FREE_USER_DAILY_LIMIT


class TradeAnalysis(db.Model):
    """Trade analysis history model"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    
    # Analysis parameters
    market_type = db.Column(db.String(50))
    trading_style = db.Column(db.String(50))  # Scalping/Day Trade/Swing
    risk_profile = db.Column(db.String(50))  # Conservative/Balanced/Aggressive
    asset_type = db.Column(db.String(50))  # Crypto/Forex/Stocks
    
    # Analysis results (stored as JSON)
    patterns = db.Column(db.Text)  # JSON array
    indicators = db.Column(db.Text)  # JSON array
    trade_direction = db.Column(db.String(20))  # Long/Short
    entry_price = db.Column(db.String(100))
    stop_loss = db.Column(db.String(100))
    take_profit = db.Column(db.Text)  # JSON array for multiple TPs
    pattern_explanation = db.Column(db.Text)
    reasoning = db.Column(db.Text)
    confidence_score = db.Column(db.Integer)
    risk_factors = db.Column(db.Text)  # JSON array
    
    # User feedback
    outcome = db.Column(db.String(20))  # win/loss/pending
    notes = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


@login_manager.user_loader
def load_user(user_id):
    """Load user for Flask-Login"""
    return User.query.get(int(user_id))


def allowed_file(filename):
    """Check if file extension is allowed"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def encode_image(image_path):
    """Encode image to base64"""
    with open(image_path, "rb") as image_file:
        return base64.b64encode(image_file.read()).decode('utf-8')


def analyze_chart_with_ai(image_path, trading_style='Day Trade', risk_profile='Balanced', asset_type='Crypto'):
    """
    Analyze trading chart using OpenAI GPT-4 Vision
    Returns structured analysis with trade setup
    """
    try:
        # Read and encode the image
        base64_image = encode_image(image_path)
        
        # Adjust prompt based on trading style and risk profile
        style_adjustments = {
            'Scalping': 'Focus on very short-term price movements (minutes to hours). Tighter stop losses and quicker profit targets.',
            'Day Trade': 'Focus on intraday movements. Positions closed within the same trading day.',
            'Swing': 'Focus on multi-day to multi-week price movements. Wider stop losses and larger profit targets.'
        }
        
        risk_adjustments = {
            'Conservative': 'Recommend tighter stop losses and smaller position sizing. Risk-reward ratio of at least 1:2.',
            'Balanced': 'Moderate risk approach with standard risk-reward ratio of 1:1.5 to 1:2.',
            'Aggressive': 'Accept higher risk for potentially higher rewards. Risk-reward ratio of 1:1 to 1:1.5 is acceptable.'
        }
        
        # Create the prompt for analysis
        prompt = f"""You are an expert technical analyst. Analyze this trading chart image and provide a structured trade setup.

Trading Context:
- Asset Type: {asset_type}
- Trading Style: {trading_style} - {style_adjustments.get(trading_style, '')}
- Risk Profile: {risk_profile} - {risk_adjustments.get(risk_profile, '')}

Your analysis should include:
1. Market type identification (crypto/forex/stocks)
2. Identified chart patterns (e.g., head and shoulders, double top, triangles, flags, etc.)
3. Key technical indicators visible (e.g., moving averages, RSI, MACD, support/resistance levels)
4. Chart quality assessment - if the chart is unclear, blurry, missing timeframe, or lacks key information, note this
5. Suggested trade setup:
   - Trade direction (Long/Short)
   - Entry price level
   - Stop loss level
   - Multiple take profit levels (TP1, TP2, TP3) for partial exits
6. Pattern explanation (brief, 2-3 sentences)
7. Trading reasoning (why this setup, key factors)
8. Confidence score (0-100%) - lower confidence if chart is unclear
9. Specific reasons if chart quality is poor

Important guidelines:
- Only analyze what is clearly visible in the chart
- If chart is unclear, blurry, or missing critical information (like timeframe), set confidence below 30% and explain issues
- Be specific with price levels when visible
- Use neutral, educational tone
- Include risk factors
- Emphasize this is educational analysis, not financial advice
- Adjust recommendations based on the trading style and risk profile provided

Format your response as JSON with this structure:
{{
  "market_type": "string",
  "patterns": ["array", "of", "patterns"],
  "indicators": ["array", "of", "indicators"],
  "chart_quality": "clear/moderate/poor",
  "chart_issues": ["array of issues if quality is poor"],
  "trade_setup": {{
    "direction": "Long or Short",
    "entry": "price level or description",
    "stop_loss": "price level or description",
    "take_profit": ["TP1", "TP2", "TP3"]
  }},
  "pattern_explanation": "string",
  "reasoning": "string",
  "confidence_score": number,
  "risk_factors": ["array", "of", "risks"]
}}"""

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
    if current_user.is_authenticated:
        return send_from_directory('static', 'dashboard.html')
    return send_from_directory('static', 'login.html')


@app.route('/login')
def login_page():
    """Serve the login page"""
    return send_from_directory('static', 'login.html')


@app.route('/register')
def register_page():
    """Serve the registration page"""
    return send_from_directory('static', 'register.html')


@app.route('/dashboard')
@login_required
def dashboard():
    """Serve the user dashboard"""
    return send_from_directory('static', 'dashboard.html')


@app.route('/analyzer')
@login_required
def analyzer():
    """Serve the chart analyzer page"""
    return send_from_directory('static', 'analyzer.html')


# Authentication API endpoints
@app.route('/api/register', methods=['POST'])
def register():
    """Register a new user"""
    data = request.get_json()
    
    # Validate required fields
    required_fields = ['username', 'email', 'password', 'full_name']
    for field in required_fields:
        if field not in data or not data[field]:
            return jsonify({'success': False, 'error': f'{field} is required'}), 400
    
    # Check if username already exists
    if User.query.filter_by(username=data['username']).first():
        return jsonify({'success': False, 'error': 'Username already exists'}), 400
    
    # Check if email already exists
    if User.query.filter_by(email=data['email']).first():
        return jsonify({'success': False, 'error': 'Email already exists'}), 400
    
    # Create new user
    user = User(
        username=data['username'],
        email=data['email'],
        full_name=data['full_name']
    )
    user.set_password(data['password'])
    
    try:
        db.session.add(user)
        db.session.commit()
        
        # Log the user in
        login_user(user)
        
        return jsonify({
            'success': True,
            'message': 'Registration successful',
            'user': {
                'username': user.username,
                'email': user.email,
                'full_name': user.full_name
            }
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/login', methods=['POST'])
def login():
    """Login user"""
    data = request.get_json()
    
    # Validate required fields
    if not data.get('username') or not data.get('password'):
        return jsonify({'success': False, 'error': 'Username and password are required'}), 400
    
    # Find user by username or email
    user = User.query.filter(
        (User.username == data['username']) | (User.email == data['username'])
    ).first()
    
    # Check password
    if not user or not user.check_password(data['password']):
        return jsonify({'success': False, 'error': 'Invalid username or password'}), 401
    
    # Log the user in
    login_user(user, remember=data.get('remember', False))
    
    return jsonify({
        'success': True,
        'message': 'Login successful',
        'user': {
            'username': user.username,
            'email': user.email,
            'full_name': user.full_name,
            'is_premium': user.is_premium
        }
    }), 200


@app.route('/api/logout', methods=['POST'])
@login_required
def logout():
    """Logout user"""
    logout_user()
    return jsonify({'success': True, 'message': 'Logout successful'}), 200


@app.route('/api/user', methods=['GET'])
@login_required
def get_user():
    """Get current user information"""
    return jsonify({
        'success': True,
        'user': {
            'id': current_user.id,
            'username': current_user.username,
            'email': current_user.email,
            'full_name': current_user.full_name,
            'is_premium': current_user.is_premium,
            'analyses_today': current_user.get_today_analysis_count(),
            'daily_limit': FREE_USER_DAILY_LIMIT if not current_user.is_premium else 'Unlimited',
            'can_analyze': current_user.can_analyze()
        }
    }), 200


@app.route('/api/analyze', methods=['POST'])
@login_required
def analyze_chart():
    """
    Endpoint to analyze uploaded chart image
    Expects: multipart/form-data with 'chart' file and optional parameters
    Returns: JSON with analysis results
    """
    # Check if user can analyze (daily limit)
    if not current_user.can_analyze():
        return jsonify({
            'success': False,
            'error': f'Daily analysis limit reached ({FREE_USER_DAILY_LIMIT} analyses per day for free users). Upgrade to premium for unlimited access.'
        }), 429
    
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
    
    # Get optional parameters
    trading_style = request.form.get('trading_style', 'Day Trade')
    risk_profile = request.form.get('risk_profile', 'Balanced')
    asset_type = request.form.get('asset_type', 'Crypto')
    
    try:
        # Save the uploaded file
        filename = secure_filename(file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(filepath)
        
        # Analyze the chart
        result = analyze_chart_with_ai(filepath, trading_style, risk_profile, asset_type)
        
        # Clean up uploaded file
        try:
            os.remove(filepath)
        except:
            pass
        
        if result['success']:
            analysis = result['analysis']
            
            # Save analysis to database
            trade_analysis = TradeAnalysis(
                user_id=current_user.id,
                market_type=analysis.get('market_type'),
                trading_style=trading_style,
                risk_profile=risk_profile,
                asset_type=asset_type,
                patterns=json.dumps(analysis.get('patterns', [])),
                indicators=json.dumps(analysis.get('indicators', [])),
                trade_direction=analysis.get('trade_setup', {}).get('direction'),
                entry_price=analysis.get('trade_setup', {}).get('entry'),
                stop_loss=analysis.get('trade_setup', {}).get('stop_loss'),
                take_profit=json.dumps(analysis.get('trade_setup', {}).get('take_profit', [])),
                pattern_explanation=analysis.get('pattern_explanation'),
                reasoning=analysis.get('reasoning'),
                confidence_score=analysis.get('confidence_score'),
                risk_factors=json.dumps(analysis.get('risk_factors', [])),
                outcome='pending'
            )
            
            db.session.add(trade_analysis)
            db.session.commit()
            
            # Add analysis ID to response
            result['analysis']['analysis_id'] = trade_analysis.id
            
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


@app.route('/api/history', methods=['GET'])
@login_required
def get_analysis_history():
    """Get user's analysis history"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 10, type=int)
    
    # Get user's analyses with pagination
    pagination = TradeAnalysis.query.filter_by(user_id=current_user.id)\
        .order_by(TradeAnalysis.created_at.desc())\
        .paginate(page=page, per_page=per_page, error_out=False)
    
    analyses = []
    for analysis in pagination.items:
        analyses.append({
            'id': analysis.id,
            'market_type': analysis.market_type,
            'trading_style': analysis.trading_style,
            'risk_profile': analysis.risk_profile,
            'asset_type': analysis.asset_type,
            'trade_direction': analysis.trade_direction,
            'entry_price': analysis.entry_price,
            'stop_loss': analysis.stop_loss,
            'take_profit': json.loads(analysis.take_profit) if analysis.take_profit else [],
            'confidence_score': analysis.confidence_score,
            'outcome': analysis.outcome,
            'created_at': analysis.created_at.isoformat()
        })
    
    return jsonify({
        'success': True,
        'analyses': analyses,
        'total': pagination.total,
        'page': page,
        'per_page': per_page,
        'pages': pagination.pages
    }), 200


@app.route('/api/analysis/<int:analysis_id>', methods=['GET'])
@login_required
def get_analysis_detail(analysis_id):
    """Get detailed information about a specific analysis"""
    analysis = TradeAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({'success': False, 'error': 'Analysis not found'}), 404
    
    return jsonify({
        'success': True,
        'analysis': {
            'id': analysis.id,
            'market_type': analysis.market_type,
            'trading_style': analysis.trading_style,
            'risk_profile': analysis.risk_profile,
            'asset_type': analysis.asset_type,
            'patterns': json.loads(analysis.patterns) if analysis.patterns else [],
            'indicators': json.loads(analysis.indicators) if analysis.indicators else [],
            'trade_direction': analysis.trade_direction,
            'entry_price': analysis.entry_price,
            'stop_loss': analysis.stop_loss,
            'take_profit': json.loads(analysis.take_profit) if analysis.take_profit else [],
            'pattern_explanation': analysis.pattern_explanation,
            'reasoning': analysis.reasoning,
            'confidence_score': analysis.confidence_score,
            'risk_factors': json.loads(analysis.risk_factors) if analysis.risk_factors else [],
            'outcome': analysis.outcome,
            'notes': analysis.notes,
            'created_at': analysis.created_at.isoformat()
        }
    }), 200


@app.route('/api/analysis/<int:analysis_id>/outcome', methods=['PUT'])
@login_required
def update_analysis_outcome(analysis_id):
    """Update the outcome of an analysis (win/loss)"""
    analysis = TradeAnalysis.query.filter_by(id=analysis_id, user_id=current_user.id).first()
    
    if not analysis:
        return jsonify({'success': False, 'error': 'Analysis not found'}), 404
    
    data = request.get_json()
    outcome = data.get('outcome')
    notes = data.get('notes', '')
    
    if outcome not in ['win', 'loss', 'pending']:
        return jsonify({'success': False, 'error': 'Invalid outcome. Must be win, loss, or pending'}), 400
    
    analysis.outcome = outcome
    analysis.notes = notes
    
    try:
        db.session.commit()
        return jsonify({'success': True, 'message': 'Outcome updated successfully'}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/stats', methods=['GET'])
@login_required
def get_user_stats():
    """Get user's trading statistics"""
    total_analyses = TradeAnalysis.query.filter_by(user_id=current_user.id).count()
    
    wins = TradeAnalysis.query.filter_by(user_id=current_user.id, outcome='win').count()
    losses = TradeAnalysis.query.filter_by(user_id=current_user.id, outcome='loss').count()
    pending = TradeAnalysis.query.filter_by(user_id=current_user.id, outcome='pending').count()
    
    # Calculate win rate
    win_rate = 0
    if wins + losses > 0:
        win_rate = round((wins / (wins + losses)) * 100, 2)
    
    # Get average confidence score
    avg_confidence = db.session.query(db.func.avg(TradeAnalysis.confidence_score))\
        .filter(TradeAnalysis.user_id == current_user.id).scalar()
    avg_confidence = round(avg_confidence, 2) if avg_confidence else 0
    
    return jsonify({
        'success': True,
        'stats': {
            'total_analyses': total_analyses,
            'wins': wins,
            'losses': losses,
            'pending': pending,
            'win_rate': win_rate,
            'avg_confidence': avg_confidence
        }
    }), 200


if __name__ == '__main__':
    # Initialize database
    with app.app_context():
        db.create_all()
        print("Database initialized successfully")
    
    # Check if API key is set
    if not openai.api_key:
        print("WARNING: OPENAI_API_KEY not set in environment variables")
        print("Please create a .env file with your OpenAI API key")
    
    # Get debug mode from environment (default to False for security)
    debug_mode = os.getenv('FLASK_DEBUG', 'False').lower() in ('true', '1', 'yes')
    
    if debug_mode:
        print("WARNING: Running in debug mode. This should NOT be used in production!")
    
    app.run(debug=debug_mode, host='0.0.0.0', port=5000)
