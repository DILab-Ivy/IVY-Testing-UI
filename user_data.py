#####################################################################################################################
# Description:
# The user_data.py module defines the user data and configuration settings.
# Class UserConfig is used so that other modules are able to
#   Usage: (1) Import: from user_data import UserConfig
#          (2) Call by: UserConfig.ACCESS_TOKEN, UserConfig.USERNAME
#####################################################################################################################


class UserConfig:
    USERNAME = "-"
    USER_NAME = "-"
    ACCESS_TOKEN = "-"

    @classmethod
    def set_user_info(cls, username, user_name, access_token):
        cls.USERNAME = username
        cls.USER_NAME = user_name
        cls.ACCESS_TOKEN = access_token
