import os
# import sys
# from supabase.lib.client_options import ClientOptions
# import httpx
# from supabase import create_client

# --- CRITICAL FIX FOR CPANEL + SUPABASE ---
# cPanel injects proxy env vars that break gotrue/httpx
# for key in (
#     "HTTP_PROXY",
#     "HTTPS_PROXY",
#     "http_proxy",
#     "https_proxy",
#     "ALL_PROXY",
#     "all_proxy",
#     "NO_PROXY",
#     "no_proxy",
# ):
#     os.environ.pop(key, None)
    
# sys.path.insert(0, os.path.dirname(__file__))



# Explicitly tell httpx to ignore environment proxies
# os.environ["HTTPX_NO_PROXY"] = "*"

from supabase import create_client
from dotenv import load_dotenv
# import os

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_SERVICE_ROLE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase credentials not set")
    
if SUPABASE_KEY:
    SUPABASE_KEY = SUPABASE_KEY.strip()

# ✅ One global Supabase client (SUPPORTED API)
supabase = create_client(SUPABASE_URL, SUPABASE_KEY)


# import httpx
# from supabase import create_client

# _supabase = None

# def get_supabase():
#     global _supabase
#     if _supabase is None:
#         http_client = httpx.Client(trust_env=False)
#         _supabase = create_client(
#             SUPABASE_URL,
#             SUPABASE_KEY,
#             options={
#                 "http_client": http_client
#             }
#         )
#     return _supabase


def save_review(business_id, name, rating, comment):
    supabase.table("reviews").insert({
        "business_id": business_id,
        "customer_name": name,
        "rating": rating,
        "comment": comment
    }).execute()

def get_reviews(business_id):
    return supabase.table("reviews").select("*").eq("business_id", business_id).execute().data

def get_business(business_id):
    return supabase.table("businesses").select("*").eq("id", business_id).single().execute().data

def get_all_businesses():
    return supabase.table("businesses").select("*").execute().data

def save_business(name, google_review_link):
    """Save a new business to the database - extract Place ID from Google Maps link"""
    import re
    
    # Extract Place ID from Google Maps URL
    google_place_id = extract_place_id_from_url(google_review_link)
    
    return supabase.table("businesses").insert({
        "name": name,
        "google_place_id": google_place_id,
        "google_review_link": google_review_link
    }).execute()

def extract_place_id_from_url(google_maps_url):
    """Extract Google Place ID from various Google Maps URL formats"""
    import re
    import requests
    
    print(f"Original URL: {google_maps_url}")
    
    # If it's a shortened URL (goo.gl), follow the redirect to get the full URL
    if "goo.gl" in google_maps_url or "maps.app.goo.gl" in google_maps_url:
        try:
            response = requests.head(google_maps_url, allow_redirects=True, timeout=10)
            expanded_url = response.url
            print(f"Expanded URL: {expanded_url}")
            google_maps_url = expanded_url
        except Exception as e:
            print(f"Could not expand shortened URL: {e}")
            # Continue with original URL
    
    # Common Google Maps URL patterns that contain Place ID
    patterns = [
        # Standard Place ID (ChIJ format)
        r'place_id:([A-Za-z0-9_-]+)',  # ?q=place_id:ChIJ...
        r'data=.*?1s([A-Za-z0-9_-]+)',  # /data=...1sChIJ...
        r'ftid=([A-Za-z0-9_-]+)',       # ftid=ChIJ...
        
        # Hexadecimal location IDs
        r'data=.*?0x([a-fA-F0-9]+):0x([a-fA-F0-9]+)',  # Extract hex coordinates
        r'@[0-9.-]+,[0-9.-]+,[0-9.]+z/data=.*?0x([a-fA-F0-9]+)',  # Hex from coordinates
        
        # Numeric IDs
        r'ludocid=([0-9]+)',            # ludocid=12345... (numeric ID)
        r'cid=([0-9]+)',                # cid=12345... (numeric ID)
        
        # Place name patterns
        r'/place/[^/]+/([A-Za-z0-9_-]+)', # /place/Name/ChIJ...
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, google_maps_url)
        if match:
            if i == 3:  # Hex coordinates pattern - use second group
                place_id = "0x" + match.group(2)
            elif i == 4:  # Single hex pattern
                place_id = "0x" + match.group(1)
            else:
                place_id = match.group(1)
            
            print(f"Found Place ID using pattern {i+1}: {place_id}")
            
            # Validate the Place ID format
            if place_id.startswith('ChIJ') or place_id.startswith('0x') or place_id.isdigit():
                return place_id
    
    # If no Place ID found, try to extract from the business name in URL
    name_match = re.search(r'/place/([^/@]+)', google_maps_url)
    if name_match:
        business_name = name_match.group(1).replace('+', ' ')
        print(f"Could not extract Place ID, using business name: {business_name}")
        return business_name
    
    print(f"Could not extract Place ID from URL: {google_maps_url}")
    return ""
    
