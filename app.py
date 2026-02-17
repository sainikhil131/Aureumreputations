# -*- coding: utf-8 -*-
from flask import Flask, render_template, request, jsonify, send_from_directory, Blueprint, redirect ,session
# from flask_mail import Mail, Message
from flask_cors import CORS
import os
import secrets
import requests
from dotenv import load_dotenv
from database import save_review, get_business
from database import get_reviews
from database import save_review, get_business, get_reviews, get_all_businesses, save_business, delete_business, create_feedback_token, validate_feedback_token, cleanup_expired_tokens, update_business, create_client, authenticate_client, update_client_password, get_client_by_id, get_client_by_email, get_reviews_for_current_month, get_all_clients, delete_client, get_reviews_by_date_range, get_reviews_by_rating_range


# Load environment variables
load_dotenv()

app = Flask(__name__)

# Security Configuration
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY', secrets.token_hex(32))
app.config['ENV'] = os.getenv('FLASK_ENV', 'production')
app.config['DEBUG'] = os.getenv('FLASK_DEBUG', 'False') == 'True'

CORS(app)

# Add security headers for HTTPS and CSP
@app.after_request
def add_security_headers(response):
    # Force HTTPS (HSTS)
    response.headers['Strict-Transport-Security'] = 'max-age=31536000; includeSubDomains; preload'
    
    # Content Security Policy - Allow necessary scripts and styles
    response.headers['Content-Security-Policy'] = "default-src 'self'; script-src 'self' 'unsafe-inline' 'unsafe-eval' https://cdnjs.cloudflare.com https://fonts.googleapis.com; style-src 'self' 'unsafe-inline' https://cdnjs.cloudflare.com https://fonts.googleapis.com; font-src 'self' https://fonts.gstatic.com https://cdnjs.cloudflare.com; img-src 'self' data: https:; connect-src 'self'; frame-ancestors 'self'"
    
    response.headers['X-Content-Type-Options'] = 'nosniff'
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    response.headers['X-XSS-Protection'] = '1; mode=block'
    response.headers['Referrer-Policy'] = 'strict-origin-when-cross-origin'
    return response

import requests


ACCOUNT_ID = "3261500000000002002"

def send_zoho_email(to_email, subject, html_content):
    # Get access token
    token_res = requests.post(
        "https://accounts.zoho.in/oauth/v2/token",
        data={
            "refresh_token": os.getenv("ZOHO_REFRESH_TOKEN"),
            "client_id": os.getenv("ZOHO_CLIENT_ID"),
            "client_secret": os.getenv("ZOHO_CLIENT_SECRET"),
            "grant_type": "refresh_token"
        },
        timeout=15
    )

    token_data = token_res.json()
    if "access_token" not in token_data:
        raise Exception(f"Zoho OAuth Error: {token_data}")

    access_token = token_data["access_token"]

    # Send mail (CORRECT endpoint)
    url = f"https://mail.zoho.in/api/accounts/{ACCOUNT_ID}/messages"

    headers = {
        "Authorization": f"Zoho-oauthtoken {access_token}",
        "Content-Type": "application/json"
    }

    payload = {
        "fromAddress": os.getenv("ZOHO_FROM_EMAIL"),
        "toAddress": to_email,
        "subject": subject,
        "content": html_content
    }

    res = requests.post(url, headers=headers, json=payload, timeout=15)

    if res.status_code not in (200, 201):
        raise Exception(f"Zoho Mail Error: {res.text}")

    return True




# AiSensy Configuration
AISENSY_API_KEY = os.getenv("AISENSY_API_KEY")
AISENSY_CAMPAIGN_ID = os.getenv("AISENSY_CAMPAIGN_ID")
AUREUM_DOMAIN = os.getenv("AUREUM_DOMAIN")



@app.route('/')
def index():
    return render_template('index.html')

@app.route('/health')
def health():
    """Health check endpoint for debugging deployment"""
    import sys
    return jsonify({
        'status': 'ok',
        'python_version': sys.version,
        'templates_folder': app.template_folder,
        'static_folder': app.static_folder,
        'debug': app.debug,
        'env': app.config.get('ENV')
    })

@app.route('/services')
def services():
    return render_template('services.html')

@app.route('/reviews')
def reviews():
    return render_template('reviews.html')


@app.route("/send-email", methods=["POST"])
def send_contact_email():
    data = request.get_json() or request.form

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    business_name = (data.get("business_name") or "").strip()
    message = (data.get("message") or "").strip()

    if not all([name, email, message]):
        return jsonify({
            "success": False,
            "message": "Name, email, and message are required."
        }), 400

    # Admin email
    send_zoho_email(
        to_email="info@aureumreputations.com",
        subject=f"New Contact Form Submission from {name}",
        html_content=f"""
            <h3>New Contact Form</h3>
            <p><b>Name:</b> {name}</p>
            <p><b>Business:</b> {business_name}</p>
            <p><b>Email:</b> {email}</p>
            <p><b>Message:</b> {message}</p>
        """
    )

    return jsonify({
        "success": True,
        "message": "Thank you for your message! We will contact you soon."
    }), 200


