from flask import jsonify
from models.user import User, db
from api import generate_caption
import logging

class CaptionController:
    @staticmethod
    def generate(user_id: int, prompt: str):
        logging.debug(f"CaptionController.generate called with user_id: {user_id}, prompt: {prompt}")
        """
        Handle caption generation request
        """
        try:
            # Get user
            user = User.query.get(user_id)
            if not user:
                logging.error(f"User not found: {user_id}")
                return jsonify({"error": "User not found"}), 404
            
            # Check credits
            if user.credits <= 0:
                logging.error(f"Insufficient credits for user: {user_id}")
                return jsonify({"error": "Insufficient credits"}), 400
            
            # Generate caption
            logging.debug("Calling generate_caption from API")
            caption = generate_caption(prompt)
            logging.debug(f"Received caption from API: {caption}")
            
            if not caption:
                logging.error("Failed to generate caption")
                return jsonify({"error": "Failed to generate caption"}), 500
            
            # Deduct credit
            user.credits -= 1
            db.session.commit()
            logging.debug(f"Updated credits for user {user_id}: {user.credits}")
            
            # Return formatted response
            response = {
                "caption": caption,
                "credits_remaining": user.credits,
                "status": "success"
            }
            logging.debug(f"Returning response: {response}")
            return jsonify(response), 200
            
        except Exception as e:
            logging.error(f"Error in CaptionController.generate: {str(e)}")
            db.session.rollback()
            return jsonify({
                "error": str(e),
                "status": "error"
            }), 500 