def convert_to_direct_review_link(google_maps_url):
    """Convert Google Maps URL to direct review page format like https://g.page/r/CSG4HF_UwszWEBE/review"""
    import re
    import requests
    
    print(f"Converting URL to direct review format: {google_maps_url}")
    
    # If it's already a g.page/r/ format, return as is
    if "g.page/r/" in google_maps_url and "/review" in google_maps_url:
        print(f"Already in direct review format: {google_maps_url}")
        return google_maps_url
    
    # If it's a shortened URL (goo.gl), follow the redirect to get the full URL
    if "goo.gl" in google_maps_url or "maps.app.goo.gl" in google_maps_url:
        try:
            response = requests.head(google_maps_url, allow_redirects=True, timeout=10)
            expanded_url = response.url
            print(f"Expanded URL: {expanded_url}")
            google_maps_url = expanded_url
        except Exception as e:
            print(f"Could not expand shortened URL: {e}")
            # Continue with original URL
    
    # Try to extract the short code from various Google Maps URL patterns
    patterns = [
        # g.page format without /review
        r'g\.page/r/([A-Za-z0-9_-]+)',
        # Google Maps data parameter patterns that might contain the short code
        r'data=.*?1s([A-Za-z0-9_-]{12,})',  # Look for longer alphanumeric codes
        r'ftid=([A-Za-z0-9_-]{12,})',       # Feature ID that might be the short code
        # Place ID patterns - these might work for g.page conversion
        r'place_id:([A-Za-z0-9_-]+)',
    ]
    
    for i, pattern in enumerate(patterns):
        match = re.search(pattern, google_maps_url)
        if match:
            potential_code = match.group(1)
            print(f"Found potential code using pattern {i+1}: {potential_code}")
            
            # For g.page format, we need a specific format code
            if i == 0:  # Already g.page format
                return f"https://g.page/r/{potential_code}/review"
            elif len(potential_code) >= 12:  # Reasonable length for g.page codes
                # Try to construct the direct review link
                direct_link = f"https://g.page/r/{potential_code}/review"
                print(f"Constructed direct review link: {direct_link}")
                return direct_link
    
    # If we can't extract a suitable code, try to find the business short code from the URL
    # Look for patterns like /place/Business+Name/@lat,lng,zoom/data=...
    place_match = re.search(r'/place/([^/@]+)', google_maps_url)
    if place_match:
        business_name = place_match.group(1).replace('+', ' ')
        print(f"Could not extract g.page code, business name: {business_name}")
        
        # Look for any alphanumeric code in the data parameter that could be the g.page code
        data_codes = re.findall(r'data=.*?([A-Za-z0-9_-]{12,})', google_maps_url)
        for code in data_codes:
            if len(code) >= 12 and len(code) <= 20:  # Reasonable g.page code length
                direct_link = f"https://g.page/r/{code}/review"
                print(f"Trying g.page code from data: {direct_link}")
                return direct_link
    
    # If all else fails, return the original URL with a note
    print(f"Could not convert to g.page format, returning original URL: {google_maps_url}")
    return google_maps_url

def delete_business(business_id):
    """Delete a business and all its reviews from the database"""
    try:
        # First, delete all reviews for this business
        print(f"Deleting reviews for business ID: {business_id}")
        reviews_result = supabase.table("reviews").delete().eq("business_id", business_id).execute()
        print(f"Deleted {len(reviews_result.data) if reviews_result.data else 0} reviews")
        
        # Then delete the business
        print(f"Deleting business with ID: {business_id}")
        business_result = supabase.table("businesses").delete().eq("id", business_id).execute()
        print(f"Business deletion result: {business_result}")
        
        return business_result
        
    except Exception as e:
        print(f"Error in delete_business: {str(e)}")
        raise e

