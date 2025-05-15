def item_not_found_exception(type, item_id):
    if item_id:
        return f"{type} with ID {item_id} not found"
    return f"{type} not found"


internal_server_exception = "Unexpected error occurred"

item_invalid_data_exception = (
    "A database integrity error occurred. Please check your input and constraints."
)
