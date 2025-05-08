# AI Fashion Advisor

An AI-powered application that provides fashion advice based on uploaded images and context scenarios. The application uses Google's Gemini API for text analysis and OpenAI's DALL-E for generating fashion suggestion images.

## Features

- Upload outfit images for analysis
- Provide context scenarios (e.g., job interview, date night, casual outing)
- Get AI-generated fashion advice based on your image and scenario
- View AI-generated outfit suggestions as images

## Project Structure

```
Fashion-Advisor/
├── backend/               # Python FastAPI backend
│   ├── main.py            # Main server file
│   ├── requirements.txt   # Python dependencies
│   └── .env.example       # Example environment variables
├── frontend/              # React TypeScript frontend
    ├── src/               # Source code
    ├── public/            # Static assets
    └── package.json       # Node dependencies
```

## Prerequisites

- Python 3.9+ with uv package manager
- Node.js 18+ with pnpm package manager
- API keys for:
  - Google Gemini API
  - OpenAI API

## Setup and Installation

### Backend Setup

1. Navigate to the backend directory:
   ```sh
   cd backend
   ```

2. Create a virtual environment and install dependencies using uv:
   ```sh
   uv venv
   uv pip install -r requirements.txt
   ```

3. Copy the `.env.example` file to `.env` and add your API keys:
   ```sh
   cp .env.example .env
   ```
   Then edit the `.env` file to add your actual API keys.

4. Start the backend server:
   ```sh
   uvicorn main:app --reload
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

## Technologies Used

### Backend
- FastAPI - Web framework
- Python - Programming language
- Google Gemini API - Text analysis
- OpenAI DALL-E - Image generation

### Frontend
- React - UI library
- TypeScript - Programming language
- Chakra UI - Component library
- Axios - HTTP client
- React Router - Navigation
- React Dropzone - File uploads