@app.route('/chatbot', methods=['POST'])
def chatbot():
    """Handle chatbot conversations with Aureum AI Assistant"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip().lower()
        conversation_history = data.get('history', [])

        # Get chatbot response
        response = get_chatbot_response(user_message, conversation_history)

        return jsonify({
            'success': True,
            'response': response
        }), 200

    except Exception as e:
        print(f"Error in chatbot: {str(e)}")
        return jsonify({
            'success': False,
            'response': "I apologize, but I'm experiencing technical difficulties. Please try again or contact us directly."
        }), 500

def get_chatbot_response(user_message, history):
    """Generate intelligent responses based on user input"""

    # Greeting patterns
    greetings = ['hello', 'hi', 'hey', 'good morning', 'good afternoon', 'good evening', 'greetings']
    if any(greeting in user_message for greeting in greetings) and len(history) == 0:
        return "Hello! How can I help you today?"

    # Fake reviews / Crisis management
    if any(word in user_message for word in ['fake review', 'negative review', 'bad review', 'attack', 'crisis', 'emergency', 'urgent']):
        return "I can help with that immediately! 🛡️\n\nAureum's Crisis Management module specializes in:\n• Identifying and removing fake reviews\n• 24/7 reputation monitoring\n• Strategic response planning\n• Brand protection protocols\n• Recovery campaigns\n\nWould you like to book a Rapid Crisis Consultation? I'll just need your business name and email to get started."

    # Review generation / growth
    if any(word in user_message for word in ['review', 'google review', 'yelp', 'testimonial', 'rating', 'grow review']):
        return "Excellent! Our Review Generation & Growth program helps you build authentic, verified feedback through smart automation. ⭐\n\nWe offer:\n• Multi-platform integration (Google, Yelp, Clutch, BBB, Airbnb)\n• Automated review requests with smart timing\n• Real-time monitoring\n• Response management\n• Growth analytics\n\nWould you like me to prepare a free Review Health Audit? I'll just need your business name and email to get started."

    # SEO / Local SEO / Citations
    if any(word in user_message for word in ['seo', 'local seo', 'citation', 'visibility', 'ranking', 'google ranking', 'search']):
        return "Great question! Our SEO & Citation Optimization service improves your visibility across 50+ directories. 📊\n\nWe provide:\n• Local SEO optimization\n• Citation management\n• NAP consistency (Name-Address-Phone)\n• Schema markup for better Google ranking\n• Multi-location listing support\n\nI can schedule a free Visibility Audit for you. Could you share your business name and email?"

    # Social media
    if any(word in user_message for word in ['social media', 'facebook', 'instagram', 'twitter', 'linkedin', 'social presence']):
        return "Exciting! Our Social Media Presence program (currently in Beta) helps build authentic engagement across platforms. 🚀\n\nWe offer:\n• Social media strategy & content planning\n• Curated post creation\n• Automated yet authentic engagement\n• Community management\n• Growth analytics\n\nWould you like to apply for Beta Access to Aureum Social Presence? I'll need your business name and email."

    # Pricing
    if any(word in user_message for word in ['price', 'cost', 'pricing', 'how much', 'expensive', 'affordable', 'package']):
        return "Great question! Our pricing is customized based on your specific needs and business size. 💼\n\nWe offer flexible packages for:\n• Review Generation & Growth\n• Crisis Management\n• SEO & Citation Optimization\n• Social Media Presence\n• Full-service reputation management\n\nWould you like to schedule a free consultation to discuss pricing tailored to your business? I'll just need your business name and email."

    # How it works / Process
    if any(word in user_message for word in ['how does it work', 'how it works', 'process', 'get started', 'begin', 'start']):
        return "Getting started with Aureum is simple! Here's our process:\n\n1️⃣ Free Audit - We analyze your current online reputation\n2️⃣ Strategy Session - We create a customized plan for your business\n3️⃣ Implementation - Our AI-powered system goes to work\n4️⃣ Monitoring & Optimization - Continuous improvement with real-time analytics\n\nReady to begin? I can schedule your free audit right now. What's your business name and email?"

    # Services overview
    if any(word in user_message for word in ['service', 'what do you do', 'what can you do', 'help with', 'offer']):
        return "I'm here to help businesses build trust, recover credibility, and grow visibility! 🌟\n\nOur Core Services:\n\n⭐ Review Generation & Growth - Build authentic review profiles\n🛡️ Crisis Management - Rapid response to reputation threats\n📊 SEO & Citation Optimization - Boost local visibility\n🚀 Social Media Presence - Authentic engagement (Beta)\n🤖 Aureum Core Intelligence - AI-powered analytics\n\nWhich service interests you most?"

    # About Aureum / Company info
    if any(word in user_message for word in ['about', 'who are you', 'company', 'aureum', 'what is aureum']):
        return "I'm Aureum, your AI-powered reputation consultant! 🌟\n\nAureum Reputations is a leading platform that helps businesses build, protect, and elevate their digital credibility through:\n\n✅ Ethical practices - No fake reviews or manipulative tactics\n✅ Data-driven results - Powered by Aureum Core Intelligence\n✅ Measurable outcomes - Real-time analytics and reporting\n\nWe believe in building authentic trust that lasts. How can I help your business today?"

    # Contact / Talk to human
    if any(word in user_message for word in ['contact', 'talk to human', 'speak to someone', 'call', 'phone', 'email']):
        return "I'd be happy to connect you with our team! 📞\n\nYou can reach us at:\n📧 Email: info@aureumreputations.com\n\nOr you can:\n• Schedule a consultation - I can book this for you right now\n• Request a callback - Our team will reach out within 24 hours\n\nWhat's your preferred method? Please share your business name and email, and I'll make sure you're taken care of."

    # Thank you
    if any(word in user_message for word in ['thank', 'thanks', 'appreciate']):
        return "You're very welcome! 😊 Is there anything else I can help you with today?\n\nRemember, I can assist with:\n• Free audits and consultations\n• Service information\n• Scheduling appointments\n• Answering questions about reputation management"

    # Goodbye
    if any(word in user_message for word in ['bye', 'goodbye', 'see you', 'later', 'exit']):
        return "Thank you for chatting with me! If you need anything else, I'm always here to help. Have a great day! ✨\n\n— Aureum Reputations Team"

    # Default response - ask for clarification
    return "I'd love to help you with that! Could you tell me more about what you're looking for? 🤔\n\nI specialize in:\n• Review management - Growing and protecting your reviews\n• Crisis response - Handling negative feedback or attacks\n• SEO optimization - Improving your local visibility\n• Social media - Building authentic engagement\n\nWhich area interests you most?"

@app.route('/send-consultation', methods=['POST'])
def send_consultation():
    try:
        data = request.get_json() or {}

        name = (data.get('name') or '').strip()
        business_name = (data.get('business_name') or '').strip()
        email = (data.get('email') or '').strip()
        phone = (data.get('phone') or '').strip()
        service = (data.get('service') or '').strip()
        message_text = (data.get('message') or '').strip()

        # Validation
        if not all([name, business_name, email, phone, service, message_text]):
            return jsonify({
                'success': False,
                'message': 'All required fields must be filled.'
            }), 400

        # ✅ Send ADMIN email via Zoho API
        send_zoho_email(
            to_email="info@aureumreputations.com",
            subject=f"Consultation Request: {name} - {service}",
            html_content=f"""
                <h2>📩 New Consultation Request</h2>
                <p><b>Name:</b> {name}</p>
                <p><b>Business:</b> {business_name}</p>
                <p><b>Email:</b> {email}</p>
                <p><b>Phone:</b> {phone}</p>
                <p><b>Service:</b> {service}</p>

                <hr>

                <p><b>Message:</b></p>
                <p>{message_text}</p>
            """
        )

        return jsonify({
            'success': True,
            'message': 'Thank you! Your consultation request has been submitted. We will contact you within 24 hours.'
        }), 200

    except Exception as e:
        print(f"Consultation form error: {str(e)}")
        return jsonify({
            'success': False,
            'message': 'An error occurred. Please try again later.'
        }), 500

from flask import render_template, request, redirect
from database import save_review, get_business
from urllib.parse import quote

def generate_feedback_link_for_phone(phone, business_id=None, customer_name=""):
    """
    Backend-safe function to generate review link
    """
    token_data = create_feedback_token(business_id, customer_name)

    if not token_data:
        return None

    return f"{AUREUM_DOMAIN}/r/{token_data['short_code']}"



@app.route("/generate-feedback-link", methods=["POST"])
def generate_feedback_link():
    if not session.get("logged_in"):
        return jsonify({"error": "Unauthorized"}), 401

    try:
        data = request.get_json()
        business_id = data.get("business_id")
        customer_name = data.get("customer_name", "")

        if not business_id:
            return jsonify({"error": "Business ID required"}), 400

        feedback_url = generate_feedback_link_for_phone(
            phone=None,
            business_id=business_id,
            customer_name=customer_name
        )

        if not feedback_url:
            return jsonify({"error": "Failed to create feedback link"}), 500

        return jsonify({
            "success": True,
            "feedback_url": feedback_url,
            "customer_name": customer_name,
            "note": "Link is permanently valid"
        })

    except Exception as e:
        print(f"Error generating feedback link: {str(e)}")
        return jsonify({"error": "Internal server error"}), 500


@app.route("/r/<short_code>")
def redirect_short_link(short_code):
    """Handle short feedback links and redirect to full feedback form"""
    try:
        # Validate the short code (lifelong link)
        token_data, validation_message = validate_feedback_token(short_code)
        
        if not token_data:
            # Short code is invalid
            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Link Invalid - Aureum Reputations</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
                <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                <style>
                    :root {{
                        --primary-bg: #0a0a0a;
                        --secondary-bg: #121212;
                        --primary-text: #ffffff;
                        --accent-gold: #D4AF37;
                        --error-red: #ef4444;
                        --card-border: #D4AF37;
                    }}

                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}

                    html {{
                        background: var(--primary-bg);
                    }}

                    body {{
                        font-family: 'Inter', sans-serif;
                        background: var(--primary-bg);
                        color: var(--primary-text);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                        position: relative;
                        overflow-x: hidden;
                    }}

                    body::before {{
                        content: '';
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100vh;
                        background: radial-gradient(circle at 50% 20%, rgba(212, 175, 55, 0.08) 0%, transparent 50%);
                        pointer-events: none;
                        z-index: 0;
                    }}

                    .invalid-container {{
                        background: linear-gradient(135deg, rgba(18, 18, 18, 0.9) 0%, rgba(18, 18, 18, 0.7) 100%);
                        border: 2px solid rgba(212, 175, 55, 0.3);
                        border-radius: 20px;
                        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(212, 175, 55, 0.1);
                        backdrop-filter: blur(10px);
                        -webkit-backdrop-filter: blur(10px);
                        overflow: hidden;
                        width: 100%;
                        max-width: 500px;
                        position: relative;
                        z-index: 1;
                    }}

                    .invalid-container::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
                        transition: left 0.8s;
                    }}

                    .invalid-container:hover::before {{
                        left: 100%;
                    }}

                    .invalid-header {{
                        background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
                        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
                        color: var(--primary-text);
                        padding: 40px 30px;
                        text-align: center;
                        position: relative;
                    }}

                    .invalid-header h1 {{
                        font-family: 'Poppins', sans-serif;
                        font-size: 28px;
                        font-weight: 700;
                        margin-bottom: 8px;
                        letter-spacing: -0.5px;
                        background: linear-gradient(135deg, #ffffff 0%, #D4AF37 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 12px;
                    }}

                    .invalid-header h1 i {{
                        color: var(--error-red);
                        font-size: 24px;
                    }}

                    .invalid-header p {{
                        color: rgba(255, 255, 255, 0.7);
                        font-size: 15px;
                        line-height: 1.6;
                    }}

                    .invalid-content {{
                        padding: 40px 30px;
                    }}

                    .status-box {{
                        background: rgba(239, 68, 68, 0.1);
                        border: 2px solid rgba(239, 68, 68, 0.2);
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 30px;
                        backdrop-filter: blur(10px);
                    }}

                    .status-title {{
                        color: var(--error-red);
                        font-weight: 600;
                        font-size: 14px;
                        margin-bottom: 8px;
                        text-transform: uppercase;
                        letter-spacing: 0.3px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}

                    .status-text {{
                        color: rgba(255, 255, 255, 0.9);
                        font-size: 15px;
                        line-height: 1.6;
                        margin-bottom: 8px;
                    }}

                    .reason {{
                        color: rgba(255, 255, 255, 0.6);
                        font-size: 14px;
                        font-style: italic;
                    }}

                    .info-section {{
                        background: rgba(0, 0, 0, 0.4);
                        border: 2px solid rgba(212, 175, 55, 0.2);
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 30px;
                        backdrop-filter: blur(10px);
                    }}

                    .info-title {{
                        color: var(--accent-gold);
                        font-weight: 600;
                        font-size: 14px;
                        margin-bottom: 8px;
                        text-transform: uppercase;
                        letter-spacing: 0.3px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}

                    .info-text {{
                        color: rgba(255, 255, 255, 0.8);
                        font-size: 15px;
                        line-height: 1.6;
                    }}

                    .security-note {{
                        background: rgba(212, 175, 55, 0.1);
                        border: 2px solid rgba(212, 175, 55, 0.2);
                        border-radius: 12px;
                        padding: 16px;
                        font-size: 14px;
                        color: rgba(255, 255, 255, 0.8);
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}

                    .security-note i {{
                        color: var(--accent-gold);
                        font-size: 16px;
                    }}

                    @media (max-width: 768px) {{
                        .invalid-container {{
                            margin: 10px;
                            border-radius: 16px;
                            max-width: 420px;
                        }}
                        
                        .invalid-header {{
                            padding: 30px 25px;
                        }}
                        
                        .invalid-header h1 {{
                            font-size: 24px;
                        }}
                        
                        .invalid-content {{
                            padding: 30px 25px;
                        }}
                    }}

                    @media (max-width: 480px) {{
                        body {{
                            padding: 15px;
                        }}

                        .invalid-header {{
                            padding: 25px 20px;
                        }}

                        .invalid-header h1 {{
                            font-size: 20px;
                            flex-direction: column;
                            gap: 8px;
                        }}

                        .invalid-content {{
                            padding: 25px 20px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="invalid-container">
                    <div class="invalid-header">
                        <h1><i class="fas fa-exclamation-triangle"></i> Link Invalid</h1>
                        <p>This feedback link is not valid</p>
                    </div>

                    <div class="invalid-content">
                        <div class="status-box">
                            <div class="status-title">
                                <i class="fas fa-exclamation-triangle"></i>
                                Access Denied
                            </div>
                            <div class="status-text">This feedback link is invalid.</div>
                            <div class="reason">Reason: {validation_message}</div>
                        </div>

                        <div class="info-section">
                            <div class="info-title">
                                <i class="fas fa-phone-alt"></i>
                                Request New Access
                            </div>
                            <div class="info-text">
                                Please contact the business directly to request a new feedback link. 
                                They can generate a fresh link for you to share your experience.
                            </div>
                        </div>

                        <div class="security-note">
                            <i class="fas fa-shield-alt"></i>
                            <span><strong>Security Notice:</strong> Feedback links are permanently valid and can be used multiple times to share your feedback.</span>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
        
        # Short code is valid, redirect to the full feedback form
        business_id = token_data.get("business_id")
        return redirect(f"/feedback/{business_id}?token={short_code}")
        
    except Exception as e:
        print(f"Error handling short link: {str(e)}")
        return "Invalid link", 400

@app.route("/feedback/<business_id>", methods=["GET", "POST"])
def feedback(business_id):
    # Check for token validation
    token = request.args.get('token')
    
    if token:
        # Validate the token (lifelong link)
        token_data, validation_message = validate_feedback_token(token)
        
        if not token_data:
            # Token is invalid
            return f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>Link Invalid - Aureum Reputations</title>
                <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css">
                <link href="https://fonts.googleapis.com/css2?family=Poppins:wght@300;400;500;600;700&family=Inter:wght@300;400;500;600;700&display=swap" rel="stylesheet">
                <style>
                    :root {{
                        --primary-bg: #0a0a0a;
                        --secondary-bg: #121212;
                        --primary-text: #ffffff;
                        --accent-gold: #D4AF37;
                        --error-red: #ef4444;
                        --card-border: #D4AF37;
                    }}

                    * {{
                        margin: 0;
                        padding: 0;
                        box-sizing: border-box;
                    }}

                    html {{
                        background: var(--primary-bg);
                    }}

                    body {{
                        font-family: 'Inter', sans-serif;
                        background: var(--primary-bg);
                        color: var(--primary-text);
                        min-height: 100vh;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        padding: 20px;
                        position: relative;
                        overflow-x: hidden;
                    }}

                    body::before {{
                        content: '';
                        position: fixed;
                        top: 0;
                        left: 0;
                        width: 100%;
                        height: 100vh;
                        background: radial-gradient(circle at 50% 20%, rgba(212, 175, 55, 0.08) 0%, transparent 50%);
                        pointer-events: none;
                        z-index: 0;
                    }}

                    .invalid-container {{
                        background: linear-gradient(135deg, rgba(18, 18, 18, 0.9) 0%, rgba(18, 18, 18, 0.7) 100%);
                        border: 2px solid rgba(212, 175, 55, 0.3);
                        border-radius: 20px;
                        box-shadow: 0 10px 40px rgba(0, 0, 0, 0.6), 0 0 0 1px rgba(212, 175, 55, 0.1);
                        backdrop-filter: blur(10px);
                        -webkit-backdrop-filter: blur(10px);
                        overflow: hidden;
                        width: 100%;
                        max-width: 500px;
                        position: relative;
                        z-index: 1;
                    }}

                    .invalid-container::before {{
                        content: '';
                        position: absolute;
                        top: 0;
                        left: -100%;
                        width: 100%;
                        height: 100%;
                        background: linear-gradient(90deg, transparent, rgba(212, 175, 55, 0.1), transparent);
                        transition: left 0.8s;
                    }}

                    .invalid-container:hover::before {{
                        left: 100%;
                    }}

                    .invalid-header {{
                        background: linear-gradient(135deg, rgba(212, 175, 55, 0.15) 0%, rgba(212, 175, 55, 0.05) 100%);
                        border-bottom: 1px solid rgba(212, 175, 55, 0.2);
                        color: var(--primary-text);
                        padding: 40px 30px;
                        text-align: center;
                        position: relative;
                    }}

                    .invalid-header h1 {{
                        font-family: 'Poppins', sans-serif;
                        font-size: 28px;
                        font-weight: 700;
                        margin-bottom: 8px;
                        letter-spacing: -0.5px;
                        background: linear-gradient(135deg, #ffffff 0%, #D4AF37 100%);
                        -webkit-background-clip: text;
                        -webkit-text-fill-color: transparent;
                        background-clip: text;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 12px;
                    }}

                    .invalid-header h1 i {{
                        color: var(--error-red);
                        font-size: 24px;
                    }}

                    .invalid-header p {{
                        color: rgba(255, 255, 255, 0.7);
                        font-size: 15px;
                        line-height: 1.6;
                    }}

                    .invalid-content {{
                        padding: 40px 30px;
                    }}

                    .status-box {{
                        background: rgba(239, 68, 68, 0.1);
                        border: 2px solid rgba(239, 68, 68, 0.2);
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 30px;
                        backdrop-filter: blur(10px);
                    }}

                    .status-title {{
                        color: var(--error-red);
                        font-weight: 600;
                        font-size: 14px;
                        margin-bottom: 8px;
                        text-transform: uppercase;
                        letter-spacing: 0.3px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}

                    .status-text {{
                        color: rgba(255, 255, 255, 0.9);
                        font-size: 15px;
                        line-height: 1.6;
                        margin-bottom: 8px;
                    }}

                    .reason {{
                        color: rgba(255, 255, 255, 0.6);
                        font-size: 14px;
                        font-style: italic;
                    }}

                    .info-section {{
                        background: rgba(0, 0, 0, 0.4);
                        border: 2px solid rgba(212, 175, 55, 0.2);
                        border-radius: 12px;
                        padding: 20px;
                        margin-bottom: 30px;
                        backdrop-filter: blur(10px);
                    }}

                    .info-title {{
                        color: var(--accent-gold);
                        font-weight: 600;
                        font-size: 14px;
                        margin-bottom: 8px;
                        text-transform: uppercase;
                        letter-spacing: 0.3px;
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}

                    .info-text {{
                        color: rgba(255, 255, 255, 0.8);
                        font-size: 15px;
                        line-height: 1.6;
                    }}

                    .security-note {{
                        background: rgba(212, 175, 55, 0.1);
                        border: 2px solid rgba(212, 175, 55, 0.2);
                        border-radius: 12px;
                        padding: 16px;
                        font-size: 14px;
                        color: rgba(255, 255, 255, 0.8);
                        display: flex;
                        align-items: center;
                        gap: 8px;
                    }}

                    .security-note i {{
                        color: var(--accent-gold);
                        font-size: 16px;
                    }}

                    @media (max-width: 768px) {{
                        .invalid-container {{
                            margin: 10px;
                            border-radius: 16px;
                            max-width: 420px;
                        }}
                        
                        .invalid-header {{
                            padding: 30px 25px;
                        }}
                        
                        .invalid-header h1 {{
                            font-size: 24px;
                        }}
                        
                        .invalid-content {{
                            padding: 30px 25px;
                        }}
                    }}

                    @media (max-width: 480px) {{
                        body {{
                            padding: 15px;
                        }}

                        .invalid-header {{
                            padding: 25px 20px;
                        }}

                        .invalid-header h1 {{
                            font-size: 20px;
                            flex-direction: column;
                            gap: 8px;
                        }}

                        .invalid-content {{
                            padding: 25px 20px;
                        }}
                    }}
                </style>
            </head>
            <body>
                <div class="invalid-container">
                    <div class="invalid-header">
                        <h1><i class="fas fa-exclamation-triangle"></i> Link Invalid</h1>
                        <p>This feedback link is not valid</p>
                    </div>

                    <div class="invalid-content">
                        <div class="status-box">
                            <div class="status-title">
                                <i class="fas fa-exclamation-triangle"></i>
                                Access Denied
                            </div>
                            <div class="status-text">This feedback link is invalid.</div>
                            <div class="reason">Reason: {validation_message}</div>
                        </div>

                        <div class="info-section">
                            <div class="info-title">
                                <i class="fas fa-phone-alt"></i>
                                Request New Access
                            </div>
                            <div class="info-text">
                                Please contact the business directly to request a new feedback link. 
                                They can generate a fresh link for you to share your experience.
                            </div>
                        </div>

                        <div class="security-note">
                            <i class="fas fa-shield-alt"></i>
                            <span><strong>Security Notice:</strong> Feedback links are permanently valid and can be used multiple times to share your feedback.</span>
                        </div>
                    </div>
                </div>
            </body>
            </html>
            """
        
        # Token is valid, verify business ID matches
        if token_data.get("business_id") != business_id:
            return "Invalid token for this business.", 400
    
    # Fetch business details
    business = get_business(business_id)

    if not business:
        return "Invalid Business ID", 404

    if request.method == "POST":
        # Get review data from form
        customer_name = request.form.get("name")
        rating = int(request.form.get("rating"))
        comment = request.form.get("comment", "")  # Make comment optional

        # Validate required fields
        if not customer_name or not customer_name.strip():
            return "Customer name is required", 400
        
        if not rating:
            return "Rating is required", 400

        # Save review to Supabase (good or bad) - comment can be empty
        save_review(business_id, customer_name.strip(), rating, comment.strip() if comment else "No additional feedback provided")

        # If 4 or 5 star ? redirect directly to the Google Maps review page
        if rating >= 4:
            # Use the original Google Maps link provided by admin
            google_review_link = business.get("google_review_link")
            
            if not google_review_link:
                return "Google Maps link not found for this business."
            
            # Convert to direct review format (g.page/r/CODE/review)
            from database import convert_to_direct_review_link
            direct_review_link = convert_to_direct_review_link(google_review_link)
            
            print(f"Redirecting to direct review link: {direct_review_link}")
            return redirect(direct_review_link)

        # If bad review ? show Thank You message (stored in DB)
        else:
            return render_template("thankyou_negative.html")

    # Render form (GET request) - show token info if available
    customer_name = token_data.get("customer_name", "") if token and token_data else ""
    
    return render_template("feedback.html", business=business, customer_name=customer_name, token_protected=bool(token))


