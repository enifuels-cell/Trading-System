# Trading Chart Analyzer 📈

An AI-powered web application that analyzes trading chart screenshots (crypto, forex, or stocks) and provides technical analysis with trade setups for educational purposes.

## Features

- 🖼️ **Image Upload**: Upload trading chart screenshots via drag-and-drop or file selection
- 🤖 **AI Analysis**: Powered by GPT-4 Vision for accurate pattern recognition
- 📊 **Pattern Identification**: Detects common chart patterns (head & shoulders, triangles, flags, etc.)
- 📉 **Trade Setup**: Provides entry points, stop loss, and take profit levels
- 💯 **Confidence Score**: Each analysis includes a confidence percentage
- ⚠️ **Risk Assessment**: Identifies potential risk factors
- 🎓 **Educational Focus**: Clear disclaimer that this is for learning, not financial advice

## Technology Stack

- **Backend**: Python with Flask
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **AI**: OpenAI GPT-4 Vision API
- **File Handling**: Werkzeug for secure uploads

## Installation

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
   
   # Edit .env and add your OpenAI API key
   # OPENAI_API_KEY=your_actual_api_key_here
   # FLASK_DEBUG=True  # Only for development, set to False for production
   ```

5. **Run the application**
   ```bash
   python app.py
   ```
   
   **Note**: By default, debug mode is disabled for security. To enable it during development, set `FLASK_DEBUG=True` in your `.env` file.

6. **Open in browser**
   - Navigate to `http://localhost:5000`
   - Upload a trading chart and click "Analyze Chart"

## Usage

1. **Upload a Chart**: Click the upload box or drag and drop a trading chart image (PNG, JPG, JPEG, GIF, or WEBP, max 10MB)

2. **Analyze**: Click the "Analyze Chart" button to start the AI analysis

3. **Review Results**: The analysis will display:
   - Market type (crypto/forex/stocks)
   - Identified chart patterns
   - Technical indicators visible
   - Suggested trade setup with entry, stop loss, and take profit
   - Pattern explanation and trading reasoning
   - Confidence score
   - Risk factors

4. **Analyze Another**: Click "Analyze Another Chart" to start over

## API Endpoints

### `POST /api/analyze`
Analyzes an uploaded chart image.

**Request**: Multipart form data with `chart` file

**Response**:
```json
{
  "success": true,
  "analysis": {
    "market_type": "Crypto",
    "patterns": ["Double Bottom", "Bullish Divergence"],
    "indicators": ["Moving Average", "RSI", "Support Level"],
    "trade_setup": {
      "direction": "Long",
      "entry": "$45,000",
      "stop_loss": "$43,500",
      "take_profit": ["$48,000", "$50,000"]
    },
    "pattern_explanation": "A double bottom pattern...",
    "reasoning": "The chart shows...",
    "confidence_score": 75,
    "risk_factors": ["High volatility", "News events"]
  }
}
```

### `GET /api/health`
Health check endpoint.

**Response**:
```json
{
  "status": "healthy",
  "service": "Trading Chart Analyzer"
}
```

## Project Structure

```
Trading-System/
├── app.py                 # Flask backend application
├── requirements.txt       # Python dependencies
├── .env.example          # Example environment variables
├── .gitignore            # Git ignore rules
├── README.md             # This file
├── static/               # Frontend files
│   ├── index.html        # Main HTML page
│   ├── styles.css        # CSS styles
│   └── script.js         # JavaScript functionality
└── uploads/              # Temporary upload directory (auto-created)
```

## Important Disclaimer

⚠️ **This tool is for educational purposes only**

- This analysis should not be considered financial advice
- Trading carries significant risk and may not be suitable for all investors
- Past performance is not indicative of future results
- Always conduct your own research and consult with a qualified financial advisor
- The creators are not responsible for any financial losses incurred

## Security Considerations

- Uploaded files are temporarily stored and deleted after analysis
- File size limited to 10MB
- Only image file types are accepted
- API keys should be kept secure in `.env` file (never commit to git)
- **Debug mode is disabled by default** - Only enable `FLASK_DEBUG=True` for local development
- For production deployment, use a proper WSGI server (e.g., Gunicorn, uWSGI) instead of Flask's built-in server

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is open source and available under the MIT License.

## Support

For issues, questions, or suggestions, please open an issue on GitHub.