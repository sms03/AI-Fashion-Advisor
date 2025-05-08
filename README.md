# AI Fashion Advisor

An AI-powered application that provides fashion advice based on uploaded images and context scenarios. The application uses multiple AI services including Google's Gemini API for text analysis, OpenAI's DALL-E, Replicate, and Stability AI for generating fashion suggestion images.

## Features

- Upload outfit images for analysis
- Provide context scenarios (e.g., job interview, date night, casual outing)
- Get AI-generated fashion advice based on your image and scenario
- View AI-generated outfit suggestions as images

## Project Structure

```
AI-Fashion-Advisor/
├── backend/               # Python FastAPI backend
│   ├── main.py           # Main server file
│   ├── requirements.txt  # Python dependencies
│   ├── .env.example     # Example environment variables
│   └── generated_images/ # AI-generated image outputs
├── frontend/             # React TypeScript frontend
    ├── src/             # Source code
    │   ├── components/  # React components
    │   ├── services/    # API services
    │   └── assets/      # Static assets
    ├── public/          # Public assets
    └── package.json     # Node dependencies
```

## Prerequisites

- Python 3.9+
- Node.js 18+ with pnpm package manager
- API keys for:
  - Google Gemini API
  - OpenAI API
  - Replicate API
  - Stability AI API

## Setup and Installation

### Backend Setup

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```

2. Install dependencies using pip:
   ```sh
   pip install -r requirements.txt
   ```

3. Copy the `.env.example` file to `.env` and add your API keys:
   ```sh
   cp .env.example .env
   ```
   Then edit the `.env` file to add your API keys:
   - OPENAI_API_KEY
   - GEMINI_API_KEY
   - REPLICATE_API_TOKEN
   - STABILITY_API_KEY

4. Start the backend server:
   ```sh
   python main.py
   ```
   The backend will run on http://localhost:8000

### Frontend Setup

1. Navigate to the frontend directory:
   ```sh
   cd frontend
   ```

2. Install dependencies using pnpm:
   ```sh
   pnpm install
   ```

3. Start the frontend development server:
   ```sh
   pnpm dev
   ```
   The frontend will run on http://localhost:5173

## Usage

1. Open your browser and navigate to http://localhost:5173
2. Upload an image of your outfit using the drag-and-drop interface or file selector
3. Describe the scenario or occasion in the text area (e.g., "Job interview at a tech company")
4. Click "Get Fashion Advice"
5. View the AI-generated fashion analysis and suggested outfit image

## API Endpoints

- `GET /api/health` - Health check endpoint
- `POST /api/analyze` - Analyze fashion from an image and scenario
- `GET /api/config-status` - Check API configuration status

## Technologies Used

### Backend
- FastAPI - Web framework
- Python - Programming language
- Google Gemini API - Text analysis
- OpenAI DALL-E - Image generation
- Replicate - AI models
- Stability AI - Image generation

### Frontend
- React - UI library
- TypeScript - Programming language
- Tailwind CSS - Styling
- Vite - Build tool
- Axios - HTTP client