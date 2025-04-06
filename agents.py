from typing import Dict, List, Optional
from langchain_ollama.llms import OllamaLLM
from langchain.schema import HumanMessage, AIMessage, SystemMessage, BaseMessage

class ChatEvaluationAgent:
    def __init__(self, entities: Dict[str, str], model_name: str = "mistral"):
        """
        Initialize the ChatEvaluationAgent with entities and a chat model.

        Args:
            entities (Dict[str, str]): A dictionary mapping entity names to their descriptions.
            model_name (str): The name of the chat model to use. Defaults to "llama-2-13b".
        """
        self.entities = entities
        self.chat_model = OllamaLLM(model="mistral")  # Use ChatOllama instead of ChatOpenAI

    def format_chat_history(self, chat_history: List[BaseMessage]) -> str:
        """
        Format the chat history into a structured string.

        Args:
            chat_history (List[BaseMessage]): The chat history containing messages.

        Returns:
            str: A formatted string representing the chat history.
        """
        formatted_history = []
        for message in chat_history:
            if isinstance(message, HumanMessage):
                role = "User"
            elif isinstance(message, AIMessage):
                role = "Assistant"
            elif isinstance(message, SystemMessage):
                role = "System"
            else:
                role = "Unknown"
            formatted_history.append(f"{role}: {message.content}")
        return "\n".join(formatted_history)

    def get_last_user_message(self, chat_history: List[BaseMessage]) -> Optional[str]:
        """
        Retrieve the last user message from the chat history.

        Args:
            chat_history (List[BaseMessage]): The chat history containing messages.

        Returns:
            Optional[str]: The content of the last user message, or None if not found.
        """
        for message in reversed(chat_history):
            if isinstance(message, HumanMessage):
                return message.content
        return None

    def evaluate_entity_likelihood(self, entity_name: str, chat_history: List[BaseMessage]) -> tuple:
        """
        Evaluate how likely it is that the user is the specified entity based on their last response.

        Args:
            entity_name (str): The name of the entity to evaluate.
            chat_history (List[BaseMessage]): The chat history containing messages.

        Returns:
            tuple: A tuple containing the likelihood score (int) and explanation (str).
        """
        if entity_name not in self.entities:
            raise ValueError(f"Entity '{entity_name}' not found in the provided entities.")

        entity_description = self.entities[entity_name]
        formatted_history = self.format_chat_history(chat_history)
        last_user_message = self.get_last_user_message(chat_history)

        if not last_user_message:
            raise ValueError("No user messages found in the chat history.")

        prompt = (
            f"Here is the conversation history:\n{formatted_history}\n\n"
            f"Focusing on the user's last response: '{last_user_message}', "
            f"and considering the description of {entity_name}: '{entity_description}', "
            f"how likely is it that the user is {entity_name}?\n"
            f"Please respond with a  whole number (int) between 0 and 5, followed by a colon ':' and a short explanation."
            f"\nExample format: '3: The user shows a strong indication of being {entity_name}.'"
        )

        # Pass the prompt as a string to the invoke method
        response = self.chat_model.invoke(prompt)

        # Assuming the response format is something like "3: Some explanation"
        likelihood, explanation = response.split(':', 1)
        return int(likelihood.strip()), explanation.strip()
def test_chat_evaluation_agent():
    # Define some mock entities and descriptions
    entities = {
        "Scientist": "An individual with a strong background in science, especially physics and chemistry.",
        "Engineer": "A professional who applies scientific knowledge to design and build systems or structures."
    }

    # Initialize the ChatEvaluationAgent with mock entities
    agent = ChatEvaluationAgent(entities)

    # Create a mock chat history
    chat_history = [
        SystemMessage(content="This is the start of the conversation."),
        HumanMessage(content="Hi, I am a scientist working on a new project."),
        AIMessage(content="That sounds fascinating! Can you tell me more about the project?"),
        HumanMessage(content="Sure, we are exploring new methods of energy storage in batteries."),
    ]

    # Test the format_chat_history method
    formatted_history = agent.format_chat_history(chat_history)
    print("Formatted Chat History:")
    print(formatted_history)

    # Test get_last_user_message method
    last_user_message = agent.get_last_user_message(chat_history)
    print("\nLast User Message:")
    print(last_user_message)

    # Test the evaluate_entity_likelihood method for the 'Scientist' entity
    likelihood = agent.evaluate_entity_likelihood("Scientist", chat_history)
    print("\nLikelihood of being a 'Scientist':")
    print(likelihood)

    # Test the evaluate_entity_likelihood method for the 'Engineer' entity
    likelihood = agent.evaluate_entity_likelihood("Engineer", chat_history)
    print("\nLikelihood of being an 'Engineer':")
    print(likelihood)

if __name__ == "__main__":
    test_chat_evaluation_agent()