@app.route("/get-google-maps-link/<business_id>", methods=["POST"])
def get_google_maps_link(business_id):
    """Get Google Maps review link for immediate redirect on high ratings"""
    # Get rating data from request
    data = request.get_json()
    rating = data.get('rating')
    customer_name = data.get('customer_name', 'Anonymous')
    
    # Fetch business details
    business = get_business(business_id)
    
    if not business:
        return jsonify({"error": "Business not found"}), 404
    
    google_review_link = business.get("google_review_link")
    
    if not google_review_link:
        return jsonify({"error": "Google Maps link not configured"}), 404
    
    # Save the rating to database quickly (async would be better but this is fast enough)
    if rating and rating >= 4:
        comment_text = f"Customer gave {rating} stars and was redirected to Google Maps"
        save_review(business_id, customer_name, int(rating), comment_text)
    
    # Convert to direct review format for better user experience
    from database import convert_to_direct_review_link
    direct_review_link = convert_to_direct_review_link(google_review_link)
    
    # Fast approach: Return the direct review link for immediate redirect
    print(f"✅ Fast redirect to direct review page: {direct_review_link}")
    
    return jsonify({"google_maps_link": direct_review_link})


@app.route("/admin")
def admin():
    if not session.get("logged_in"):
        return redirect("/login")
    
    try:
        businesses = get_all_businesses()
        clients = get_all_clients()
        
        # Get success/error messages from URL parameters
        success_msg = request.args.get('success')
        error_msg = request.args.get('error')
        
        return render_template("admin.html", 
                             businesses=businesses,
                             clients=clients,
                             success=success_msg,
                             error=error_msg)
    except Exception as e:
        print(f"Database connection error: {str(e)}")
        return jsonify({
            'error': 'Database connection failed',
            'message': 'Unable to connect to Supabase. Please check your internet connection and Supabase project status.',
            'details': str(e)
        }), 500


