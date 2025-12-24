# Trading Analysis Platform 📈

A comprehensive AI-powered trading analysis platform with user authentication, chart analysis, and performance tracking. Built for traders who want to analyze their charts using AI while keeping track of their trading performance.

## ✨ Features

### 🔐 User Account Management
- **Professional Login System**: Corporate-style authentication with secure session management
- **User Registration**: Create your personal trading account
- **Account Dashboard**: Track your trading performance and analysis history
- **Analysis History**: View all your past chart analyses with filtering options
- **Win/Loss Tracking**: Tag trades as wins or losses and track your success rate

### 🤖 AI-Powered Chart Analysis
- **GPT-4 Vision Integration**: Advanced AI pattern recognition
- **Multi-Asset Support**: Analyze Crypto, Forex, and Stock charts
- **Trading Style Customization**: 
  - Scalping (Minutes to Hours)
  - Day Trading (Intraday)
  - Swing Trading (Days to Weeks)
- **Risk Profile Settings**:
  - Conservative (Lower Risk)
  - Balanced (Moderate Risk)
  - Aggressive (Higher Risk)

### 📊 Comprehensive Trade Analysis
- **Pattern Detection**: Identifies head & shoulders, triangles, flags, and more
- **Technical Indicators**: Recognizes moving averages, RSI, MACD, support/resistance
- **Multiple Take Profit Levels**: TP1, TP2, TP3 for partial exit strategies
- **Entry & Stop Loss**: Precise levels based on chart analysis
- **Confidence Scoring**: 0-100% confidence with color-coded visualization
- **Chart Quality Detection**: AI refuses unclear charts and explains what's missing

### 📈 Performance Tracking
- **Statistics Dashboard**: View total analyses, win rate, and average confidence
- **Analysis History**: Browse past analyses with outcome tracking
- **Filter Options**: Filter by all, wins, losses, or pending trades
- **Detailed Analysis View**: Review complete analysis details including patterns, reasoning, and risk factors

### 🛡️ Safety & Educational Features
- **Daily Limits**: Free users get 5 analyses per day (unlimited for premium)
- **Educational Disclaimers**: Prominent notices that this is not financial advice
- **Risk Warnings**: Clear communication about trading risks
- **Not a Signal Service**: Explicit statement that platform is for education only

### 🎨 Professional UI/UX
- **Corporate Design**: Clean, professional interface
- **Responsive Layout**: Works on desktop, tablet, and mobile
- **Color-Coded Confidence**: Visual indication of analysis quality
- **Intuitive Navigation**: Easy to use dashboard and analyzer
- **Real-time Stats**: Live updates of your performance metrics

## 🛠️ Technology Stack

