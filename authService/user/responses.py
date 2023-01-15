class UserResponses:
    def user_exists_error(self, data):
        return {
            "status": "FAILED",
            "message": "User with these credentials already exists.",
            "data": data,
        }

    def user_created_success(self, data: dict):
        return {
            "status": "CREATED",
            "message": "User Account successfully Created",
            "data": data,
        }

    def create_user_error(self, data: dict):
        d = data.keys()
        print(data.keys())
        s = [a for a in data.keys()]
        print(s)
        # d.append(data)
        return {
            "status": "FAILED",
            # "message": data[s[0]][0],
            "data": data
        }

    def password_mismatch_error(self):
        return {
            "status": "FAILED",
            "message": "Password Mismatch. Passwords do not match",
        }

    def verify_social_signup_exist_error(self, data):
        return {
            "status": "FAILED",
            "message": "User with this email already exists",
            "data": data,
        }

    def user_does_not_exist_error(self):
        return {
            "status": "FAILED",
            "message": "User does not exist",
        }

    def verify_social_signup_success(self, data):
        return {"status": "SUCCESS", "message": "User can proceed with Social Auth.", "data":data}

    def verify_social_signup_error(self, data):
        return {
            "status": "FAILED",
            "message": "Invalid fields. Please try again",
            "data": data,
        }

    def social_signup_success(self, data):
        return {
            "status": "CREATED",
            "message": "Social Sign Up Successful",
            "data": data,
        }

    def social_signup_error(self, data):

        d = data.keys()
        print(data.keys())
        s = [a for a in data.keys()]
        print(s)
        # d.append(data)
        return {
            "status": "FAILED",
            "message": data[s[0]][0],
            "data": data
        }


        # return {
        #     "status": "FAILED",
        #     "message": "Unable to create User Account. Please check fields and try again",
        #     "data": data,
        # }

    def user_update_success(self, data):
        return {
            "status": "SUCCESS",
            "message": "User Account Updated Successfully",
            "data": data,
        }

    def user_update_error(self):
        return {"status": "FAILED", "message": "User update failed"}

    def password_change_success(self):
        return {"status": "SUCCESS", "message": "Password successfully changed"}

    def password_and_confirmpassword_mismatch(self):
        return {
            "status": "FAILED",
            "message": "Password and confirm password must be the same",
        }

    def password_and_oldpasswordmismatch(self):
        return {
            "status": "FAILED",
            "message": "Old and New passwords must be different",
        }

    def incorrect_password_error(self):
        return {"status": "FAILED", "message": "Invalid Current Password"}

    def change_password_error(self, data):
        d = data.keys()
        print(data.keys())
        s = [a for a in data.keys()]
        print(s)
        return {
            "status": "FAILED",
            "message": data[s[0]][0],
            "data": data
        }
        

    def invalid_deactivate_user_action_error(self):
        return {"status": "FAILED", "message": "Action must be BLOCK or DELETE"}

    def block_user_success(self, data):
        return {
            "status": "SUCCESS",
            "message": "User account successfully blocked",
            "data": data,
        }

    def delete_user_success(self, data):
        return {
            "status": "SUCCESS",
            "message": "User account successfully deleted",
            "data": data,
        }

    def deactivate_user_error(self, data):
        return {
            "status": "FAILED",
            "message": "Unable to disable account. Check fields and try again",
            "data": data,
        }

    def invalid_unblock_action_error(self):
        return {"status": "FAILED", "message": "Action must be UNBLOCK"}

    def unblock_account_success(self, data):
        return {
            "status": "SUCCESS",
            "message": "User account successfully Unblocked",
            "data": data,
        }

    def unblock_user_error(self, data):
        return {
            "status": "FAILED",
            "message": "Unable to unblock account. Check fields and try again",
            "data": data,
        }

    def country_not_supported_error(self):
        return {
            "status": "FAILED",
            "message": "Oops! Selected country not currently supported."
        }

    def get_user_notifs_preferences(self, data: dict):
        return {
            "status": "SUCCES",
            "data": data
        }
        
    def update_user_notifs_preferences_success(self, data: dict):
        return {
            "status": "SUCCESS",
            "message": "User Notification Preference updated successfully",
            "data": data
        }

    def update_user_notifs_preferences_error(self, data: dict):
        return {
            "status": "FAILED",
            "message": "Unable to update User Notification Preference. Please check fields and try again",
            "data": data
        }

    def get_user_success(self, data: dict):
        return {
            "status": "SUCCESS",
            "data": data
        }

    def forgot_password_error(self, data):

        d = data.keys()
        print(data.keys())
        s = [a for a in data.keys()]
        print(s)
        return {
            "status": "FAILED",
            "message": data[s[0]][0],
            "data": data
        }
        


u_responses = UserResponses()
