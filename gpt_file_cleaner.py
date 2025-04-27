import random
from openai import OpenAI
from env_manager import env
import time
import logging

"""This code is deprecated and will be removed in the future."""

logging.basicConfig(level=logging.INFO)


# Initialize OpenAI client
client = OpenAI(
        api_key=env('API_GPT'),
    )

# Generate a random confirmation code
def generate_confirmation_code():
    return random.randint(100000, 999999)
    
# Step 2: Delete all vector stores
def delete_all_vector_stores():
    try:
        # List all vector stores and collect their IDs
        vector_stores = client.beta.vector_stores.list()
        vector_store_ids = [vector_store.id for vector_store in vector_stores]
        
        # Loop through and delete each vector store
        for vector_store_id in vector_store_ids:
            logging.info(f"Deleting vector store: {vector_store_id}")
            try:
                client.beta.vector_stores.delete(vector_store_id=vector_store_id)
                logging.info(f"Vector store {vector_store_id} deleted successfully!")
            except openai.error.InvalidRequestError:
                logging.exception(f"Error deleting {vector_store_id}")
            except Exception:
                logging.exception(f"Unexpected error deleting {vector_store_id}")

            time.sleep(1)  # Avoid hitting rate limits or overwhelming the API
    except Exception:
        logging.exception(f"Error while listing vector stores")


# Main deletion process with warning and confirmation
def confirm_and_delete():
    print("WARNING: This action will delete all vector stores from your OpenAI cloud storage.")
    print("This action is irreversible.")

    # Generate confirmation code
    confirmation_code = generate_confirmation_code()
    print(f"To proceed, please enter the following confirmation code: {confirmation_code}")

    # Prompt user to input the confirmation code
    user_input = input("Enter the confirmation code: ")

    # Check if the input matches the generated code
    if user_input == str(confirmation_code):
        print("Confirmation successful. Proceeding with deletion.")
        delete_all_vector_stores()
        print("All vector stores have been deleted.")
    else:
        print("Incorrect confirmation code. Aborting deletion.")

# Execute confirmation and deletion process
if __name__ == "__main__":
    confirm_and_delete()
