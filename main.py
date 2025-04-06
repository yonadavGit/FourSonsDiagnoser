from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from agents import ChatEvaluationAgent
from langchain_core.messages import AIMessage, HumanMessage
from speakers import VoiceOverSpeaker
import random

sons_descriptions = {
    "wise_son": "The Wise Son is deeply engaged with the intellectual aspects of tradition. He approaches the Seder with a thirst for knowledge, seeking to understand the underlying principles and philosophies of the rituals. His questions are thoughtful and reflect a genuine desire to connect with the deeper meanings of the commandments.",
    "wicked_son": "The Wicked Son exhibits a rebellious stance toward tradition, often questioning its relevance or dismissing its importance. His inquiry, 'What does this service mean to you?' suggests a sense of detachment or exclusion from the communal practices.",
    "simple_son": "The Simple Son approaches the Seder with innocence and straightforwardness. His question, 'What's this?' reflects a sincere curiosity and a desire to understand, albeit without the depth of inquiry seen in the Wise Son. He may appear less sophisticated in his approach but is earnest in his wish to learn.",
    "son_who_does_not_know_to_ask": "This son is unaware of his own ignorance, lacking the initiative to seek knowledge. His inability to ask questions may stem from unfamiliarity with the traditions, a sense of indifference, or a lack of exposure to the cultural and religious narratives of the community."
}
subjects = [
    "Why matzah is basically just a cracker on a diet",
    "The secret life of Elijah the Prophet and his mysterious appearance at the Seder",
    "How to survive eating too much gefilte fish at the Seder",
    "The possible conspiracy behind the disappearance of the afikoman",
    "What would happen if the Seder plate items had a reality TV show",
    "Why we only eat unleavened bread for a week — are we just trying to make bread jealous?",
    "The bizarre journey of the half-eaten charoset from the Seder plate to your stomach",
    "If Moses had a GPS, would he have crossed the Red Sea so dramatically?",
    "Why the maror always feels spicier than last year, even though it’s the same",
    "How to explain to your non-Jewish friends why you’re eating bitter herbs and drinking wine at 10 AM"
]

# Initialize the Ollama LLM with the desired model
llm = OllamaLLM(model="mistral")
MAIN_SESSION_ID = "main_session"
# Define a function to retrieve or create chat history
store = {}

def get_session_history(session_id: str) -> BaseChatMessageHistory:
    if session_id not in store:
        store[session_id] = ChatMessageHistory()
    return store[session_id]




template = f"""You are a helpful assistant.
Your job is to engage the user in a rich, thoughtful conversation that encourages them to reveal as much of their personality as possible. Through open-ended questions and meaningful dialogue, you should aim to uncover the user's beliefs, interests, and behaviors, so that it will be easier to determine their personality type. Approach the conversation with empathy and curiosity, guiding the user to share deeper insights into who they are.
Never ask the user directly about their personality or interest. Foucus on the subject, and even if they are reluctant to talk about it, ask about the subject from a different angle.

{{chat_history}}
User: {{user_message}}
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
def chat_with_bot(session_id: str, rounds: int, evaluation_agent: ChatEvaluationAgent, speaker: VoiceOverSpeaker = None):
    # Send the first message to kick off the conversation
    random_subject = random.choice(subjects)
    initial_message_content = f"To start, let's talk about {random_subject}. What do you think about this topic?"

    # Create an AIMessage object
    initial_message = AIMessage(content=initial_message_content)
    if speaker:
        # Use the speaker to vocalize the assistant's response
        speaker.speak(initial_message_content)

    # Display the assistant's first message
    print(f"Assistant: {initial_message_content}")

    # Store the first message in session history
    get_session_history(session_id).add_message(initial_message)

    for _ in range(rounds):
        # Wait for the user's input
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat.")
            break

        # Store the user's message in session history
        user_message = HumanMessage(content=user_input)
        get_session_history(session_id).add_message(user_message)

        # Evaluate the user's responses immediately after the input
        for son, description in sons_descriptions.items():
            likelihood, explanation = evaluation_agent.evaluate_entity_likelihood(
                son, get_session_history(session_id).messages
            )
            print(f"Likelihood of being {son}: {likelihood} - {explanation}")

        # Invoke the chain with the user's input (assistant responds)
        assistant_response = chain_with_history.invoke(
            {"user_message": user_input},
            config={"configurable": {"session_id": session_id}},
        )

        if speaker:
            # Use the speaker to vocalize the assistant's response
            speaker.speak(assistant_response)

        # Display the assistant's response
        print(f"Assistant: {assistant_response}")

        # Store the assistant's response in session history
        assistant_message = AIMessage(content=assistant_response)
        get_session_history(session_id).add_message(assistant_message)


        # print("History:" + str(get_session_history(session_id).messages))

if __name__ == "__main__":
    n_rounds = 5  # Number of interaction rounds
    evaluation_agent = ChatEvaluationAgent(entities=sons_descriptions)
    speaker = VoiceOverSpeaker()
    chat_with_bot(MAIN_SESSION_ID, n_rounds, evaluation_agent, speaker=speaker)
