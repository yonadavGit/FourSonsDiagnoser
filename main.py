from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory

# Initialize the Ollama LLM with the desired model
llm = OllamaLLM(model="mistral")

# Define a function to retrieve or create chat history
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]

# Define a prompt template that includes the chat history
template = """You are a helpful assistant.

{chat_history}
User: {user_message}
Assistant:"""

prompt = ChatPromptTemplate.from_template(template)

# Create a chain that combines the prompt and the model
chain = prompt | llm

# Wrap the chain with message history functionality
chain_with_history = RunnableWithMessageHistory(
    chain,
    get_session_history,
    input_messages_key="user_message",
    history_messages_key="chat_history",
)

# Function to interact with the chatbot for a specified number of rounds
def chat_with_bot(session_id: str, rounds: int):
    for _ in range(rounds):
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat.")
            break

        # Invoke the chain with the user input
        response = chain_with_history.invoke(
            {"user_message": user_input},
            config={"configurable": {"session_id": session_id}},
        )

        print(f"Assistant: {response}")

if __name__ == "__main__":
    session_id = "user_123"  # Unique identifier for the chat session
    n_rounds = 5  # Number of interaction rounds
    chat_with_bot(session_id, n_rounds)