@app.route("/client-dashboard")
def client_dashboard():
    if not session.get("client_logged_in"):
        return redirect("/login")
    
    try:
        business_id = session.get("business_id")
        business = get_business(business_id)
        
        if not business:
            return redirect("/login?error=Business not found")
        
        # Get filter parameters from request
        start_date = request.args.get('start_date')
        end_date = request.args.get('end_date')
        rating_filter = request.args.get('rating_filter')  # 'low', 'high', or None
        
        # Get all reviews and current month reviews for stats
        all_reviews = get_reviews(business_id)
        monthly_reviews = get_reviews_for_current_month(business_id)
        
        # Calculate rating-based statistics
        low_rating_reviews = [r for r in all_reviews if r.get('rating', 0) < 3] if all_reviews else []
        high_rating_reviews = [r for r in all_reviews if r.get('rating', 0) >= 4] if all_reviews else []
        
        # Get filtered reviews based on date range and rating filter
        if rating_filter == 'low':
            # Show reviews with rating < 3
            filtered_reviews = get_reviews_by_rating_range(business_id, None, 2, start_date, end_date)
        elif rating_filter == 'high':
            # Show reviews with rating 4-5
            filtered_reviews = get_reviews_by_rating_range(business_id, 4, 5, start_date, end_date)
        elif start_date or end_date:
            # Show reviews filtered by date only
            filtered_reviews = get_reviews_by_date_range(business_id, start_date, end_date)
        else:
            # If no filters, show recent reviews (last 20)
            filtered_reviews = get_reviews(business_id)
            if filtered_reviews:
                # Sort by created_at descending and limit to 20
                filtered_reviews = sorted(filtered_reviews, 
                                        key=lambda x: x.get('created_at', ''), 
                                        reverse=True)[:20]
        
        # Calculate statistics (always based on all reviews for consistency)
        total_reviews = len(all_reviews) if all_reviews else 0
        monthly_count = len(monthly_reviews) if monthly_reviews else 0
        low_rating_count = len(low_rating_reviews)
        high_rating_count = len(high_rating_reviews)
        
        # Calculate average rating
        if all_reviews:
            avg_rating = sum(review.get('rating', 0) for review in all_reviews) / len(all_reviews)
            avg_rating = round(avg_rating, 1)
        else:
            avg_rating = 0
        
        # Calculate monthly average rating
        if monthly_reviews:
            monthly_avg_rating = sum(review.get('rating', 0) for review in monthly_reviews) / len(monthly_reviews)
            monthly_avg_rating = round(monthly_avg_rating, 1)
        else:
            monthly_avg_rating = 0
        
        # Get current month name
        from datetime import datetime
        current_month = datetime.now().strftime("%B %Y")
        
        # Convert created_at strings to datetime objects for template formatting
        for review in filtered_reviews:
            if review.get('created_at') and isinstance(review['created_at'], str):
                try:
                    review['created_at'] = datetime.fromisoformat(review['created_at'].replace('Z', '+00:00'))
                except:
                    review['created_at'] = None
        
        return render_template("client_dashboard.html", 
                             business=business,
                             total_reviews=total_reviews,
                             monthly_reviews=monthly_count,
                             avg_rating=avg_rating,
                             monthly_avg_rating=monthly_avg_rating,
                             current_month=current_month,
                             filtered_reviews=filtered_reviews,
                             low_rating_count=low_rating_count,
                             high_rating_count=high_rating_count,
                             current_rating_filter=rating_filter)
    except Exception as e:
        print(f"Error in client dashboard: {str(e)}")
        return redirect("/login?error=Dashboard error")

