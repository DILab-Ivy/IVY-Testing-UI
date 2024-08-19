#####################################################################################################################
# Description:
# The config.py module defines the configuration settings and constants.
# Class Config is used so that other modules are able to 
#   Usage: (1) Import: from constants import Config
#          (2) Call by: Config.ACCESS_TOKEN, Config.USERNAME 
# The module also includes validation for required environment variables.
#####################################################################################################################
import os
REQUIRED_ENV_VARS = ["COGNITO_LOCALHOST_CLIENT_SECRET", "COGNITO_PROD_CLIENT_SECRET"]

def check_required_env_vars():
    # Function for error handling if one of the required variables are not set
    for env_var in REQUIRED_ENV_VARS:
        if not os.getenv(env_var):
            raise ValueError(f"Please set the {env_var} environment variable")

# Define your configuration values
IS_DEVELOPER_VIEW = True
ON_LOCALHOST = False

SKILL_NAME_TO_MCM_URL = {
    "Classification": "https://classification.dilab-ivy.com/ivy/ask_question",
    "Incremental Concept Learning": "https://icl.dilab-ivy.com/ivy/ask_question",
    "Means End Analysis": "https://mea.dilab-ivy.com/ivy/ask_question",
    "Semantic Networks": "https://gpp.dilab-ivy.com/ivy/ask_question",
}
COGNITO_DOMAIN = "https://ivy.auth.us-east-1.amazoncognito.com"
REDIRECT_URL = (
    "http://localhost:8002/ask-ivy"
    if ON_LOCALHOST
    else "https://dev.dilab-ivy.com/ask-ivy"
)
CLIENT_ID = (
    "60p8a9bvteiihrd8g89r5ggabi" if ON_LOCALHOST else "2d7ah9kttong2hdlt4olhtao4d"
)
CLIENT_SECRET = (
    os.getenv("COGNITO_LOCALHOST_CLIENT_SECRET")
    if ON_LOCALHOST
    else os.getenv("COGNITO_PROD_CLIENT_SECRET")
)
LOGIN_URL = (
    COGNITO_DOMAIN
    + f"/login?response_type=code&client_id={CLIENT_ID}&redirect_uri={REDIRECT_URL}"
)
GET_ACCESS_TOKEN_URL = COGNITO_DOMAIN + "/oauth2/token"
GET_USER_INFO_URL = COGNITO_DOMAIN + "/oauth2/userInfo"

class Config:
    USERNAME = ""
    USER_NAME = ""
    ACCESS_TOKEN = ""

    @classmethod
    def set_user_info(cls, username, user_name, access_token):
        cls.USERNAME = username
        cls.USER_NAME = user_name
        cls.ACCESS_TOKEN = access_token

# Check environment variables
check_required_env_vars()
