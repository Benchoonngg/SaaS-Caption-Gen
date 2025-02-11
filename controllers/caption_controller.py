from flask import jsonify
from models.user import User, db
from api import generate_caption
import logging

class CaptionController:
    # Update instruction categories mapping to match exactly with frontend values
    instruction_categories = {
        "Tip Me": "Generate a Tip Me Caption",
        "Winner": "Generate a Winner Caption",
        "Holiday": "Generate a Holiday Caption",
        "Bundle": "Generate a Bundle Caption",
        "Descriptive": "Generate a Descriptive Caption",
        "Spin the Wheel": "Generate a Spin the Wheel Caption",
        "Girlfriend Non-Explicit": "Generate a Girlfriend Non-Explicit Caption",
        "Girlfriend Explicit": "Generate a Girlfriend Explicit Caption",
        "List": "Generate a List Caption",
        "Short": "Generate a Short Caption",
        "Sub Promo": "Generate a Sub Promo Caption",
        "VIP": "Generate a VIP Caption"
    }

    @staticmethod
    def generate(user_id: int, prompt: str, category: str):
        try:
            # Add debug logging for category
            logging.debug(f"Received category: '{category}'")
            logging.debug(f"Available categories: {list(CaptionController.instruction_categories.keys())}")
            
            # Get user
            user = User.query.get(user_id)
            if not user:
                return {"error": "User not found"}, 404
            
            if user.credits <= 0:
                return {"error": "No credits remaining"}, 400

            # Get the full instruction for the category
            instruction = CaptionController.instruction_categories.get(category.strip())  # Add strip()
            if not instruction:
                return {"error": f"Invalid category: '{category}'"}, 400

            # Format the prompt with detailed instruction
            formatted_prompt = f"### Instruction:\n{instruction}\n\n### Input:\n{prompt}\n\n### Response:\n"
            
            logging.debug(f"Formatted prompt: {formatted_prompt}")
            
            # Generate caption using the API
            caption = generate_caption(formatted_prompt)
            
            if caption:
                # Deduct credit
                user.credits -= 1
                db.session.commit()
                
                return {
                    "caption": caption,
                    "credits_remaining": user.credits
                }
            else:
                return {"error": "Failed to generate caption"}, 500
                
        except Exception as e:
            logging.error(f"Error in CaptionController.generate: {str(e)}")
            return {"error": str(e)}, 500 