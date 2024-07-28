############################################################################
# Test For local development only!
# Purpose: Quickly check if the app can communicate with Cognito
# PASS Condition: Success message indicating a successful connection
# FAIL Condition: Exception Message
############################################################################

import requests

# Cognito configuration
COGNITO_DOMAIN = "https://cognito-idp.us-east-1.amazonaws.com/us-east-1_aLwvXBfAm"

# URL to fetch JWKS (JSON Web Key Set)
JWKS_URL = f"{COGNITO_DOMAIN}/.well-known/jwks.json"

def check_cognito_communication():
    try:
        response = requests.get(JWKS_URL)
        response.raise_for_status()
        print("Success! Communicated with Cognito endpoint.")
        print("Response:", response.json())
    except Exception as e:
        print(f"Error communicating with Cognito: {str(e)}")

if __name__ == "__main__":
    check_cognito_communication()
