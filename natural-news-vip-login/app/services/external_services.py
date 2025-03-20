import requests
from fastapi import HTTPException
from app.schemas.user import PlatformEnum, TierEnum  # Import Enums only
import datetime

# from app.services.user_service import calculate_total_spent
from app.core.config import ACTIVE_CAMPAIGN_API_KEY, ACTIVE_CAMPAIGN_URL, SHOPIFY_STORE_URL, SHOPIFY_API_KEY
import random

def get_shopify_orders(email: str):
    """Fetch orders by email within the last 3 months from Shopify and calculate total amount"""
    three_months_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%S%z")
    
    url = f"{SHOPIFY_STORE_URL}/admin/api/2025-01/orders.json?status=any&email={email}&created_at_min={three_months_ago}"
    headers = {"X-Shopify-Access-Token": SHOPIFY_API_KEY}

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        orders = data.get("orders", [])

        # Sum up current_total_price from all orders
        total_amount = round(sum(float(str(order.get("current_total_price", "0"))) for order in orders), 2)

        return {
            "total_amount": total_amount,
            "orders": orders
        }

    return {"total_amount": 0, "orders": []}  # Return empty if no orders found
def check_active_campaign(email: str):
    """Check if email exists in ActiveCampaign"""
    headers = {"Api-Token": ACTIVE_CAMPAIGN_API_KEY}
    url = f"{ACTIVE_CAMPAIGN_URL}/api/3/contacts?email={email}"
    
    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        data = response.json()
        if data.get("contacts"):
            return data["contacts"][0]  # Return user data
    return None  # Not found

def check_shopify(email: str):
    """Check if email exists in Shopify"""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2025-01/customers/search.json?query=email:{email}"
    # three_months_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%S%z")

    # url = f"{SHOPIFY_STORE_URL}/admin/api/2025-01/orders.json?status=any&email={email}&created_at_min={three_months_ago}"
    orders = get_shopify_orders(email)

    headers = {"X-Shopify-Access-Token": SHOPIFY_API_KEY}

    response = requests.get(url, headers=headers)
    # orders = response.json()
    # print('----',orders.get("orders"))
    if response.status_code == 200:
        data = response.json()
        if data.get("customers"):
            customer = data["customers"][0]
            customer["platform"] = PlatformEnum.SHOPIFY
            customer['total_spent'] = orders['total_amount']
            return customer
    return None  # Not found

def get_user_tier(total_spent: float) -> str:
    """
    Determine the user's tier based on total spent.
    
    - BRONZE: Default tier if total_spent < 100
    - SILVER: If total_spent is between 100 and 499
    - GOLD: If total_spent is between 500 and 999
    - PLATINUM: If total_spent >= 1000
    """
    if total_spent >= 2499:
        return "PLATINUM"
    elif total_spent >= 999:
        return "GOLD"
    elif total_spent >= 99:
        return "SILVER"
    else:
        return "BRONZE"  # Default tier

