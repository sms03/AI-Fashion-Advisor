import os
import random
from dotenv import load_dotenv
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
import uvicorn
from PIL import Image
import io
from openai import OpenAI
import google.generativeai as genai
from pydantic import BaseModel
from typing import Optional, Dict, Any
import base64
import time
import requests
import replicate

# Load environment variables
load_dotenv()

# Configure API keys
openai_api_key = os.getenv("OPENAI_API_KEY")
gemini_api_key = os.getenv("GEMINI_API_KEY")
replicate_api_key = os.getenv("REPLICATE_API_KEY")

# Initialize OpenAI client (new SDK style)
openai_client = OpenAI(api_key=openai_api_key) if openai_api_key else None

# Initialize Replicate client
replicate_client = replicate.Client(api_token=replicate_api_key) if replicate_api_key else None

# Configure Gemini API
if gemini_api_key:
    try:
        genai.configure(api_key=gemini_api_key)
        # Test the API key validity by making a minimal request
        models = genai.list_models()
        print("Gemini API key is valid.")
    except Exception as e:
        print(f"Gemini API key validation failed: {str(e)}")
        gemini_api_key = None  # Invalidate the key if it doesn't work

# Create FastAPI app with metadata for documentation
app = FastAPI(
    title="Fashion Advisor API",
    description="AI-powered fashion advice API using Google Gemini and OpenAI DALL-E",
    version="1.0.0",
    docs_url="/api/docs",
    redoc_url="/api/redoc",
)

# Ensure the generated_images directory exists
generated_images_dir = os.path.join(os.path.dirname(__file__), "generated_images")
os.makedirs(generated_images_dir, exist_ok=True)

# Mount static files directory for serving generated images
app.mount("/generated-images", StaticFiles(directory=generated_images_dir), name="generated-images")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Adjust in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class FashionResponse(BaseModel):
    text_advice: str
    image_url: Optional[str] = None


# Define helper functions outside the endpoint functions
async def get_fashion_advice_gemini(image_base64: str, scenario: str):
    """Get fashion advice using Google's Gemini API"""
    try:
        # Configure the model - updated to use gemini-1.5-flash
        model = genai.GenerativeModel('gemini-1.5-flash')
        
        # Create image part from base64
        image_data = {
            "mime_type": "image/jpeg",
            "data": image_base64
        }
        
        # Generate fashion advice
        prompt = f"""
        You are a professional fashion advisor. Analyze this clothing/outfit image.
        
        User scenario: {scenario}
        
        Provide detailed fashion advice including:
        1. Style assessment of the current outfit
        2. Recommendations for improvements or alternatives
        3. Suggestions for accessories, colors, or styling tips
        4. Occasion appropriateness
        
        Be specific and personalized in your advice.
        """
        
        response = model.generate_content([prompt, image_data])
        return response.text
    
    except Exception as e:
        print(f"Error with Gemini API: {str(e)}")
        # Fallback text if API fails
        return "We couldn't analyze your fashion image at this time. Please try again later."


