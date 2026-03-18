import os
import time
import uuid
import requests
import base64
from django.conf import settings

class MomoPaymentProvider:
    """
    Handles MTN MoMo API interactions for the Collection product (RequestToPay).
    Supports a MOCK mode for instant testing without provisioning sandbox keys.
    """

    def __init__(self):
        self.mock_api = getattr(settings, 'MOMO_MOCK_API', True)
        self.base_url = getattr(settings, 'MOMO_BASE_URL', 'https://sandbox.momodeveloper.mtn.com')
        self.target_env = getattr(settings, 'MOMO_ENVIRONMENT', 'sandbox')
        self.subscription_key = getattr(settings, 'MOMO_COLLECTION_SUBSCRIPTION_KEY', '')
        self.api_user = getattr(settings, 'MOMO_API_USER_ID', '')
        self.api_key = getattr(settings, 'MOMO_API_KEY', '')
        self.currency = getattr(settings, 'MOMO_CURRENCY', 'RWF')
        
        # In-memory mock database to simulate delayed authorization
        self._mock_transactions = {}

    def get_access_token(self):
        """Fetches the Bearer Token from MTN API for Collections."""
        if self.mock_api:
            return "mock_bearer_token_12345"

        url = f"{self.base_url}/collection/token/"
        headers = {
            "Ocp-Apim-Subscription-Key": self.subscription_key,
        }
        auth_str = f"{self.api_user}:{self.api_key}"
        encoded_auth = base64.b64encode(auth_str.encode()).decode('utf-8')
        headers["Authorization"] = f"Basic {encoded_auth}"

        try:
            response = requests.post(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('access_token')
            return None
        except Exception as e:
            print(f"MoMo API Token Error: {e}")
            return None

    def request_to_pay(self, amount, phone_number, external_id, payer_message="Payment for Willystore"):
        """Triggers the USSD PIN prompt on the customer's phone."""
        # Clean phone number layout, e.g., standardizing to international format expected by MTN
        phone_number = ''.join(filter(str.isdigit, str(phone_number)))
        # For Rwanda sandbox, typically requires 250 prefix.
        if phone_number.startswith('07'):
            phone_number = f"25{phone_number}"
            
        reference_id = str(uuid.uuid4())

        if self.mock_api:
            # Simulate a successful push to phone and store mock status
            # We'll set it to PENDING initially, and then let it 'succeed' after a few seconds
            self._mock_transactions[reference_id] = {
                'status': 'PENDING',
                'created_at': time.time()
            }
            return reference_id, True

        token = self.get_access_token()
        if not token:
            return None, False

        url = f"{self.base_url}/collection/v1_0/requesttopay"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Reference-Id": reference_id,
            "X-Target-Environment": self.target_env,
            "Ocp-Apim-Subscription-Key": self.subscription_key,
            "Content-Type": "application/json"
        }

        payload = {
            "amount": str(amount),
            "currency": self.currency,
            "externalId": str(external_id),
            "payer": {
                "partyIdType": "MSISDN",
                "partyId": phone_number
            },
            "payerMessage": payer_message,
            "payeeNote": "Willystore Order"
        }

        try:
            response = requests.post(url, headers=headers, json=payload, timeout=15)
            # The API returns 202 Accepted on success.
            if response.status_code == 202:
                return reference_id, True
            return None, False
        except Exception as e:
            print(f"MoMo RequestToPay Error: {e}")
            return None, False

    def get_transaction_status(self, reference_id):
        """Polls the API to check if the user entered their PIN and completed payment."""
        if self.mock_api:
            # Simulate real-world delay for USSD prompt typing (e.g., waiting 6 seconds)
            mock_data = self._mock_transactions.get(reference_id)
            if not mock_data:
                return "FAILED"
            
            elapsed = time.time() - mock_data['created_at']
            if elapsed > 6:
                return "SUCCESSFUL"
            return "PENDING"

        token = self.get_access_token()
        if not token:
            return "FAILED"

        url = f"{self.base_url}/collection/v1_0/requesttopay/{reference_id}"
        headers = {
            "Authorization": f"Bearer {token}",
            "X-Target-Environment": self.target_env,
            "Ocp-Apim-Subscription-Key": self.subscription_key
        }

        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                data = response.json()
                return data.get('status', 'PENDING') # 'SUCCESSFUL', 'PENDING', 'FAILED'
            return "FAILED"
        except Exception as e:
            print(f"MoMo Status Error: {e}")
            return "PENDING"

# Global instantiator
momo_provider = MomoPaymentProvider()