def create_feedback_token(business_id, customer_name="", expires_in_minutes=2):
    """Create a temporary feedback token that expires after being opened for specified minutes"""
    import secrets
    import time
    import string
    import random
    
    # Generate a short, professional code (6 characters: letters and numbers)
    characters = string.ascii_letters + string.digits
    short_code = ''.join(random.choices(characters, k=6))
    
    # Also create the original long token for backward compatibility
    token = secrets.token_urlsafe(32)
    current_time = int(time.time())  # Convert to integer
    
    expires_at = current_time + (100 * 365 * 24 * 60 * 60)  # 100 years in seconds
    
    # NOTE: expires_at is now only used for cleanup of very old unopened tokens (24 hours)
    # The real expiry happens after first opening (stored in opened_expires_at)
    cleanup_expires_at = current_time + (24 * 60 * 60)  # 24 hours for cleanup
    
    try:
        # Store token in database with new fields
        supabase.table("feedback_tokens").insert({
            "token": token,
            "short_code": short_code,
            "business_id": business_id,
            "customer_name": customer_name,
            "expires_at": cleanup_expires_at,  # For cleanup only
            "used": False,
            "created_at": current_time,
            "first_opened_at": None,  # Will be set when first opened
            "opened_expires_at": None,  # Will be set when first opened
            "expires_at": expires_at
        }).execute()
        
        return {"token": token, "short_code": short_code, "expires_in_minutes": expires_in_minutes}
    except Exception as e:
        print(f"Error creating feedback token: {str(e)}")
        return None

# def validate_feedback_token(token_or_code, consume= Flase):
#     """
#     Validate a feedback token (supports both token and short_code)
#     Links are now completely lifelong and can be used multiple times
    
#     Args:
#         token_or_code: The token or short code to validate
#         consume: Kept for compatibility but ignored (tokens are never consumed)
        
#     """
    
    
#     try:
#         # Try to find by short_code first, then by token
#         result = None
        
#         # Check if it's a short code (6 characters) or long token
#         if len(token_or_code) == 6:
#             # It's a short code
#             result = supabase.table("feedback_tokens").select("*").eq("short_code", token_or_code).single().execute()
#         else:
#             # It's a long token
#             result = supabase.table("feedback_tokens").select("*").eq("token", token_or_code).single().execute()
        
#         if not result.data:
#             return None, "Invalid token"
        
#         token_data = result.data
        
        
#         # # Check if token is already used
#         # if token_data.get("used"):
#         #     return None, "Token already used"
        
#         # # Check expiry logic:
#         # # 1. If never opened, check against cleanup expiry (24 hours)
#         # # 2. If opened, check against opened_expires_at (2 minutes after opening)
        
#         # first_opened_at = token_data.get("first_opened_at")
#         # opened_expires_at = token_data.get("opened_expires_at")
        
#         # if first_opened_at is None:
#         #     # Token has never been opened
#         #     # Only check cleanup expiry (24 hours from creation)
#         #     cleanup_expires_at = token_data.get("expires_at", 0)
#         #     if current_time > cleanup_expires_at:
#         #         return None, "Token expired (cleanup)"
            
#         #     # If this is the first time opening, mark it as opened
#         #     if mark_opened:
#         #         opened_expires_at = current_time + (2 * 60)  # 2 minutes from now
                
#         #         # Update the token with opening timestamp
#         #         update_data = {
#         #             "first_opened_at": current_time,
#         #             "opened_expires_at": opened_expires_at
#         #         }
                
#         #         if len(token_or_code) == 6:
#         #             supabase.table("feedback_tokens").update(update_data).eq("short_code", token_or_code).execute()
#         #             print(f"Short code {token_or_code} marked as opened, expires at {opened_expires_at}")
#         #         else:
#         #             supabase.table("feedback_tokens").update(update_data).eq("token", token_or_code).execute()
#         #             print(f"Token {token_or_code[:10]}... marked as opened, expires at {opened_expires_at}")
                
#         #         # Update token_data for return
#         #         token_data["first_opened_at"] = current_time
#         #         token_data["opened_expires_at"] = opened_expires_at
#         # else:
#         #     # Token has been opened before, check 2-minute expiry
#         #     if opened_expires_at and current_time > opened_expires_at:
#         #         return None, "Token expired (2 minutes after opening)"
        
#         # Mark token as used only if consume=True (for POST requests)
#         if consume:
#             if len(token_or_code) == 6:
#                 supabase.table("feedback_tokens").update({"used": True}).eq("short_code", token_or_code).execute()
#                 print(f"Short code {token_or_code} consumed (marked as used)")
#             else:
#                 supabase.table("feedback_tokens").update({"used": True}).eq("token", token_or_code).execute()
#                 print(f"Token {token_or_code[:10]}... consumed (marked as used)")
#         else:
#             if len(token_or_code) == 6:
#                 print(f"Short code {token_or_code} validated but not consumed")
#             else:
#                 print(f"Token {token_or_code[:10]}... validated but not consumed")
        