@app.route("/client-change-password", methods=["GET", "POST"])
def client_change_password():
    if not session.get("client_logged_in"):
        return redirect("/login")
    
    first_login = request.args.get("first_login") == "true"
    
    if request.method == "POST":
        current_password = request.form.get("current_password", "")
        new_password = request.form.get("new_password", "")
        confirm_password = request.form.get("confirm_password", "")
        
        # Validation
        if not all([current_password, new_password, confirm_password]):
            return render_template("client_change_password.html", 
                                 error="All fields are required", 
                                 first_login=first_login)
        
        if new_password != confirm_password:
            return render_template("client_change_password.html", 
                                 error="New passwords do not match", 
                                 first_login=first_login)
        
        # Password strength validation
        if len(new_password) < 8:
            return render_template("client_change_password.html", 
                                 error="Password must be at least 8 characters long", 
                                 first_login=first_login)
        
        if not any(c.isupper() for c in new_password):
            return render_template("client_change_password.html", 
                                 error="Password must contain at least one uppercase letter", 
                                 first_login=first_login)
        
        if not any(c.islower() for c in new_password):
            return render_template("client_change_password.html", 
                                 error="Password must contain at least one lowercase letter", 
                                 first_login=first_login)
        
        if not any(c.isdigit() for c in new_password):
            return render_template("client_change_password.html", 
                                 error="Password must contain at least one number", 
                                 first_login=first_login)
        
        if not any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in new_password):
            return render_template("client_change_password.html", 
                                 error="Password must contain at least one special character", 
                                 first_login=first_login)
        
        # Verify current password
        client_email = session.get("client_email")
        client, message = authenticate_client(client_email, current_password)
        
        if not client:
            return render_template("client_change_password.html", 
                                 error="Current password is incorrect", 
                                 first_login=first_login)
        
        # Update password
        client_id = session.get("client_id")
        result = update_client_password(client_id, new_password)
        
        if result:
            return redirect("/client-dashboard?success=Password updated successfully")
        else:
            return render_template("client_change_password.html", 
                                 error="Failed to update password", 
                                 first_login=first_login)
    
    return render_template("client_change_password.html", first_login=first_login)

@app.route("/client-logout")
def client_logout():
    session.pop("client_logged_in", None)
    session.pop("client_id", None)
    session.pop("client_email", None)
    session.pop("business_id", None)
    return redirect("/login?success=Logged out successfully")

@app.route("/client-send-customer", methods=["GET", "POST"])
def client_send_customer():
    """Client version of send WhatsApp review requests to customers"""
    if not session.get("client_logged_in"):
        return redirect("/login")
    
    try:
        business_id = session.get("business_id")
        business = get_business(business_id)
        
        if not business:
            return redirect("/login?error=Business not found")
        
        if request.method == "POST":
            try:
                # Handle single customer form
                if 'name' in request.form and 'phone' in request.form:
                    name = request.form.get('name', '').strip()
                    phone = request.form.get('phone', '').strip()
                    country_code = request.form.get('country_code', '+91').strip()
                    
                    if not name or not phone:
                        return render_template("client_send_customer.html", 
                                             business=business,
                                             error="All fields are required.")
                    
                    # Format phone number with country code
                    full_phone = country_code + phone
                    
                    # Send WhatsApp message
                    success, message = send_review_template_sigmo(
                        phone=full_phone,
                        customer_name=name,
                        business_name=business["name"],
                        review_link=review_link)

                    
                    if success:
                        return render_template("client_send_customer.html", 
                                             business=business,
                                             success=message)
                    else:
                        return render_template("client_send_customer.html", 
                                             business=business,
                                             error=message)
                
                # Handle bulk upload
                elif 'excel_file' in request.files:
                    excel_file = request.files['excel_file']
                    
                    if not excel_file or excel_file.filename == '':
                        return render_template("client_send_customer.html", 
                                             business=business,
                                             error="Please select an Excel file.")
                    
                    try:
                        # Read Excel file
                        import pandas as pd
                        df = pd.read_excel(excel_file)
                        
                        # Check for required columns
                        name_col = None
                        phone_col = None
                        
                        for col in df.columns:
                            col_lower = str(col).lower()
                            if 'name' in col_lower and not name_col:
                                name_col = col
                            elif ('phone' in col_lower or 'whatsapp' in col_lower or 'number' in col_lower) and not phone_col:
                                phone_col = col
                        
                        if not name_col or not phone_col:
                            return render_template("client_send_customer.html", 
                                                 business=business,
                                                 error="Excel file must contain 'Customer Name' and 'WhatsApp Number' columns.")
                        
                        # Process each row
                        success_count = 0
                        error_count = 0
                        errors = []
                        
                        for index, row in df.iterrows():
                            try:
                                name = str(row[name_col]).strip()
                                phone = str(row[phone_col]).strip()
                                
                                if pd.isna(row[name_col]) or pd.isna(row[phone_col]) or not name or not phone:
                                    error_count += 1
                                    errors.append(f"Row {index + 2}: Missing name or phone")
                                    continue
                                
                                # Clean phone number (remove any non-digits)
                                import re
                                phone = re.sub(r'\D', '', phone)
                                
                                if len(phone) < 10:
                                    error_count += 1
                                    errors.append(f"Row {index + 2}: Invalid phone number")
                                    continue
                                
                                # Send WhatsApp message
                                success, message = send_review_template_sigmo(phone=full_phone,
                                    customer_name=name,
                                    business_name=business["name"],
                                    review_link=review_link)


                                if success:
                                    success_count += 1
                                else:
                                    error_count += 1
                                    errors.append(f"Row {index + 2}: {message}")
                                
                            except Exception as e:
                                error_count += 1
                                errors.append(f"Row {index + 2}: {str(e)}")
                        
                        # Prepare result message
                        result_message = f"Processed {success_count + error_count} records. "
                        result_message += f"Successfully sent: {success_count}, Errors: {error_count}"
                        
                        if errors and len(errors) <= 5:
                            result_message += f"\nErrors: {'; '.join(errors)}"
                        elif errors:
                            result_message += f"\nFirst 5 errors: {'; '.join(errors[:5])}"
                        
                        if success_count > 0:
                            return render_template("client_send_customer.html", 
                                                 business=business,
                                                 success=result_message)
                        else:
                            return render_template("client_send_customer.html", 
                                                 business=business,
                                                 error=result_message)
                    
                    except Exception as e:
                        return render_template("client_send_customer.html", 
                                             business=business,
                                             error=f"Error reading Excel file: {str(e)}")
                
            except Exception as e:
                print(f"Error in client_send_customer: {str(e)}")
                return render_template("client_send_customer.html", 
                                     business=business,
                                     error=f"An error occurred: {str(e)}")
        
        # GET request - show the form
        return render_template("client_send_customer.html", business=business)
        
    except Exception as e:
        print(f"Database error in client_send_customer: {str(e)}")
        return redirect("/login?error=Database error")

