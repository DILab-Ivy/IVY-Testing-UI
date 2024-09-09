#####################################################################################################################
# Description:
# The constants.py module defines the constants used in multiple modules.
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
    "Planning": "https://planning.dilab-ivy.com/ivy/ask_question",
    "Semantic Networks Logic": "https://gpp.logic.dilab-ivy.com/ivy/ask_question",
    "MAGE": "https://mage.dilab-ivy.com/ivy/ask_question",
}
COGNITO_DOMAIN = "https://ivy.auth.us-east-1.amazoncognito.com"
REDIRECT_URL = (
    "http://localhost:8002/ask-ivy"
    if ON_LOCALHOST
    else "https://dev.dilab-ivy.com/ask-ivy"
)
EVALUATION_URL = (
    "http://localhost:8002/evaluation"
    if ON_LOCALHOST
    else "https://dev.dilab-ivy.com/evaluation"
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

EVALUATION_METRIC_DESCRIPTION = {
    "Correctness": "A response with high correctness should be factually accurate (based on TMK) to the question or context",
    "Completeness": "A response with high completeness satisfactorily covers all aspects of a user’s query, ensuring no critical information is left out",
    "Confidence": "A response with high confidence is indicated by straightforward, factual answers, while terms like 'not sure,' 'likely,' or 'could be' signify medium to low confidence",
    "Comprehensibility": "A response with high comprehensibility is easy to understand, useful and/or actionable. Reduces the likelihood of misunderstandings or need for follow-up questions",
    "Compactness": "A response with high compactness is clear and to the point, without unnecessary elaboration",
}

# Check environment variables
check_required_env_vars()