async def generate_fashion_image(fashion_advice: str):
    """Generate a fashion suggestion image using Replicate or OpenAI based on Gemini's fashion advice"""
    try:
        # Create a concise prompt for the image generation from the fashion advice
        max_prompt_length = 800
        refined_prompt = f"Create a professional photograph showing a fashion outfit based on this advice: {fashion_advice[:max_prompt_length]}"
        if len(refined_prompt) > max_prompt_length:
            # Extract key fashion elements from the advice
            common_fashion_terms = [
                "dress", "suit", "formal", "casual", "business", "professional", 
                "shirt", "blouse", "skirt", "pants", "trousers", "jeans", 
                "jacket", "blazer", "coat", "sweater", "cardigan", "shoes",
                "accessories", "jewelry", "elegant", "stylish", "modern", "classic"
            ]
            colors = [
                "red", "blue", "green", "yellow", "black", "white", "grey", "gray",
                "purple", "pink", "orange", "brown", "navy", "teal", "maroon", "beige"
            ]
            extracted_terms = []
            for term in common_fashion_terms:
                if term in fashion_advice.lower():
                    extracted_terms.append(term)
            for color in colors:
                if color in fashion_advice.lower():
                    extracted_terms.append(color)
            if extracted_terms:
                style_description = " ".join(extracted_terms)
                refined_prompt = f"Create a professional fashion photograph showing an outfit with: {style_description}"
            else:
                refined_prompt = "Create a professional fashion photograph showing a stylish outfit suitable for various occasions"
        
        print(f"Generating image with prompt: {refined_prompt[:100]}...")
        
        # Try Replicate flux-schnell model first
        if replicate_client and replicate_api_key:
            try:
                print("Attempting to generate image with Replicate flux-schnell model...")
                output = replicate.run(
                    "black-forest-labs/flux-schnell:1c27155af5f3a2add89abe3a2f2dce21522f3a15f125a955d2805251d75533ef",
                    input={
                        "prompt": refined_prompt,
                        "negative_prompt": "deformed, bad anatomy, disfigured, poorly drawn face, mutation, mutated, extra limbs, ugly, poorly drawn hands, low resolution, blurry",
                        "num_inference_steps": 30,
                        "guidance_scale": 7.5,
                        "width": 1024,
                        "height": 1024,
                        "seed": random.randint(1, 10000000)
                    }
                )
                
                if output and isinstance(output, list) and len(output) > 0:
                    print("Successfully generated image with Replicate flux-schnell model")
                    return output[0]  # Return the URL of the generated image
            except Exception as e:
                print(f"Error with Replicate flux-schnell generation: {str(e)}")
        
        # If Replicate fails or is not configured, try OpenAI models
        if not openai_client or not openai_api_key:
            print("OpenAI API key not configured, and Replicate failed or not configured")
            return None
            
        # Try each OpenAI model with its specific parameters
        # 1. Try gpt-image-1 first
        try:
            print("Attempting to generate image with gpt-image-1...")
            response = openai_client.images.generate(
                model="gpt-image-1",
                prompt=refined_prompt,
                n=1,
                size="1024x1024",
                quality="high"
            )
            if response and response.data and len(response.data) > 0:
                print("Successfully generated image with gpt-image-1")
                return response.data[0].url
        except Exception as e:
            print(f"Error with OpenAI gpt-image-1 generation: {str(e)}")
            
            # 2. Try Stability AI's API
            stability_api_key = os.getenv("STABILITY_API_KEY")
            if stability_api_key:
                try:
                    print("Attempting to generate image with Stability AI...")
                    stability_url = "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image"
                    stability_headers = {
                        "Content-Type": "application/json",
                        "Accept": "application/json",
                        "Authorization": f"Bearer {stability_api_key}"
                    }
                    stability_payload = {
                        "text_prompts": [{"text": refined_prompt}],
                        "cfg_scale": 7,
                        "height": 1024,
                        "width": 1024,
                        "samples": 1,
                        "steps": 30
                    }
                    
                    stability_response = requests.post(
                        stability_url,
                        headers=stability_headers,
                        json=stability_payload
                    )
                    
                    if stability_response.status_code == 200:
                        data = stability_response.json()
                        if data and 'artifacts' in data and len(data['artifacts']) > 0:
                            image_b64 = data['artifacts'][0]['base64']
                            print("Successfully generated image with Stability AI")
                            img_data = base64.b64decode(image_b64)
                            img = Image.open(io.BytesIO(img_data))
                            filename = f"stability_{int(time.time())}.png"
                            temp_path = os.path.join(generated_images_dir, filename)
                            img.save(temp_path)
                            return f"http://localhost:8000/generated-images/{filename}"
                except Exception as stability_error:
                    print(f"Error with Stability AI generation: {str(stability_error)}")
            
            # 3. Try Nebius AI's API
            nebius_api_key = os.getenv("NEBIUS_API_KEY")
            nebius_folder_id = os.getenv("NEBIUS_FOLDER_ID")
            if nebius_api_key and nebius_folder_id:
                try:
                    print("Attempting to generate image with Nebius AI...")
                    nebius_url = "https://llm.api.cloud.nebius.ai/foundationModels/v1/generation"
                    nebius_headers = {
                        "Content-Type": "application/json",
                        "Authorization": f"Api-Key {nebius_api_key}",
                        "x-folder-id": nebius_folder_id
                    }
                    nebius_payload = {
                        "modelUri": "kandinsky-3",
                        "parameters": {
                            "prompt": refined_prompt,
                            "negative_prompt": "deformed, bad anatomy, disfigured, poorly drawn face, mutated, ugly, poorly drawn hands",
                            "num_steps": 30,
                            "width": 1024,
                            "height": 1024,
                            "num_images": 1
                        }
                    }
                    
                    nebius_response = requests.post(
                        nebius_url,
                        headers=nebius_headers,
                        json=nebius_payload
                    )
                    
                    if nebius_response.status_code == 200:
                        data = nebius_response.json()
                        if data and 'images' in data and len(data['images']) > 0:
                            image_b64 = data['images'][0]
                            print("Successfully generated image with Nebius AI")
                            img_data = base64.b64decode(image_b64)
                            img = Image.open(io.BytesIO(img_data))
                            filename = f"nebius_{int(time.time())}.png"
                            temp_path = os.path.join(generated_images_dir, filename)
                            img.save(temp_path)
                            return f"http://localhost:8000/generated-images/{filename}"
                except Exception as nebius_error:
                    print(f"Error with Nebius AI generation: {str(nebius_error)}")
                    if 'nebius_response' in locals():
                        print(f"Nebius API response: {nebius_response.text if nebius_response else 'No response'}")
            
            # 4. Fallback to DALL-E 3 if previous options fail
            try:
                print("Attempting to generate image with DALL-E 3...")
                response = openai_client.images.generate(
                    model="dall-e-3",
                    prompt=refined_prompt,
                    n=1,
                    size="1024x1024"
                )
                if response and response.data and len(response.data) > 0:
                    print("Successfully generated image with DALL-E 3")
                    return response.data[0].url
            except Exception as e2:
                print(f"Error with DALL-E 3 fallback: {str(e2)}")
                # 5. Fallback to DALL-E 2 as last resort
                try:
                    print("Attempting to generate image with DALL-E 2...")
                    response = openai_client.images.generate(
                        model="dall-e-2",
                        prompt="professional fashion outfit",
                        n=1,
                        size="1024x1024"
                    )
                    if response and response.data and len(response.data) > 0:
                        print("Successfully generated image with DALL-E 2")
                        return response.data[0].url
                except Exception as e3:
                    print(f"Error with DALL-E 2 fallback: {str(e3)}")
        print("All image generation attempts failed")
        return None
    except Exception as e:
        print(f"Error in generate_fashion_image: {str(e)}")
        return None


