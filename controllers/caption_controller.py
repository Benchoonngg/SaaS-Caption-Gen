from flask import jsonify
from models.user import User, db
from api import generate_caption

class CaptionController:
    @staticmethod
    def generate(user_id: int, prompt: str):
        """
        Handle caption generation request
        """
        try:
            # Get user
            user = User.query.get(user_id)
            if not user:
                return jsonify({"error": "User not found"}), 404
            
            # Check credits
            if user.credits <= 0:
                return jsonify({"error": "Insufficient credits"}), 400
            
            # Generate caption
            caption = generate_caption(prompt)
            if not caption:
                return jsonify({"error": "Failed to generate caption"}), 500
            
            # Deduct credit
            user.credits -= 1
            db.session.commit()
            
            # Return formatted response
            return jsonify({
                "caption": caption,
                "credits_remaining": user.credits,
                "status": "success"
            }), 200
            
        except Exception as e:
            db.session.rollback()
            return jsonify({
                "error": str(e),
                "status": "error"
            }), 500 