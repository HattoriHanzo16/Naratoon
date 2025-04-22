import os
from openai import OpenAI
from typing import List, Dict
import json
from dotenv import load_dotenv
from pathlib import Path
import time
import random
import requests
import uuid
import shutil

# Get the absolute path to the .env file
env_path = Path(__file__).parent.parent.parent / '.env'

# Load the environment variables from the specific path
load_dotenv(dotenv_path=env_path)

# Get the API key
api_key = os.getenv("OPENAI_API_KEY")

if not api_key:
    raise ValueError(f"OPENAI_API_KEY not found in environment variables. Looked in: {env_path}")

client = OpenAI(api_key=api_key)

# Create images directory if it doesn't exist
IMAGES_DIR = Path(__file__).parent.parent.parent / 'static' / 'images'
IMAGES_DIR.mkdir(parents=True, exist_ok=True)

# Base URL for accessing saved images
BASE_IMAGE_URL = "/static/images/"

class StoryService:
    @staticmethod
    def analyze_story(story_text: str) -> List[Dict]:
        """Analyze story text and break it down into scenes with descriptions and text content using GPT-4."""
        try:
            # Add retry logic for rate limits
            max_retries = 3
            base_delay = 2  # seconds
            
            for attempt in range(max_retries):
                try:
                    response = client.chat.completions.create(
                        model="gpt-4o", 
                        response_format={ "type": "json_object" },
                        messages=[
                            {"role": "system", "content": """You are a comic script writer. Break down the provided story into 8-10 sequential comic panels. 
                            For each panel, you MUST provide:
                            1. `visual_description`: A concise description of the scene and action for an image generation model. Focus on visual elements ONLY.
                            2. `panel_text`: The text content (dialogue in quotes, captions, or sound effects in uppercase). This field is MANDATORY and must not be empty. Keep it brief.
                            Return the result as a JSON object with a single key "panels" containing an array of these panel objects."""},
                            {"role": "user", "content": f"Break this story into 8-10 comic panels, providing visual descriptions and MANDATORY text for each panel:\n\n{story_text}"}
                        ]
                    )
                    break  # Success, exit retry loop
                except Exception as e:
                    # Check if this is a rate limit error
                    if "429" in str(e) or "rate limit" in str(e).lower():
                        if attempt < max_retries - 1:  # Don't sleep on the last attempt
                            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                            print(f"Rate limit hit, retrying in {delay:.2f} seconds... (Attempt {attempt+1}/{max_retries})")
                            time.sleep(delay)
                        else:
                            raise  # Re-raise on last attempt
                    else:
                        raise  # Re-raise if not a rate limit error
            
            # Process the response and return structured panel data
            structured_data = json.loads(response.choices[0].message.content)
            panels = structured_data.get("panels", [])
            
            # --- DEBUGGING: Print parsed panels --- 
            print("DEBUG: Parsed panels from LLM:", panels)
            # --- END DEBUGGING ---

            if not panels or not isinstance(panels, list):
                 print("ERROR: Failed to parse panels or panels list is empty.") # Added print
                 raise ValueError("Failed to parse panels from LLM response.")

            # Limit to 10 panels maximum
            return panels[:10] # Increased limit to 10
        except json.JSONDecodeError as json_err:
            print(f"ERROR: JSONDecodeError - {json_err}. Response: {response.choices[0].message.content if response and response.choices else 'No response'}") # Added print
            raise Exception(f"Error decoding JSON from LLM response: {json_err}")
        except Exception as e:
            print(f"ERROR: Exception in analyze_story - {str(e)}") # Added print
            raise Exception(f"Error analyzing story: {str(e)}")

    @staticmethod
    def generate_panel(visual_description: str) -> str: 
        """Generate a comic panel image using DALL-E based on visual description."""
        # Add retry logic for rate limits
        max_retries = 3
        base_delay = 2  # seconds
        
        for attempt in range(max_retries):
            try:
                # Limit description length to avoid exceeding API limits
                truncated_desc = visual_description[:500] if visual_description else "Comic panel scene"
                
                # Make prompt more DALL-E friendly and avoid potential policy violations
                safe_prompt = f"Comic panel illustration: {truncated_desc}. Style: classic comic book art, clear lines, vibrant colors. Avoid rendering text directly in the image."
                
                # Log actual prompt for debugging
                print(f"DEBUG: DALL-E Prompt: {safe_prompt}")
                
                response = client.images.generate(
                    model="dall-e-3",
                    prompt=safe_prompt,
                    n=1,
                    size="1024x1024"
                )
                
                # Get the image URL from DALL-E
                dalle_url = response.data[0].url
                
                # Download and save the image locally
                return StoryService.download_and_save_image(dalle_url)
            except Exception as e:
                # Check if this is a rate limit error
                if "429" in str(e) or "rate limit" in str(e).lower():
                    if attempt < max_retries - 1:  # Don't sleep on the last attempt
                        delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
                        print(f"Rate limit hit in DALL-E, retrying in {delay:.2f} seconds... (Attempt {attempt+1}/{max_retries})")
                        time.sleep(delay)
                    else:
                        print(f"All DALL-E retries failed: {str(e)}")
                        # Return a placeholder image path
                        return BASE_IMAGE_URL + "placeholder-rate-limit.png"
                else:
                    print(f"ERROR: Exception in generate_panel - {str(e)}")
                    # For non-rate limit errors, return a placeholder immediately
                    return BASE_IMAGE_URL + "placeholder-error.png"
        
        # This should never be reached due to the return statements above, but as a fallback
        return BASE_IMAGE_URL + "placeholder-unexpected.png"
    
    @staticmethod
    def download_and_save_image(image_url: str) -> str:
        """Download an image from a URL and save it to the local filesystem."""
        try:
            # Generate a unique filename
            filename = f"{uuid.uuid4()}.png"
            filepath = IMAGES_DIR / filename
            
            # Download the image
            response = requests.get(image_url, stream=True, timeout=30)
            
            # Check if the request was successful
            if response.status_code == 200:
                # Save the image to disk
                with open(filepath, 'wb') as f:
                    response.raw.decode_content = True
                    shutil.copyfileobj(response.raw, f)
                
                # Return the URL path to access the image
                return f"{BASE_IMAGE_URL}{filename}"
            else:
                print(f"Failed to download image: HTTP status {response.status_code}")
                return BASE_IMAGE_URL + "placeholder-download-error.png"
        except Exception as e:
            print(f"Error downloading image: {str(e)}")
            return BASE_IMAGE_URL + "placeholder-download-error.png"

    @staticmethod
    def process_story(story_text: str) -> List[Dict]:
        """Process the entire story and generate comic panels with text and images."""
        # Create placeholder images if they don't exist
        StoryService.ensure_placeholder_images_exist()
        
        panels_data = StoryService.analyze_story(story_text) 
        comic_panels_output = []
        
        for i, panel_info in enumerate(panels_data):
            try:
                visual_desc = panel_info.get("visual_description", "Default scene") 
                panel_text_content = panel_info.get("panel_text", "") 

                # --- Check for empty text --- 
                if not panel_text_content:
                    print(f"WARNING: Panel {i+1} has empty panel_text_content. Panel Info: {panel_info}")
                # --- End Check ---
                
                if not visual_desc:
                     print(f"WARNING: Missing visual description for panel {i+1}. Using fallback. Panel Info: {panel_info}")
                     visual_desc = "Abstract comic panel" 

                image_url = StoryService.generate_panel(visual_desc) 

                comic_panels_output.append({
                    "panel_number": i + 1,
                    "scene_description": visual_desc, 
                    "panel_text": panel_text_content, 
                    "image_url": image_url
                })
            except Exception as e:
                print(f"ERROR: Failed to process panel {i+1}: {str(e)}")
                # Add a fallback panel instead of failing the whole process
                comic_panels_output.append({
                    "panel_number": i + 1,
                    "scene_description": "Error generating panel",
                    "panel_text": panel_text_content or "Error occurred", 
                    "image_url": BASE_IMAGE_URL + "placeholder-panel-error.png"
                })
        
        return comic_panels_output
        
    @staticmethod
    def ensure_placeholder_images_exist():
        """Create placeholder images if they don't exist."""
        placeholders = {
            "placeholder-rate-limit.png": "Rate Limit Exceeded",
            "placeholder-error.png": "Image Generation Failed",
            "placeholder-unexpected.png": "Unexpected Error",
            "placeholder-download-error.png": "Image Download Failed",
            "placeholder-panel-error.png": "Panel Generation Failed"
        }
        
        for filename, text in placeholders.items():
            filepath = IMAGES_DIR / filename
            if not filepath.exists():
                StoryService.create_placeholder_image(filepath, text)
    
    @staticmethod
    def create_placeholder_image(filepath, text):
        """Create a simple placeholder image with text."""
        try:
            # Use PIL to create a simple placeholder image
            from PIL import Image, ImageDraw, ImageFont
            
            # Create a gray image
            img = Image.new('RGB', (512, 512), color=(200, 200, 200))
            d = ImageDraw.Draw(img)
            
            # Try to use a default font
            try:
                font = ImageFont.truetype("Arial", 24)
            except:
                font = ImageFont.load_default()
            
            # Draw the text
            d.text((256, 256), text, fill=(50, 50, 50), font=font, anchor="mm")
            
            # Save the image
            img.save(filepath)
        except Exception as e:
            print(f"Failed to create placeholder image: {str(e)}")
            # Create a minimal placeholder if PIL fails
            with open(filepath, 'w') as f:
                f.write("Placeholder Image") 