@app.get("/", response_class=HTMLResponse)
async def root():
    """Redirect to the API documentation"""
    return RedirectResponse(url="/api/docs")


@app.get("/api", response_class=HTMLResponse)
async def api_info():
    """API information page"""
    return """
    <html>
        <head>
            <title>Fashion Advisor API</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
                h1 { color: #333; }
                a { color: #0066cc; }
                .endpoint { background: #f4f4f4; padding: 10px; margin: 10px 0; border-radius: 5px; }
                .warning { color: #cc0000; }
            </style>
        </head>
        <body>
            <h1>AI Fashion Advisor API</h1>
            <p>Welcome to the Fashion Advisor API! This service provides AI-powered fashion advice.</p>
            
            <h2>Available Endpoints:</h2>
            <div class="endpoint">
                <h3>POST /api/analyze</h3>
                <p>Upload an image and get fashion advice</p>
            </div>
            <div class="endpoint">
                <h3>GET /api/health</h3>
                <p>Check if the API is running</p>
            </div>
            <div class="endpoint">
                <h3>GET /api/config-status</h3>
                <p>Check if API keys are configured</p>
            </div>
            
            <h2>Documentation:</h2>
            <p><a href="/api/docs">Swagger UI Documentation</a></p>
            <p><a href="/api/redoc">ReDoc Documentation</a></p>
        </body>
    </html>
    """


@app.get("/api/config-status")
async def config_status():
    """Check if API keys are properly configured"""
    status = {
        "openai": bool(openai_api_key),
        "gemini": bool(gemini_api_key),
        "replicate": bool(replicate_api_key),
        "all_configured": bool(openai_api_key and gemini_api_key and replicate_api_key)
    }
    return status


@app.post("/api/analyze", response_model=FashionResponse)
async def analyze_fashion(
    file: UploadFile = File(...),
    scenario: str = Form(...)
):
    """
    Analyze a fashion image and provide advice
    
    - **file**: Image file of the outfit/clothing to analyze
    - **scenario**: Description of the scenario or occasion (e.g., job interview, date night)
    
    Returns fashion advice text and a suggested outfit image
    """
    # Validate image
    if not file.content_type.startswith("image/"):
        raise HTTPException(400, "File must be an image")
    
    # Check API keys
    if not gemini_api_key:
        missing = []
        if not gemini_api_key:
            missing.append("Gemini")
        raise HTTPException(500, f"Missing API key(s): {', '.join(missing)}. Please configure your .env file.")
    
    try:
        # Read and process the image
        image_content = await file.read()
        image = Image.open(io.BytesIO(image_content))
        
        # Convert to base64 for API use
        buffered = io.BytesIO()
        image.save(buffered, format="JPEG")
        img_str = base64.b64encode(buffered.getvalue()).decode()
        
        # Get text advice from Gemini
        text_advice = await get_fashion_advice_gemini(img_str, scenario)
        
        # Generate fashion suggestion image
        image_url = await generate_fashion_image(text_advice)
        
        # Ensure we're returning a valid response object
        if not text_advice:
            text_advice = "Could not generate fashion advice at this time."
        
        response = FashionResponse(
            text_advice=text_advice,
            image_url=image_url
        )
        
        return response
    
    except Exception as e:
        print(f"Error in analyze_fashion: {str(e)}")
        # Return a fallback response rather than raising an exception
        fallback_response = FashionResponse(
            text_advice="We encountered an error analyzing your image. Please try again later.",
            image_url=None
        )
        return fallback_response


@app.get("/api/health")
async def health_check():
    """Health check endpoint that returns the current status and timestamp"""
    return {"status": "ok", "timestamp": time.time()}


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)