# Admin routes for client management
@app.route("/admin/create-client", methods=["GET", "POST"])
def admin_create_client():
    if not session.get("logged_in"):
        return redirect("/login")
    
    if request.method == "POST":
        business_id = request.form.get("business_id", "").strip()
        email = request.form.get("email", "").strip()
        
        if not business_id or not email:
            businesses = get_all_businesses()
            return render_template("admin_create_client.html", 
                                 businesses=businesses,
                                 error="Business and email are required")
        
        # Check if client already exists
        existing_client = get_client_by_email(email)
        if existing_client:
            businesses = get_all_businesses()
            return render_template("admin_create_client.html", 
                                 businesses=businesses,
                                 error="A client with this email already exists")
        
        # Generate temporary password
        import secrets
        import string
        temp_password = ''.join(secrets.choice(string.ascii_letters + string.digits + "!@#$%^&*") for _ in range(12))
        
        # Create client
        client = create_client(business_id, email, temp_password)
        
        if client:
            # Send email with credentials
            try:
                business = get_business(business_id)
                send_client_credentials_email(email, temp_password, business)
                return redirect("/admin?success=Client created successfully and credentials sent via email")
            except Exception as e:
                print(f"Error sending email: {str(e)}")
                # Still redirect with success but mention email issue
                return redirect(f"/admin?success=Client created successfully. Email sending failed - please provide credentials manually. Temporary password: {temp_password}")
        else:
            businesses = get_all_businesses()
            return render_template("admin_create_client.html", 
                                 businesses=businesses,
                                 error="Failed to create client")
    
    businesses = get_all_businesses()
    return render_template("admin_create_client.html", businesses=businesses)

def send_client_credentials_email(email, temp_password, business):
    """Send client login credentials via Zoho Mail API"""

    subject = f'Your Login Credentials - {business["name"]} Dashboard'

    html_content = f"""
    <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <div style="max-width: 600px; margin: 0 auto; padding: 20px; background-color: #f9f9f9; border-radius: 10px;">
                <div style="background: linear-gradient(135deg, #D4AF37 0%, #B8941F 100%); padding: 30px; text-align: center; border-radius: 10px 10px 0 0;">
                    <h1 style="color: white; margin: 0; font-size: 26px;">🔑 Your Dashboard Access</h1>
                </div>

                <div style="background-color: white; padding: 30px; border-radius: 0 0 10px 10px;">
                    <p style="font-size: 16px;">Hello,</p>

                    <p style="font-size: 16px;">
                        Your client dashboard account has been created for
                        <strong style="color: #D4AF37;">{business["name"]}</strong>.
                    </p>

                    <div style="background-color: #f5f5f5; padding: 20px; border-left: 4px solid #D4AF37; border-radius: 3px; margin: 25px 0;">
                        <p style="margin: 0 0 10px 0; font-size: 15px;">
                            <strong>🔑 Login Details:</strong>
                        </p>
                        <p style="margin: 5px 0; font-size: 15px;">
                            <strong>Email:</strong> {email}
                        </p>
                        <p style="margin: 5px 0; font-size: 15px;">
                            <strong>Temporary Password:</strong>
                            <code style="background: #e0e0e0; padding: 4px 8px; border-radius: 4px;">
                                {temp_password}
                            </code>
                        </p>
                    </div>

                    <div style="text-align: center; margin: 30px 0;">
                        <a href="{AUREUM_DOMAIN}/login"
                           style="display: inline-block;
                                  background: linear-gradient(135deg, #D4AF37 0%, #B8941F 100%);
                                  color: white;
                                  padding: 15px 30px;
                                  text-decoration: none;
                                  border-radius: 8px;
                                  font-weight: 600;
                                  font-size: 16px;">
                            🚀 Access Your Dashboard
                        </a>
                    </div>

                    <div style="background-color: #fff3cd; border: 1px solid #ffeaa7; border-radius: 5px; padding: 15px; margin: 20px 0;">
                        <p style="margin: 0; font-size: 14px; color: #856404;">
                            <strong>🔒 Security Notice:</strong>
                            For security reasons, you will be required to change your password on first login.
                        </p>
                    </div>

                    <p style="font-size: 15px; margin-top: 30px;">
                        Best regards,<br>
                        <strong style="color: #D4AF37;">Aureum Reputations Team</strong>
                    </p>
                </div>

                <p style="text-align: center; color: #999; font-size: 12px; margin-top: 20px;">
                    This is an automated email. Please do not reply.<br>
                    © 2025 Aureum Reputations. All rights reserved.
                </p>
            </div>
        </body>
    </html>
    """

    # ✅ Send via Zoho API (NO SMTP)
    send_zoho_email(
        to_email=email,
        subject=subject,
        html_content=html_content
    )

@app.route("/admin/delete-client/<client_id>", methods=["POST"])
def admin_delete_client(client_id):
    if not session.get("logged_in"):
        return redirect("/login")
    
    try:
        # Get client info before deletion
        client = get_client_by_id(client_id)
        if not client:
            return redirect("/admin?error=Client not found")
        
        client_email = client.get('email', 'Unknown')
        
        # Delete the client
        result = delete_client(client_id)
        
        return redirect(f"/admin?success=Client account '{client_email}' deleted successfully")
        
    except Exception as e:
        print(f"Error deleting client: {str(e)}")
        return redirect("/admin?error=Error occurred while deleting client account")


@app.route("/dashboard/<business_id>")
def dashboard(business_id):
    if not session.get("logged_in"):
        return redirect("/login")
    reviews = get_reviews(business_id)
    business = get_business(business_id)
    count = len(reviews)
    return render_template("dashboard.html", business=business, reviews=reviews, count=count)



@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username_or_email = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        
        if not username_or_email or not password:
            return render_template("login.html", error="Username/Email and password are required")
        
        # First, try admin login
        if username_or_email == "admin" and password == "admin123":
            session["logged_in"] = True
            return redirect("/admin")
        
        # Then, try client login (check if it's an email format)
        if "@" in username_or_email:
            client, message = authenticate_client(username_or_email, password)
            
            if client:
                session["client_logged_in"] = True
                session["client_id"] = client["id"]
                session["client_email"] = client["email"]
                session["business_id"] = client["business_id"]
                
                # Check if password is temporary
                if client.get("is_temporary_password", False):
                    return redirect("/client-change-password?first_login=true")
                else:
                    return redirect("/client-dashboard")
        
        # If neither admin nor client login worked
        return render_template("login.html", error="Invalid username/email or password")

    return render_template("login.html")


