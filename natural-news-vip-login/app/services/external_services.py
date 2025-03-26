import requests
from fastapi import HTTPException
from app.schemas.user import PlatformEnum, TierEnum  # Import Enums only
import datetime

# from app.services.user_service import calculate_total_spent
from app.core.config import ACTIVE_CAMPAIGN_API_KEY, ACTIVE_CAMPAIGN_URL, SHOPIFY_STORE_URL, SHOPIFY_API_KEY
import random

#####################################################SHOPIFY#########################################################
HEADERS_SHOPIFY = {"X-Shopify-Access-Token": SHOPIFY_API_KEY}
def check_shopify(email: str):
    """Check if email exists in Shopify"""
    url = f"{SHOPIFY_STORE_URL}/admin/api/2025-01/customers/search.json?query=email:{email}"
    # three_months_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%S%z")

    # url = f"{SHOPIFY_STORE_URL}/admin/api/2025-01/orders.json?status=any&email={email}&created_at_min={three_months_ago}"
    orders = get_shopify_orders(email)

    response = requests.get(url, headers=HEADERS_SHOPIFY)
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


def get_shopify_orders(email: str):
    """Fetch orders by email within the last 3 months from Shopify and calculate total amount"""
    three_months_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%S%z")
    
    url = f"{SHOPIFY_STORE_URL}/admin/api/2025-01/orders.json?status=any&email={email}&created_at_min={three_months_ago}"

    response = requests.get(url, headers=HEADERS_SHOPIFY)

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


#####################################################ACTIVE-CAMPAIGN#########################################################
HEADERS_ACTIVE_CAMPAIGN = {
    "Api-Token": ACTIVE_CAMPAIGN_API_KEY,
    "Content-Type": "application/json"
    }

def check_active_campaign(email: str):
    """Check if email exists in ActiveCampaign"""

    url = f"{ACTIVE_CAMPAIGN_URL}/api/3/users/email/{email}"
    response = requests.get(url, headers=HEADERS_ACTIVE_CAMPAIGN)
    if response.status_code == 200:
        data = response.json()
        user = data.get("user", {})
        return user  # Return the user details if found

    return None  # Return None if email not found

def get_all_orders_by_customer_email(customer_email: str):
    orders = []
    url = f'{ACTIVE_CAMPAIGN_URL}/api/3/ecomOrders?filters[email]={customer_email}'
    response = requests.get(url, headers=HEADERS_ACTIVE_CAMPAIGN)
    if response.status_code == 200:
        data = response.json()
        orders.extend(data.get('ecomOrders', []))
    return orders

def calculate_total_spent(orders):
    total_spent = 0.0
    three_months_ago = (datetime.datetime.utcnow() - datetime.timedelta(days=90)).strftime("%Y-%m-%dT%H:%M:%S%z")
    for order in orders:
        order_date = datetime.datetime.strptime(order['externalCreatedDate'], "%Y-%m-%dT%H:%M:%S%z")
        if order_date >= three_months_ago:
            total_spent += float(order['totalPrice'])
    return total_spent

def get_total_spent_last_three_months_active_campaign(email):
    """
    Calculate the total amount spent by the customer in the last three months.
    """

    orders = get_all_orders_by_customer_email(email)
    total_spent = calculate_total_spent(orders)
    return total_spent

######################################################

def determine_user_tier_and_reward(email):
    user_data_shopify = check_shopify(email)
    user_data_active_campaign = check_active_campaign(email)
    
    if not user_data_shopify and not user_data_active_campaign:
        raise HTTPException(status_code=404, detail="User not found in ActiveCampaign or Shopify")
    
    if user_data_shopify:
        platform = user_data_shopify.get("platform", "SHOPIFY")
        total_spent_shopify = float(user_data_shopify.get("total_spent", 0))
    else:
        total_spent_shopify = 0.0
    
    if user_data_active_campaign:
        platform = "HRS"
    
    total_spent = total_spent_shopify
    tier = get_user_tier(total_spent)
    new_reward = get_tier_reward(tier)
    
    if user_data_shopify and user_data_active_campaign:
        platform = PlatformEnum.SHOPIFY_HRS
    
    return platform, tier, new_reward

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
    
def get_tier_reward(tier: TierEnum) -> int:
    """Returns the initial reward count based on the user's tier."""
    reward_mapping = {
        "BRONZE": 5,
        "SILVER": 10,
        "GOLD": 50,
        "PLATINUM": 99999  # Platinum gets unlimited (set a high number)
    }
    return reward_mapping.get(tier, 5)  # Default to Bronze reward

