from langchain_ollama.llms import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from langchain_community.chat_message_histories import ChatMessageHistory
from langchain_core.chat_history import BaseChatMessageHistory
from langchain_core.runnables.history import RunnableWithMessageHistory
from agents import ChatEvaluationAgent
from langchain_core.messages import AIMessage, HumanMessage
from speakers import VoiceOverSpeaker
import random
from tabulate import tabulate
from trackers import DiagnosisTracker
import textwrap
from tqdm import tqdm
import time

sons_descriptions = {
    "wise_son": "The Wise Son responds with respect and clarity, showing consideration for both the question and the person asking it. His answers are thoughtful, direct, and insightful, reflecting a sharp mind and a sincere engagement with the topic at hand.",

    "wicked_son": "The Wicked Son scoffs at the question or twists it with sarcasm. He often responds with cynicism or disdain, revealing strong negative feelings toward tradition and a deliberate effort to distance himself from it.",

    "simple_son": "The Simple Son offers a basic and often off-the-mark response. Lacking intellectual depth, his answers tend to miss the point or show a limited understanding, though there may still be a spark of honest intent behind them.",

    "son_who_does_not_know_to_ask": "This son appears bewildered and unable to articulate a question at all. He struggles to form coherent thoughts, not from malice but from confusion or cognitive limitation, leaving him silent in the face of unfamiliarity."
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
farewell_messages = [
    "It was a blast chatting with you! Don’t let the maror get you down.",
    "Thanks for joining the Seder of the mind — see you next Passover!",
    "May your matzah always be crispy and your charoset sweet. Shalom!",
    "This concludes your diagnosis — you’re probably a delightful mix of sons. Farewell!"
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
Your job is to engage the user in a rich, thoughtful and short conversation that encourages them to reveal as much of their personality as possible. Through open-ended questions and meaningful dialogue, you should aim to uncover the user's beliefs, interests, and behaviors, so that it will be easier to determine their personality type. Approach the conversation with empathy and curiosity, guiding the user to share deeper insights into who they are.
Never ask the user directly about their personality or interest. Focus on the subject, and even if they are reluctant to talk about it, ask about the subject from a different angle. Keep your questions very short and very funny.

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

def get_num_of_rounds_from_user():
    while True:
        try:
            rounds_input = input("How many QnA rounds would you like to have? (or type 'exit' to quit): ")
            if rounds_input.lower() in ["exit", "quit"]:
                print("Exiting.")
                return None
            rounds = int(rounds_input)
            if rounds <= 0:
                print("Please enter a positive number.")
                continue
            break
        except ValueError:
            print("Please enter a valid number.")
    return rounds

def chat_with_bot(session_id: str, evaluation_agent: ChatEvaluationAgent, rounds: int =None, speaker: VoiceOverSpeaker = None):
    if rounds is None:
        rounds = get_num_of_rounds_from_user()
    diagnosis_tracker = DiagnosisTracker(sons_descriptions)
    # Send the first message to kick off the conversation
    random_subject = random.choice(subjects)
    initial_message_content = f"To start, let's talk about {random_subject}. What do you think about this topic?"

    # Create an AIMessage object
    initial_message = AIMessage(content=initial_message_content)
    if speaker:
        # Use the speaker to vocalize the assistant's response
        speaker.speak(initial_message_content)

    # Display the assistant's first message
    print(f"Diagnoser: {initial_message_content}")

    # Store the first message in session history
    get_session_history(session_id).add_message(initial_message)

    for i in range(rounds):
        # Wait for the user's input
        user_input = input("You: ")
        if user_input.lower() in ["exit", "quit"]:
            print("Exiting chat.")
            break

        # Store the user's message in session history
        user_message = HumanMessage(content=user_input)
        get_session_history(session_id).add_message(user_message)

        # Evaluate the user's responses immediately after the input
        table_data = []
        round_data = {}
        scoring_response_progress_bar = tqdm(sons_descriptions.items(), total=len(sons_descriptions),
                                             desc="Scoring Last Response")
        for son, description in scoring_response_progress_bar:
            likelihood, explanation = evaluation_agent.evaluate_entity_likelihood(
                son, get_session_history(session_id).messages
            )
            round_data[son] = {"likelihood": likelihood, "explanation": explanation}
            wrapped_explanation = "\n".join(textwrap.wrap(explanation, width=25))
            table_data.append([son, likelihood, wrapped_explanation])
        # scoring_response_progress_bar.close()
        diagnosis_tracker.add_round_data(round_data)
        headers = ["Son", "Score", "Explanation"]
        print("\n📊Last Response Score:")
        print(tabulate(table_data, headers=headers, tablefmt="grid"))

        # Invoke the chain with the user's input (assistant responds)
        if i < rounds - 1:
            assistant_response = chain_with_history.invoke(
                {"user_message": user_input},
                config={"configurable": {"session_id": session_id}},
            )

        else:
            farewell_message = random.choice(farewell_messages)
            assistant_response = f"{farewell_message}"

        if speaker:
            speaker.speak(assistant_response)

        # Display the assistant's response
        print(f"Diagnoser: {assistant_response}")

        # Store the assistant's response in session history
        assistant_message = AIMessage(content=assistant_response)
        get_session_history(session_id).add_message(assistant_message)

    diagnosis_tracker.print_summary()
    time.sleep(5)


if __name__ == "__main__":
    # n_rounds = 2  # Number of interaction rounds
    evaluation_agent = ChatEvaluationAgent(entities=sons_descriptions, model_name='llama3.1')
    speaker = VoiceOverSpeaker()
    chat_with_bot(MAIN_SESSION_ID, evaluation_agent, speaker=speaker)