@app.route("/logout")
def logout():
    session.pop("logged_in", None)
    return redirect("/login")

@app.route("/send-customer", methods=["GET", "POST"])
def send_customer():
    """Page to send WhatsApp review requests to customers"""
    if request.method == "POST":
        try:
            # Check if it's a bulk upload (Excel file) or single customer
            excel_file = request.files.get('excel_file')
            
            if excel_file and excel_file.filename:
                # Handle bulk upload from Excel file
                return handle_bulk_upload(excel_file)
            else:
                # Handle single customer submission
                return handle_single_customer()
                
        except Exception as e:
            print(f"Error in send_customer: {str(e)}")
            try:
                businesses = get_all_businesses()
            except:
                businesses = []
            return render_template("send_customer.html", 
                                 error=f"An error occurred: {str(e)}",
                                 businesses=businesses)
    
    # GET request - show the form
    try:
        businesses = get_all_businesses()
        return render_template("send_customer.html", businesses=businesses)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return render_template("send_customer.html", 
                             error="Unable to load businesses. Please check database connection.",
                             businesses=[])

def handle_single_customer():
    """Handle single customer WhatsApp message sending"""
    customer_name = request.form.get("name", "").strip()
    phone = request.form.get("phone", "").strip()
    country_code = request.form.get("country_code", "+91").strip()
    business_id = request.form.get("business_id", "").strip()
    
    # Combine country code with phone number
    if phone and not phone.startswith("+"):
        phone = country_code + phone
    
    # Validation
    if not all([customer_name, phone, business_id]):
        try:
            businesses = get_all_businesses()
        except:
            businesses = []
        return render_template("send_customer.html", 
                             error="All fields are required.",
                             businesses=businesses)
    
    # Get business details
    try:
        business = get_business(business_id)
        if not business:
            businesses = get_all_businesses()
            return render_template("send_customer.html", 
                                 error="Invalid business selected.",
                                 businesses=businesses)
    except Exception as e:
        return render_template("send_customer.html", 
                             error=f"Database error: {str(e)}",
                             businesses=[])
    
    # Send WhatsApp message
    # Generate review link
    review_link = generate_feedback_link_for_phone(
        phone=phone,
        business_id=business["id"],
        customer_name=customer_name
    )

    if not review_link:
        return render_template(
            "send_customer.html",
            error="Failed to generate review link.",
            businesses=get_all_businesses()
        )

    # Send WhatsApp template via SIGMO
    success = send_review_template_sigmo(
        phone=phone,
        customer_name=customer_name,
        business_name=business["name"],
        review_link=review_link
    )

    message = (
        "WhatsApp review request sent successfully"
        if success else
        "Failed to send WhatsApp message"
    )

    
    try:
        businesses = get_all_businesses()
    except:
        businesses = []
    
    if success:
        return render_template("send_customer.html", 
                             success=message,
                             businesses=businesses)
    else:
        return render_template("send_customer.html", 
                             error=message,
                             businesses=businesses)

def handle_bulk_upload(excel_file):
    """Handle bulk upload from Excel file"""
    import pandas as pd
    import io
    
    try:
        business_id = request.form.get("business_id", "").strip()
        
        if not business_id:
            try:
                businesses = get_all_businesses()
            except:
                businesses = []
            return render_template("send_customer.html", 
                                 error="Please select a business for bulk upload.",
                                 businesses=businesses)
        
        # Get business details
        try:
            business = get_business(business_id)
            if not business:
                businesses = get_all_businesses()
                return render_template("send_customer.html", 
                                     error="Invalid business selected.",
                                     businesses=businesses)
        except Exception as e:
            return render_template("send_customer.html", 
                                 error=f"Database error: {str(e)}",
                                 businesses=[])
        
        # Read Excel file
        try:
            # Read the Excel file
            df = pd.read_excel(io.BytesIO(excel_file.read()))
            
            # Find the name and phone columns (case insensitive)
            name_col = None
            phone_col = None
            
            for col in df.columns:
                col_lower = str(col).lower()
                if 'name' in col_lower and name_col is None:
                    name_col = col
                elif ('phone' in col_lower or 'whatsapp' in col_lower or 'number' in col_lower) and phone_col is None:
                    phone_col = col
            
            if name_col is None or phone_col is None:
                try:
                    businesses = get_all_businesses()
                except:
                    businesses = []
                return render_template("send_customer.html", 
                                     error="Excel file must contain 'Customer Name' and 'WhatsApp Number' columns.",
                                     businesses=businesses)
            
            # Process each row
            success_count = 0
            error_count = 0
            errors = []
            
            for index, row in df.iterrows():
                try:
                    customer_name = str(row[name_col]).strip()
                    phone = str(row[phone_col]).strip()
                    
                    # Skip empty rows
                    if not customer_name or not phone or customer_name.lower() == 'nan' or phone.lower() == 'nan':
                        continue
                    
                    # Clean phone number - remove any non-digit characters
                    cleaned_phone = ''.join(filter(str.isdigit, phone))
                    
                    # Validate phone number format
                    if len(cleaned_phone) < 10:
                        errors.append(f"Row {index + 2}: Phone number too short - {phone}")
                        error_count += 1
                        continue
                    
                    # Check if it starts with common country codes
                    valid_country_codes = ['91', '1', '44', '971', '966', '65', '60', '61', '49', '33', '39', '34', '7', '86', '81', '82', '55', '52', '27', '234']
                    has_valid_country_code = False
                    
                    for code in sorted(valid_country_codes, key=len, reverse=True):  # Check longer codes first
                        if cleaned_phone.startswith(code):
                            has_valid_country_code = True
                            break
                    
                    if not has_valid_country_code:
                        errors.append(f"Row {index + 2}: Phone number must start with a valid country code (e.g., 91, 1, 44) - {phone}")
                        error_count += 1
                        continue
                    
                    # Add + sign for WhatsApp API
                    final_phone = "+" + cleaned_phone
                    
                    # Generate review link
                    review_link = generate_feedback_link_for_phone(
                        phone=final_phone,
                        business_id=business["id"],
                        customer_name=customer_name
                    )

                    if not review_link:
                        error_count += 1
                        errors.append(f"Row {index + 2} ({customer_name}): Failed to generate review link")
                        continue

                        # Send WhatsApp template via SIGMO
                    success = send_review_template_sigmo(
                        phone=final_phone,
                        customer_name=customer_name,
                        business_name=business["name"],
                        review_link=review_link
                    )
    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"Row {index + 2} ({customer_name}): Failed to send WhatsApp message")

                    
                    if success:
                        success_count += 1
                    else:
                        error_count += 1
                        errors.append(f"Row {index + 2} ({customer_name}): {message}")
                    
                    # Add small delay to avoid rate limiting
                    import time
                    time.sleep(0.5)
                    
                except Exception as e:
                    error_count += 1
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            # Prepare result message
            result_message = f"Bulk upload completed! Successfully sent: {success_count}, Failed: {error_count}"
            
            if errors and len(errors) <= 10:  # Show first 10 errors
                result_message += "\n\nErrors:\n" + "\n".join(errors[:10])
            elif errors:
                result_message += f"\n\n{len(errors)} errors occurred. First 10:\n" + "\n".join(errors[:10])
            
            try:
                businesses = get_all_businesses()
            except:
                businesses = []
            
            if success_count > 0:
                return render_template("send_customer.html", 
                                     success=result_message,
                                     businesses=businesses)
            else:
                return render_template("send_customer.html", 
                                     error=result_message,
                                     businesses=businesses)
                
        except Exception as e:
            try:
                businesses = get_all_businesses()
            except:
                businesses = []
            return render_template("send_customer.html", 
                                 error=f"Error reading Excel file: {str(e)}",
                                 businesses=businesses)
            
    except Exception as e:
        try:
            businesses = get_all_businesses()
        except:
            businesses = []
        return render_template("send_customer.html", 
                             error=f"Error processing bulk upload: {str(e)}",
                             businesses=businesses)


