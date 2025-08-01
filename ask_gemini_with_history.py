import google.generativeai as genai
import os # Used for potentially loading API key from environment variables

# --- IMPORTANT: Configure your API Key ---
# It's highly recommended to load your API key from an environment variable
# for security reasons, rather than hardcoding it directly in the script.
# Example: export GOOGLE_API_KEY="YOUR_API_KEY" in your terminal
# Then, in your Python script:
# API_KEY = os.environ.get("GOOGLE_API_KEY")

# For demonstration, you can replace "YOUR_API_KEY" with your actual key.
# However, be cautious about sharing scripts with hardcoded keys.
API_KEY = "Your_API_Key" # Replace with your actual API key

# Configure the genai library with your API key
genai.configure(api_key=API_KEY)

# Initialize the Generative Model
# Using 'gemini-2.0-flash' as requested, or 'gemini-pro' for general text tasks
model = genai.GenerativeModel('gemini-2.0-flash')

# Start a new chat session. This object will manage the conversation history.
# Initialize with an empty history for a fresh start.
chat = model.start_chat(history=[])

# Function to send a message to Gemini and get a response
def ask_gemini_with_history(question: str) -> str:
    """
    Sends a question to the Gemini model within the ongoing chat session
    and returns its response.

    Args:
        question (str): The user's question.

    Returns:
        str: The Gemini model's text response.
    """
    try:
        # Use the chat.send_message method to maintain conversation context
        response = chat.send_message(question)
        return response.text
    except Exception as e:
        return f"Error communicating with Gemini: {e}"

# Example usage for a continuous chat
# print("Welcome to the Gemini AI chat!")
# print("Type 'exit' or 'quit' to end the chat.")

# while True:
#    user_input = input("You: ")
#    if user_input.lower() in ["exit", "quit"]:
#        print("Exiting chat.")
#        break

    # Get response from Gemini using the function that maintains history
#    response_text = ask_gemini_with_history(user_input)
#    print("Gemini:", response_text)

# You can also inspect the full conversation history at any point:
# print("\n--- Full Conversation History ---")
# for message in chat.history:
#     print(f"Role: {message.role}, Content: {message.parts[0].text}")
