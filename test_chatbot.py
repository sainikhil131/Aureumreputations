"""
Test script for Aureum Chatbot
Run this to test the chatbot responses without starting the full Flask app
"""

def get_chatbot_response(user_message, history):
    """Generate intelligent responses based on user input"""
    
    user_message = user_message.lower()
    
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


def test_chatbot():
    """Run test conversations"""
    print("=" * 60)
    print("AUREUM CHATBOT TEST SUITE")
    print("=" * 60)
    
    test_cases = [
        ("Hello", []),
        ("I need help with fake reviews", []),
        ("How can I grow my Google reviews?", []),
        ("What are your prices?", []),
        ("Tell me about your SEO services", []),
        ("What services do you offer?", []),
        ("How does it work?", []),
        ("How can I contact you?", []),
        ("Thank you", []),
        ("Goodbye", []),
    ]
    
    for i, (message, history) in enumerate(test_cases, 1):
        print(f"\n{'─' * 60}")
        print(f"Test {i}: {message}")
        print(f"{'─' * 60}")
        response = get_chatbot_response(message, history)
        print(f"Bot: {response}")
    
    print("\n" + "=" * 60)
    print("ALL TESTS COMPLETED")
    print("=" * 60)


if __name__ == "__main__":
    test_chatbot()