#         return token_data, "Valid"
        
#     except Exception as e:
#         print(f"Error validating token: {str(e)}")
#         return None, "Token validation error"

def validate_feedback_token(token_or_code, consume=False):
    """
    Validate a feedback token (supports both token and short_code)
    Links are now completely lifelong and can be used multiple times
    
    Args:
        token_or_code: The token or short code to validate
        consume: Kept for compatibility but ignored (tokens are never consumed)
    """
    try:
        # Try to find by short_code first, then by token
        result = None
        
        # Check if it's a short code (6 characters) or long token
        if len(token_or_code) == 6:
            # It's a short code
            result = supabase.table("feedback_tokens").select("*").eq("short_code", token_or_code).single().execute()
        else:
            # It's a long token
            result = supabase.table("feedback_tokens").select("*").eq("token", token_or_code).single().execute()
        
        if not result.data:
            return None, "Invalid token"
        
        token_data = result.data
        
        # Token is always valid if it exists - no expiration, no usage limits
        if len(token_or_code) == 6:
            print(f"Short code {token_or_code} validated (lifelong link)")
        else:
            print(f"Token {token_or_code[:10]}... validated (lifelong link)")
        
        return token_data, "Valid"
        
    except Exception as e:
        print(f"Error validating token: {str(e)}")
        return None, "Token validation error"


def update_business(business_id, name, google_review_link):
    """Update an existing business in the database"""
    import re
    
    # Extract Place ID from Google Maps link
    google_place_id = extract_place_id_from_url(google_review_link)
    
    return supabase.table("businesses").update({
        "name": name,
        "google_place_id": google_place_id,
        "google_review_link": google_review_link
    }).eq("id", business_id).execute()

# def cleanup_expired_tokens():
#     """Clean up expired tokens from database"""
#     # import time
    
#     # try:
#     #     current_time = int(time.time())
        
#     #     # Clean up tokens that are either:
#     #     # 1. Past cleanup expiry (24 hours from creation) and never opened
#     #     # 2. Past opened expiry (2 minutes after opening)
        
#     #     # First, cleanup old unopened tokens (24+ hours old)
#     #     result1 = supabase.table("feedback_tokens").delete().lt("expires_at", current_time).is_("first_opened_at", "null").execute()
        
#     #     # Second, cleanup opened tokens that expired (2+ minutes after opening)
#     #     result2 = supabase.table("feedback_tokens").delete().lt("opened_expires_at", current_time).execute()
        
#     #     total_cleaned = (len(result1.data) if result1.data else 0) + (len(result2.data) if result2.data else 0)
#     #     print(f"Cleaned up {total_cleaned} expired tokens")
#     try:
#         # Only clean up tokens that are marked as used
#         result = supabase.table("feedback_tokens").delete().eq("used", True).execute()
        
#         total_cleaned = len(result.data) if result.data else 0
#         print(f"Cleaned up {total_cleaned} used tokens")
        
#     except Exception as e:
#         print(f"Error cleaning up tokens: {str(e)}")


def cleanup_expired_tokens():
    """Optional cleanup function - kept for compatibility but does nothing since tokens are lifelong"""
    print("Cleanup skipped - tokens are now lifelong and never expire")


