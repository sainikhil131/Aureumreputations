#!/usr/bin/env python3

from supabase import create_client
import requests
from datetime import datetime

# ================= CONFIG =================

SUPABASE_URL = "https://YOUR_PROJECT_ID.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im56a3JneHZzdGR3bWNrcXl1b3ZxIiwicm9sZSI6ImFub24iLCJpYXQiOjE3NjI4NjM4NTAsImV4cCI6MjA3ODQzOTg1MH0.AUGiQs-fM7IKcUFGQwNbV7M-1KvzoI1ttOW-STjuRMI"

AISENSY_API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpZCI6IjY5MmIwY2ZkYjJiZmFiMGQ1NzNhYzczMiIsIm5hbWUiOiJBdXJldW0gUmVwdXRhdGlvbnMiLCJhcHBOYW1lIjoiQWlTZW5zeSIsImNsaWVudElkIjoiNjkyYjBjZmRiMmJmYWIwZDU3M2FjNzJkIiwiYWN0aXZlUGxhbiI6IkZSRUVfRk9SRVZFUiIsImlhdCI6MTc2NDQyOTA1M30.ajkNwyvhW4N_Axw0FYuye7Z3AC4t_zxjZjVkczhuJGA"
AISENSY_MESSAGES_URL = "https://backend.aisensy.com/messages"
AISENSY_SEND_URL = "https://backend.aisensy.com/campaign/t1/api/v2"

FLASK_BASE_URL = "https://aureumreputations.com"

VALID_REPLIES = {"loved it", "okay", "needs improvement"}

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)

# ================= HELPERS =================

def get_last_processed_time():
    res = supabase.table("aisensy_state").select("last_message_time").eq("id", 1).single().execute()
    return datetime.fromisoformat(res.data["last_message_time"].replace("Z", ""))

def update_last_processed_time(ts):
    supabase.table("aisensy_state").update({
        "last_message_time": ts.isoformat()
    }).eq("id", 1).execute()

def already_sent_today(phone):
    res = supabase.table("processed_feedback") \
        .select("phone") \
        .eq("phone", phone) \
        .eq("date", datetime.utcnow().date().isoformat()) \
        .execute()
    return len(res.data) > 0

def mark_sent(phone):
    supabase.table("processed_feedback").insert({
        "phone": phone,
        "date": datetime.utcnow().date().isoformat()
    }).execute()

def get_business_id_from_phone(phone):
    res = supabase.table("customers") \
        .select("business_id") \
        .eq("phone", phone) \
        .single() \
        .execute()
    return res.data["business_id"] if res.data else None

def generate_review_link(phone, business_id):
    r = requests.post(
        f"{FLASK_BASE_URL}/generate-feedback-link",
        json={
            "business_id": business_id,
            "customer_phone": phone
        },
        timeout=10
    )
    r.raise_for_status()
    return r.json()["short_url"]

def send_link_campaign(phone, link):
    payload = {
        "apiKey": AISENSY_API_KEY,
        "campaignName": "link",
        "destination": phone,
        "userName": "Aureum Reputations",
        "templateParams": [link],
        "source": "auto-feedback"
    }

    r = requests.post(AISENSY_SEND_URL, json=payload, timeout=10)
    r.raise_for_status()
    print("✅ Link sent to", phone)

# ================= MAIN =================

def poll():
    since = get_last_processed_time()
    print("⏱ Polling since:", since)

    headers = {
        "Authorization": f"Bearer {AISENSY_API_KEY}"
    }

    params = {"from": since.isoformat()}

    r = requests.get(AISENSY_MESSAGES_URL, headers=headers, params=params, timeout=10)
    r.raise_for_status()

    messages = r.json().get("data", [])
    print("📨 Messages:", len(messages))

    for msg in messages:
        phone = msg.get("phone")
        text = msg.get("message", "").strip().lower()
        created_at = datetime.fromisoformat(msg["createdAt"].replace("Z", ""))

        update_last_processed_time(created_at)

        if text not in VALID_REPLIES:
            continue

        if already_sent_today(phone):
            continue

        business_id = get_business_id_from_phone(phone)
        if not business_id:
            print("❌ No business mapped for:", phone)
            continue

        link = generate_review_link(phone, business_id)
        send_link_campaign(phone, link)
        mark_sent(phone)

if __name__ == "__main__":
    poll()
