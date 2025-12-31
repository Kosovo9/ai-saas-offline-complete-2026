import os
import mercadopago
import logging
from typing import Optional, Dict

logger = logging.getLogger("payment_service")

class PaymentService:
    """
    Antigravity V2 Payment Engine
    Exclusively using Mercado Pago and PayPal.
    """
    
    # Tier Prices in USD (Converted to numeric for MP)
    TIER_PRICES = {
        "FOUNDATION": 9999.00,
        "VISIONARY": 49999.00,
        "IMMORTAL": 199999.00
    }

    def __init__(self):
        self.access_token = os.getenv("MERCADO_PAGO_ACCESS_TOKEN")
        self.paypal_id = os.getenv("PAYPAL_HOSTED_BUTTON_ID")
        
        if self.access_token:
            self.sdk = mercadopago.SDK(self.access_token)
        else:
            self.sdk = None
            logger.warning("⚠️ MERCADO_PAGO_ACCESS_TOKEN not found in .env")

    def create_checkout_session(self, tier: str, user_email: Optional[str] = None, method: str = "mercadopago") -> str:
        """
        Creates a payment session using Mercado Pago or PayPal
        """
        tier = tier.upper()
        if tier not in self.TIER_PRICES:
            raise ValueError(f"Invalid tier: {tier}")

        price = self.TIER_PRICES[tier]
        frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")

        if method == "paypal":
            # For PayPal hosted buttons, we usually redirect to a specific URL with the button ID
            # This is a simplified direct link for hosted buttons
            return f"https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id={self.paypal_id}"

        if not self.sdk:
            raise Exception("Mercado Pago SDK not initialized. Check ACCESS_TOKEN.")

        # Mercado Pago Preference
        preference_data = {
            "items": [
                {
                    "title": f"ANTIGRAVITY V2 - {tier} TIER",
                    "quantity": 1,
                    "unit_price": price,
                    "currency_id": "USD" # Note: Mercado Pago might require local currency depending on account
                }
            ],
            "payer": {
                "email": user_email or "client@antigravity.ai"
            },
            "back_urls": {
                "success": f"{frontend_url}/chat?payment=success",
                "failure": f"{frontend_url}/?payment=failed",
                "pending": f"{frontend_url}/?payment=pending"
            },
            "auto_return": "approved",
            "external_reference": f"{tier}-{user_email}"
        }

        try:
            preference_response = self.sdk.preference().create(preference_data)
            preference = preference_response["response"]
            
            # Use 'init_point' for real payments, 'sandbox_init_point' for testing
            # returning init_point as user wants "real payments"
            return preference.get("init_point") or preference.get("sandbox_init_point")
            
        except Exception as e:
            logger.error(f"Mercado Pago Error: {e}")
            raise Exception(f"Failed to create Mercado Pago preference: {str(e)}")

# Global instance
payment_service = PaymentService()
