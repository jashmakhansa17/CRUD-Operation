def item_not_found_exception(type, item_id):
    if item_id:
        return f"{type} with ID {item_id} not found"
    return f"{type} not found"


def user_not_found_exception(type, user_id):
    if user_id:
        return f"{type} with ID {user_id} not found"
    return f"{type} not found"


internal_server_exception = "Unexpected error occurred"

item_invalid_data_exception = (
    "A database integrity error occurred. Please check your input and constraints."
)

invalid_access_token = "Invalid token type: access token required"
invalid_jwt_token = "Invalid token type: jwt token required"
invalid_refresh_token = "Invalid token type: refresh token required"
token_is_blacklisted = "Token is blacklisted"
invalid_token = "Invalid token"
user_not_found="User not found"
admin_can_access="Only Admin can access!"

password_have_atleast_8_characters="Password must be at least 8 characters long"
password_have_atleast_one_uppercase_letter="Password must include at least one uppercase letter"
password_have_atleast_one_lowercase_letter="Password must include at least one lowercase letter"
password_have_atleast_one_digit="Password must include at least one digit"
password_have_atleast_one_special_character="Password must include at least one special character"

email_already_exist="Email already exist"
invalid_email_or_user="Invalid email/user!"
invalid_password="Invalid password!"
invalid_current_password="Incorrect current password!"
invalid_confirm_password="Confirm password must be same as New password!"

password_updated_successful="Password updated successfully"
password_reset_email_sent="Password reset email sent"
logout_successful="logged out successfully"

not_authenticated="Not authenticated"