- **Backend**: Python 3.8+ with Flask 3.0
- **Authentication**: Flask-Login for secure session management
- **Database**: SQLAlchemy with SQLite (easily upgradeable to PostgreSQL)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: OpenAI GPT-4 Vision API
- **File Handling**: Werkzeug for secure uploads

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- OpenAI API key (get one from [OpenAI Platform](https://platform.openai.com/))

### Setup Steps

1. **Clone the repository**
   ```bash
   git clone https://github.com/enifuels-cell/Trading-System.git
   cd Trading-System
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment variables**
   ```bash
   # Copy the example env file
   cp .env.example .env
   
   # Edit .env and add your configuration
   # Required:
   # OPENAI_API_KEY=your_actual_api_key_here
   
   # Optional (will use defaults if not set):
   # SECRET_KEY=your_secret_key_for_sessions
   # DATABASE_URL=sqlite:///trading_system.db
   # FLASK_DEBUG=False  # Set to True only for development
   ```

5. **Run the application**
   ```bash
   python app.py
   ```
   
   The database will be automatically created on first run.
   
   **Note**: By default, debug mode is disabled for security. To enable it during development, set `FLASK_DEBUG=True` in your `.env` file.

6. **Open in browser**
   - Navigate to `http://localhost:5000`
   - Register a new account or login
   - Start analyzing charts!

## 🚀 Usage

### Getting Started

1. **Create an Account**
   - Go to the registration page
   - Fill in your details (full name, email, username, password)
   - Your account will be created and you'll be automatically logged in

2. **Analyze Your First Chart**
   - Navigate to "New Analysis" from the dashboard
   - Configure your analysis settings:
     - Select Asset Type (Crypto/Forex/Stocks)
     - Choose Trading Style (Scalping/Day Trade/Swing)
     - Set Risk Profile (Conservative/Balanced/Aggressive)
   - Upload your chart image (drag & drop or click to browse)
   - Click "Analyze Chart"

3. **Review Results**
   The analysis will display:
   - Market type identification
   - Detected chart patterns
   - Technical indicators visible
   - Suggested trade setup with entry, stop loss, and multiple take profit levels
   - Pattern explanation in beginner-friendly language
   - Trading reasoning and key factors
   - Confidence score with color-coded visualization
   - Risk factors to consider

4. **Track Your Performance**
   - Go to your dashboard to see:
     - Total analyses performed
     - Win rate percentage
     - Average confidence score
     - Analyses remaining today (for free users)
   - View your analysis history
   - Filter by all, wins, losses, or pending trades
   - Click on any past analysis to review details

### Daily Limits

- **Free Users**: 5 chart analyses per day
- **Premium Users**: Unlimited analyses (upgrade option coming soon)

## 📊 API Endpoints

### Authentication

#### `POST /api/register`
Register a new user account.

**Request Body**:
```json
{
  "username": "trader123",
  "email": "trader@example.com",
  "password": "securepass123",
  "full_name": "John Trader"
}
```

#### `POST /api/login`
Login to existing account.

**Request Body**:
```json
{
  "username": "trader123",
  "password": "securepass123",
  "remember": false
}
```

#### `POST /api/logout`
Logout from current session.

#### `GET /api/user`
Get current user information and stats.

### Analysis

#### `POST /api/analyze`
Analyze an uploaded chart image (requires authentication).

**Request**: Multipart form data with:
- `chart`: Image file (PNG, JPG, JPEG, GIF, or WEBP)
- `trading_style`: "Scalping", "Day Trade", or "Swing" (optional)
- `risk_profile`: "Conservative", "Balanced", or "Aggressive" (optional)
- `asset_type`: "Crypto", "Forex", or "Stocks" (optional)

**Response**:
```json
{
  "success": true,
  "analysis": {
    "market_type": "Crypto",
    "patterns": ["Double Bottom", "Bullish Divergence"],
    "indicators": ["Moving Average", "RSI", "Support Level"],
    "chart_quality": "clear",
    "trade_setup": {
      "direction": "Long",
      "entry": "$45,000",
      "stop_loss": "$43,500",
      "take_profit": ["$48,000 (TP1)", "$50,000 (TP2)", "$52,000 (TP3)"]
    },
    "pattern_explanation": "A double bottom pattern...",
    "reasoning": "The chart shows...",
    "confidence_score": 75,
    "risk_factors": ["High volatility", "News events"],
    "analysis_id": 123
  }
}
```

#### `GET /api/history`
Get user's analysis history.

**Query Parameters**:
- `page`: Page number (default: 1)
- `per_page`: Results per page (default: 10, max: 100)

#### `GET /api/analysis/<id>`
Get detailed information about a specific analysis.

#### `PUT /api/analysis/<id>/outcome`
Update the outcome of an analysis (win/loss/pending).

**Request Body**:
```json
{
  "outcome": "win",
  "notes": "Hit TP2 target"
}
```

#### `GET /api/stats`
Get user's trading statistics.

**Response**:
```json
{
  "success": true,
  "stats": {
    "total_analyses": 50,
    "wins": 30,
    "losses": 15,
    "pending": 5,
    "win_rate": 66.67,
    "avg_confidence": 72.5
  }
}
```

### `GET /api/health`
Health check endpoint.

## 📁 Project Structure

```
Trading-System/
├── app.py                      # Flask backend application
├── requirements.txt            # Python dependencies
├── .env.example               # Example environment variables
├── .gitignore                 # Git ignore rules
├── README.md                  # This file
├── test_app.py                # Test suite
├── static/                    # Frontend files
│   ├── login.html             # Login page
│   ├── register.html          # Registration page
│   ├── dashboard.html         # User dashboard
│   ├── analyzer.html          # Chart analyzer page
│   ├── auth-styles.css        # Authentication page styles
│   ├── dashboard-styles.css   # Dashboard styles
│   ├── styles.css             # Analyzer styles
│   ├── dashboard-script.js    # Dashboard JavaScript
│   └── analyzer-script.js     # Analyzer JavaScript
├── uploads/                   # Temporary upload directory (auto-created)
└── trading_system.db          # SQLite database (auto-created)
```

## ⚠️ Important Disclaimer

**This platform is for educational purposes only**

- This analysis should not be considered financial advice
- Trading carries significant risk and may not be suitable for all investors
- Past performance is not indicative of future results
- Always conduct your own research and consult with a qualified financial advisor
- The creators are not responsible for any financial losses incurred
- **This is NOT a signal service** - all analyses are for learning purposes only

## 🔒 Security Considerations

- User passwords are securely hashed using Werkzeug's security utilities
- Session management via Flask-Login with secure cookies
- Uploaded files are temporarily stored and deleted after analysis
- File size limited to 10MB
- Only image file types are accepted
- API keys should be kept secure in `.env` file (never commit to git)
- **Debug mode is disabled by default** - Only enable `FLASK_DEBUG=True` for local development
- For production deployment, use a proper WSGI server (e.g., Gunicorn, uWSGI)
- Database includes user isolation - users can only access their own data

## 🧪 Testing

Run the test suite:

```bash
python test_app.py
```

Tests include:
- File extension validation
- Health endpoint
- Authentication flows
- API endpoint protection
- Static file existence
- User registration

## 🚧 Future Enhancements

- [ ] Export analysis as image
- [ ] Share analysis via unique URL
- [ ] Premium subscription system
- [ ] Chart annotation overlay
- [ ] Email notifications for daily limit reset
- [ ] Multi-language support
- [ ] Dark mode
- [ ] Trading journal integration
- [ ] Performance analytics and charts
- [ ] Community features (compare with other users)

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is open source and available under the MIT License.

## 💬 Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check existing issues for solutions
- Contribute to the project

## 🙏 Acknowledgments

- OpenAI for the GPT-4 Vision API
- Flask community for the excellent web framework
- All contributors and users of this platform

---

**Happy Trading! Remember: This is for educational purposes only. Always trade responsibly!** 📈📉