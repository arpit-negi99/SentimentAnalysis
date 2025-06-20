# YouTube Video Sentiment Analysis

A Flask web application that analyzes the sentiment of YouTube video comments to generate an overall rating for the video based on viewer opinions.

## Features

- **YouTube Integration**: Fetches comments from any public YouTube video using the YouTube Data API v3
- **Sentiment Analysis**: Uses NLTK's VADER sentiment analyzer to evaluate comment sentiment
- **Text Processing**: Implements natural language processing techniques including stemming and stopword removal
- **Rating System**: Generates a 0-5 star rating based on sentiment analysis of comments
- **Web Interface**: Clean, simple web interface for entering YouTube video URLs
- **Video Details**: Displays video title and thumbnail alongside the analysis

## How It Works

1. **Comment Extraction**: The application fetches up to 100+ comments from a YouTube video using the YouTube Data API
2. **Text Preprocessing**: Comments are cleaned by removing special characters, converting to lowercase, removing stopwords, and applying stemming
3. **Sentiment Analysis**: Each processed comment is analyzed using NLTK's VADER sentiment analyzer
4. **Rating Calculation**: A weighted algorithm combines positive, negative, and compound sentiment scores to generate a final rating out of 5

## Requirements

### Dependencies
- Flask
- google-api-python-client
- pandas
- nltk
- tqdm
- re (built-in)

### API Requirements
- YouTube Data API v3 key from Google Cloud Console

## Installation

1. **Clone or download the project files**

2. **Install required packages**:
   ```bash
   pip install flask google-api-python-client pandas nltk tqdm
   ```

3. **Download NLTK data**:
   ```python
   import nltk
   nltk.download('vader_lexicon')
   nltk.download('punkt')
   nltk.download('stopwords')
   ```

4. **Set up YouTube API**:
   - Visit [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable YouTube Data API v3
   - Create credentials (API key)
   - Replace `DEVELOPER_KEY` in `app.py` with your API key

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```

2. **Access the web interface**:
   - Open your browser and go to `http://localhost:8080`

3. **Analyze a video**:
   - Enter a YouTube video URL in the input field
   - Click "Analyze" to process the video
   - View the sentiment-based rating and video details

## File Structure

```
project/
│
├── app.py          # Main Flask application
├── index.html      # HTML template (should be in templates/ folder)
└── README.md       # This file
```

**Note**: For proper Flask functionality, create a `templates/` directory and move `index.html` into it.

## API Key Security

⚠️ **Important Security Note**: The current implementation has the API key hardcoded in the source code. For production use, consider:

- Using environment variables to store the API key
- Adding the API key to a `.env` file and loading it with python-dotenv
- Using cloud-based secret management services

Example with environment variables:
```python
import os
DEVELOPER_KEY = os.environ.get('YOUTUBE_API_KEY')
```

## Rating Algorithm

The application uses a sophisticated weighting system:

- **Compound Score**: Base sentiment score (-1 to 1) normalized to 0-3 scale
- **Positive Weight**: Dynamically assigned (1-5) based on positive sentiment strength
- **Negative Weight**: Fixed penalty multiplier (1.5)
- **Final Calculation**: `((compound + 1) / 2 * 3) + (positive * weight) - (negative * 1.5)`
- **Range**: Final rating is clamped between 0-5 and rounded to 2 decimal places

## Limitations

- **API Limits**: YouTube API has daily quota limits
- **Comment Availability**: Only works with videos that have comments enabled
- **Language**: Currently optimized for English comments
- **Sample Size**: Analysis limited to available comments (max ~100 per request cycle)

## Potential Improvements

- Add support for multiple languages
- Implement caching to reduce API calls
- Add more sophisticated sentiment analysis models
- Include comment like/dislike ratios in rating calculation
- Add data visualization for sentiment distribution
- Implement user authentication and history tracking

## Troubleshooting

**Common Issues:**

1. **Invalid Video ID Error**: Ensure the YouTube URL is properly formatted and the video is public
2. **API Key Errors**: Verify your YouTube API key is valid and has proper permissions
3. **Module Import Errors**: Ensure all required packages are installed
4. **NLTK Data Missing**: Run the NLTK download commands mentioned in installation

## License

This project is open source. Please ensure compliance with YouTube's Terms of Service when using their API.

## Contributing

Feel free to fork this project and submit pull requests for improvements or bug fixes.