@app.route("/add-business", methods=["GET", "POST"])
def add_business():
    """Admin page to add new businesses"""
    if not session.get("logged_in"):
        return redirect("/login")
    
    if request.method == "POST":
        try:
            business_name = request.form.get("business_name", "").strip()
            google_review_link = request.form.get("google_review_link", "").strip()
            
            # Validation
            if not all([business_name, google_review_link]):
                return render_template("add_business.html", 
                                     error="Business name and Google Maps link are required.")
            
            # Validate Google Maps URL (including shortened links and direct review format)
            if not any(domain in google_review_link.lower() for domain in [
                "google.com/maps", 
                "maps.google.com", 
                "maps.app.goo.gl",
                "goo.gl",
                "g.page/r/"
            ]):
                return render_template("add_business.html", 
                                     error="Please provide a valid Google Maps URL or direct review link (g.page/r/CODE/review).")
            
            # Save to database (Place ID will be extracted automatically)
            result = save_business(business_name, google_review_link)
            
            # Check if Place ID was extracted successfully
            if result.data and len(result.data) > 0:
                extracted_place_id = result.data[0].get('google_place_id', '')
                if extracted_place_id:
                    return render_template("add_business.html", 
                                         success=f"Business '{business_name}' added successfully! Place ID: {extracted_place_id}")
                else:
                    return render_template("add_business.html", 
                                         success=f"Business '{business_name}' added, but Place ID could not be extracted. You may need to update it manually.",
                                         warning=True)
            else:
                return render_template("add_business.html", 
                                     success=f"Business '{business_name}' added successfully!")
                
        except Exception as e:
            print(f"Error adding business: {str(e)}")
            return render_template("add_business.html", 
                                 error=f"An error occurred: {str(e)}")
    
    # GET request - show the form
    return render_template("add_business.html")

@app.route("/delete-business/<business_id>", methods=["POST"])
def delete_business_route(business_id):
    """Delete a business and all its reviews (admin only)"""
    if not session.get("logged_in"):
        return redirect("/login")
    
    try:
        print(f"Attempting to delete business with ID: {business_id}")
        
        # First, check if the business exists
        business = get_business(business_id)
        if not business:
            print(f"Business with ID {business_id} not found")
            return redirect("/admin?error=Business not found")
        
        business_name = business.get('name', 'Unknown')
        
        # Check how many reviews will be deleted
        reviews = get_reviews(business_id)
        review_count = len(reviews) if reviews else 0
        
        print(f"Deleting business: {business_name} (with {review_count} reviews)")
        
        # Delete the business (this will also delete all reviews)
        result = delete_business(business_id)
        print(f"Delete operation completed")
        
        # Create success message
        if review_count > 0:
            success_msg = f"Business '{business_name}' and {review_count} associated reviews deleted successfully"
        else:
            success_msg = f"Business '{business_name}' deleted successfully"
            
        return redirect(f"/admin?success={success_msg}")
            
    except Exception as e:
        error_msg = str(e)
        print(f"Error deleting business: {error_msg}")
        
        # Handle specific foreign key constraint error
        if "foreign key constraint" in error_msg.lower():
            return redirect("/admin?error=Cannot delete business: it has associated reviews. Please delete reviews first.")
        else:
            return redirect("/admin?error=Error occurred while deleting business")

@app.route("/edit-business/<business_id>", methods=["GET", "POST"])
def edit_business_route(business_id):
    """Edit an existing business (admin only)"""
    if not session.get("logged_in"):
        return redirect("/login")
    
    try:
        # Get the business data
        business = get_business(business_id)
        if not business:
            return redirect("/admin?error=Business not found")
        
        if request.method == "POST":
            # Handle form submission
            business_name = request.form.get("business_name", "").strip()
            google_review_link = request.form.get("google_review_link", "").strip()
            
            # Validation
            if not business_name:
                return render_template("edit_business.html", 
                                     business=business,
                                     error="Business name is required")
            
            if not google_review_link:
                return render_template("edit_business.html", 
                                     business=business,
                                     error="Google review link is required")
            
            # Validate Google Maps URL (including direct review format)
            if "google.com/maps" not in google_review_link and "goo.gl" not in google_review_link and "maps.app.goo.gl" not in google_review_link and "g.page/r/" not in google_review_link:
                return render_template("edit_business.html", 
                                     business=business,
                                     error="Please provide a valid Google Maps URL or direct review link (g.page/r/CODE/review)")
            
            try:
                # Update the business
                result = update_business(business_id, business_name, google_review_link)
                print(f"Business updated successfully: {result}")
                
                return redirect(f"/admin?success=Business '{business_name}' updated successfully")
                
            except Exception as e:
                error_msg = str(e)
                print(f"Error updating business: {error_msg}")
                return render_template("edit_business.html", 
                                     business=business,
                                     error="Error occurred while updating business")
        
        # GET request - show the edit form
        return render_template("edit_business.html", business=business)
        
    except Exception as e:
        print(f"Error in edit_business_route: {str(e)}")
        return redirect("/admin?error=Error occurred while accessing business")

@app.route("/debug-routes")
def debug_routes():
    """Debug endpoint to see all registered routes"""
    routes = []
    for rule in app.url_map.iter_rules():
        routes.append({
            'endpoint': rule.endpoint,
            'methods': list(rule.methods),
            'rule': str(rule)
        })
    return jsonify(routes)

@app.route("/test-route")
def test_route():
    return "Test route is working!"



def process_messages(messages):
    for msg in messages:
        text = msg["message"].strip().lower()
        phone = msg["phone"]
        timestamp = msg["createdAt"]

        if text in VALID_REPLIES:
            handle_feedback(phone, text)

        update_last_processed_time(timestamp)

def handle_feedback(phone, response):
    business_id = get_business_id_from_phone(phone)

    review_link = generate_feedback_link_for_phone(
        phone=phone,
        business_id=business["id"],
        customer_name=name
    )

    send_link_campaign(phone, review_link)


import requests
import os

SIGMO_API_KEY = os.getenv("SIGMO_API_KEY")  # same key you tested in curl
SIGMO_SENDER = "916301952600"
SIGMO_TEMPLATE_ID = "review_hyi3vjyaup3djy0q"



def send_review_template_sigmo(phone, customer_name, business_name, review_link):
    """
    Send WhatsApp review request using TrustSignal Single API
    Uses message_type = text_var (CONFIRMED WORKING)
    """

    url = (
        "https://wpapi.trustsignal.io/api/v1/whatsapp/single"
        f"?api_key={SIGMO_API_KEY}"
    )

    payload = {
        "message_type": "text_var",
        "sender": SIGMO_SENDER,
        "to": phone,  # digits only preferred (no +)
        "template_id": SIGMO_TEMPLATE_ID,
        "sample": {
            "header": "Hello",
            "bodyvar": [
                customer_name,   # {{1}}
                business_name,   # {{2}}
                review_link      # {{3}}
            ]
        }
    }

    headers = {
        "Content-Type": "application/json"
    }

    try:
        response = requests.post(
            url,
            json=payload,
            headers=headers,
            timeout=15
        )

        data = response.json()

        # 🔍 Debug logs (keep while testing)
        print("SIGMO PAYLOAD:", payload)
        print("SIGMO RESPONSE:", data)

        if response.status_code == 200 and data.get("success") is True:
            return True, "WhatsApp message sent successfully"

        return False, data.get("errors", [{}])[0].get(
            "message", "Unknown TrustSignal error"
        )

    except Exception as e:
        print("SIGMO ERROR:", str(e))
        return False, str(e)

   
@app.errorhandler(404)
def not_found(e):
    """Handle 404 errors"""
    return jsonify({
        'error': '404 Not Found',
        'message': 'The requested URL was not found on the server.',
        'available_routes': [str(rule) for rule in app.url_map.iter_rules()]
    }), 404

if __name__ == '__main__':
    # Get configuration from environment variables
    debug_mode = os.getenv('FLASK_DEBUG', 'False') == 'True'
    port = int(os.getenv('PORT', 5000))
    host = os.getenv('HOST', '0.0.0.0')

    # Run the application
    app.run(debug=debug_mode, host=host, port=port)


