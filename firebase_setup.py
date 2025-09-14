# firebase_setup.py
import firebase_admin
from firebase_admin import credentials, auth

# Initialize Firebase Admin SDK once
try:
    # firebase_setup.py
    cred = credentials.Certificate("C:/Users/neire/OneDrive/Documents/Seneca-Hacks/seneca-95937-firebase-adminsdk-fbsvc-e560fe24c9.json")
    firebase_admin.initialize_app(cred)
except ValueError:
    # App is already initialized
    pass

def get_user_id_from_token(id_token: str):
    """Verifies the Firebase ID token and returns the user's UID."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token['uid'], decoded_token.get('premium', False)
    except auth.AuthError as e:
        print(f"AuthError: {e}")
        return None

def get_user_tier(user_id: str):
    """Fetches user tier from custom claims."""
    try:
        user = auth.get_user(user_id)
        return user.custom_claims.get('tier', 'standard')
    except auth.AuthError as e:
        print(f"Error fetching user: {e}")
        return None
def set_premium_claim(user_id: str):
    try:
        # Get the current custom claims
        user = auth.get_user(user_id)
        current_claims = user.custom_claims or {}

        # Set the 'premium' claim to True
        updated_claims = {**current_claims, 'premium': True}

        # Set the custom claims on the user
        auth.set_custom_user_claims(user_id, updated_claims)
        print(f"Custom claim 'premium' set to True for user {user_id}")
    except Exception as e:
        print(f"Error setting custom claim: {e}")