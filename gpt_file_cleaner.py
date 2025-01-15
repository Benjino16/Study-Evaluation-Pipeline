import random
import openai
from env_manager import env
import time

# Initialize OpenAI client
client = openai(
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
            print(f"Deleting vector store: {vector_store_id}")
            try:
                client.beta.vector_stores.delete(vector_store_id=vector_store_id)
                print(f"Vector store {vector_store_id} deleted successfully!")
            except openai.error.InvalidRequestError as e:
                print(f"Error deleting {vector_store_id}: {str(e)}")
            except Exception as e:
                print(f"Unexpected error deleting {vector_store_id}: {str(e)}")

            time.sleep(1)  # Avoid hitting rate limits or overwhelming the API
    except Exception as e:
        print(f"Error while listing vector stores: {str(e)}")


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
