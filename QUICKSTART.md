# Quick Start Guide

## Getting Started

### 1. Prerequisites
- Python 3.8 or higher installed
- OpenAI API key (get one from https://platform.openai.com/)

### 2. Installation

```bash
# Clone the repository
git clone https://github.com/enifuels-cell/Trading-System.git
cd Trading-System

# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

```bash
# Copy environment template
cp .env.example .env

# Edit .env file and add your OpenAI API key
# OPENAI_API_KEY=sk-your-actual-api-key-here
# FLASK_DEBUG=True  # Optional, for development only
```

### 4. Run the Application

```bash
python app.py
```

The application will start on http://localhost:5000

## Using the Application

### Uploading a Chart
1. Open http://localhost:5000 in your browser
2. Click the upload area or drag and drop a chart image
3. Supported formats: PNG, JPG, JPEG, GIF, WEBP (max 10MB)

### Getting Analysis
1. After uploading, click "Analyze Chart"
2. Wait for the AI to process (typically 10-30 seconds)
3. Review the analysis results including:
   - Market type identification
   - Chart patterns detected
   - Technical indicators found
   - Trade setup with entry, stop loss, take profit
   - Pattern explanation and reasoning
   - Confidence score
   - Risk factors

### Analyzing Another Chart
Click "Analyze Another Chart" to start over with a new image

## Example Analysis Output

The system will identify patterns such as:
- **Chart Patterns**: Head & Shoulders, Double Top/Bottom, Triangles, Flags, Wedges
- **Indicators**: Moving Averages, RSI, MACD, Support/Resistance Levels, Volume
- **Trade Setup**: Long/Short direction with specific price levels

## Important Notes

### Educational Purpose Only
⚠️ This tool is for educational purposes only. The analysis provided:
- Should NOT be considered financial advice
- Does not guarantee profits or predict future results
- Is based only on visible chart information
- Should be verified with your own research
- Requires consultation with a qualified financial advisor before trading

### API Costs
- Each analysis uses the OpenAI GPT-4 Vision API
- Costs approximately $0.01-0.03 per analysis
- Monitor your OpenAI usage at https://platform.openai.com/usage

### Best Practices
1. Use clear, high-quality chart images
2. Ensure price levels and indicators are visible
3. Include timeframe information in the chart if possible
4. Verify AI suggestions with manual technical analysis
5. Never trade based solely on AI analysis

## Troubleshooting

### "OPENAI_API_KEY not set" warning
- Make sure you've created a `.env` file
- Verify your API key is correctly copied (no extra spaces)
- Ensure the `.env` file is in the project root directory

### "Failed to connect to the server" error
- Check if the Flask server is running
- Verify you're accessing http://localhost:5000
- Check firewall settings

### "Invalid file type" error
- Ensure your image is in a supported format (PNG, JPG, JPEG, GIF, WEBP)
- Verify the file is not corrupted
- Check file size is under 10MB

### Analysis returns unexpected results
- Use higher quality, clearer chart images
- Ensure the chart is not too cluttered
- Try images with clear price levels and indicators
- Make sure the chart is properly cropped

## Production Deployment

For production use:
1. Set `FLASK_DEBUG=False` (default)
2. Use a production WSGI server (Gunicorn, uWSGI)
3. Set up HTTPS with SSL certificates
4. Implement rate limiting
5. Add user authentication if needed
6. Monitor API usage and costs

Example with Gunicorn:
```bash
pip install gunicorn
gunicorn -w 4 -b 0.0.0.0:5000 app:app
```

## Support

For issues or questions:
- Review the README.md for detailed documentation
- Check the test_app.py file for usage examples
- Open an issue on GitHub

## License

This project is open source under the MIT License.