# Client Management Functions
def create_client(business_id, email, temporary_password):
    """Create a new client account for a business"""
    import bcrypt
    import secrets
    
    try:
        # Hash the temporary password
        hashed_password = bcrypt.hashpw(temporary_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Insert client record
        result = supabase.table("clients").insert({
            "business_id": business_id,
            "email": email,
            "password_hash": hashed_password,
            "is_temporary_password": True,
            "created_at": "now()"
        }).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error creating client: {str(e)}")
        return None

def authenticate_client(email, password):
    """Authenticate a client login"""
    import bcrypt
    
    try:
        # Get client by email
        result = supabase.table("clients").select("*").eq("email", email).execute()
        
        if not result.data or len(result.data) == 0:
            return None, "Invalid email or password"
        
        client = result.data[0]
        
        # Check password
        if bcrypt.checkpw(password.encode('utf-8'), client['password_hash'].encode('utf-8')):
            return client, "Success"
        else:
            return None, "Invalid email or password"
            
    except Exception as e:
        print(f"Error authenticating client: {str(e)}")
        return None, "Authentication error"

def update_client_password(client_id, new_password):
    """Update client password and mark as no longer temporary"""
    import bcrypt
    
    try:
        # Hash the new password
        hashed_password = bcrypt.hashpw(new_password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
        
        # Update client record
        result = supabase.table("clients").update({
            "password_hash": hashed_password,
            "is_temporary_password": False,
            "updated_at": "now()"
        }).eq("id", client_id).execute()
        
        return result.data[0] if result.data else None
    except Exception as e:
        print(f"Error updating client password: {str(e)}")
        return None

def get_client_by_id(client_id):
    """Get client by ID"""
    try:
        result = supabase.table("clients").select("*").eq("id", client_id).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting client: {str(e)}")
        return None

def get_client_by_email(email):
    """Get client by email"""
    try:
        result = supabase.table("clients").select("*").eq("email", email).execute()
        if result.data and len(result.data) > 0:
            return result.data[0]
        return None
    except Exception as e:
        print(f"Error getting client by email: {str(e)}")
        return None

def get_reviews_for_current_month(business_id):
    """Get reviews for the current month"""
    from datetime import datetime, timedelta
    
    try:
        # Get current month start
        now = datetime.now()
        month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Format for Supabase query
        month_start_str = month_start.isoformat()
        
        result = supabase.table("reviews").select("*").eq("business_id", business_id).gte("created_at", month_start_str).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting monthly reviews: {str(e)}")
        return []

def get_reviews_by_date_range(business_id, start_date=None, end_date=None):
    """Get reviews filtered by date range"""
    from datetime import datetime
    
    try:
        query = supabase.table("reviews").select("*").eq("business_id", business_id)
        
        if start_date:
            # Convert string date to datetime if needed
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_date_str = start_date.isoformat()
            query = query.gte("created_at", start_date_str)
        
        if end_date:
            # Convert string date to datetime if needed
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            # Add 23:59:59 to include the entire end date
            end_date = end_date.replace(hour=23, minute=59, second=59)
            end_date_str = end_date.isoformat()
            query = query.lte("created_at", end_date_str)
        
        # Order by created_at descending to show newest first
        result = query.order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting reviews by date range: {str(e)}")
        return []

def get_reviews_by_rating_range(business_id, min_rating=None, max_rating=None, start_date=None, end_date=None):
    """Get reviews filtered by rating range and optionally by date range"""
    from datetime import datetime
    
    try:
        query = supabase.table("reviews").select("*").eq("business_id", business_id)
        
        # Apply rating filters
        if min_rating is not None:
            query = query.gte("rating", min_rating)
        if max_rating is not None:
            query = query.lte("rating", max_rating)
        
        # Apply date filters if provided
        if start_date:
            if isinstance(start_date, str):
                start_date = datetime.strptime(start_date, '%Y-%m-%d')
            start_date_str = start_date.isoformat()
            query = query.gte("created_at", start_date_str)
        
        if end_date:
            if isinstance(end_date, str):
                end_date = datetime.strptime(end_date, '%Y-%m-%d')
            end_date = end_date.replace(hour=23, minute=59, second=59)
            end_date_str = end_date.isoformat()
            query = query.lte("created_at", end_date_str)
        
        # Order by created_at descending to show newest first
        result = query.order("created_at", desc=True).execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting reviews by rating range: {str(e)}")
        return []

def get_all_clients():
    """Get all clients for admin view"""
    try:
        result = supabase.table("clients").select("*, businesses(name)").execute()
        return result.data if result.data else []
    except Exception as e:
        print(f"Error getting all clients: {str(e)}")
        return []

def delete_client(client_id):
    """Delete a client account"""
    try:
        result = supabase.table("clients").delete().eq("id", client_id).execute()
        return result
    except Exception as e:
        print(f"Error deleting client: {str(e)}")
        raise e



print("SUPABASE_URL:", SUPABASE_URL)
print("SUPABASE_KEY starts with:", SUPABASE_KEY[:20])

if not SUPABASE_KEY.startswith("eyJ"):
    raise RuntimeError("Invalid Supabase service role key loaded")

import base64
import json

def decode_jwt_role(token):
    try:
        payload = token.split(".")[1]
        padded = payload + "=" * (-len(payload) % 4)
        data = json.loads(base64.urlsafe_b64decode(padded))
        return data.get("role")
    except Exception:
        return "INVALID"

print("SUPABASE JWT ROLE:", decode_jwt_role(SUPABASE_KEY))

