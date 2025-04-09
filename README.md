
# FourSonsDiagnoser

FourSonsDiagnoser is a humooristic, Python-based chatbot designed to emulate the Four Sons from the Passover Haggadah: the Wise, the Wicked, the Simple, and the One Who Does Not Know How to Ask. After chatting with the Diagnoser bot for a pre-defined number of QnA rounds, the Diagnoser provides the user with a likelhood estimation of what Haggadah son he most likely is.


## Installation

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yonadavGit/FourSonsDiagnoser.git
   ```

2. **Navigate to the Project Directory**:

   ```bash
   cd FourSonsDiagnoser
   ```

3. **Install Required Dependencies**:

   ```bash
   pip install -r requirements.txt
   ```

## Using Ollama for Local AI Model Deployment

FourSonsDiagnoser integrates with [Ollama](https://ollama.com/), an open-source platform for running large language models (LLMs) locally. To set up Ollama:

1. **Install Ollama**:

   - **For macOS**:
     - Download the official installer from [Ollama's website](https://ollama.com/).
     - Open the downloaded file and follow the installation prompts.
     - Once installed, Ollama will run as a background service.

   - **For Linux**:
     - Download the latest version suitable for your operating system from [Ollama's website](https://ollama.com/).
     - Install necessary dependencies as outlined in the [Ollama documentation](https://ollama.readthedocs.io/en/quickstart/).
     - Follow the installation prompts to complete the setup.

2. **Start the Ollama Server**:

   Open your terminal and run:

   ```bash
   ollama serve
   ```

   This command starts the Ollama server, allowing you to run models locally.

3. **Download and Run Models**:

   To download specific models, use the `ollama pull` command:

   - **Download Mistral Model**:

     ```bash
     ollama pull mistral
     ```

     This command downloads the Mistral model to your local machine.

   - **Download Llama 3.1 Model**:

     ```bash
     ollama pull llama3.1
     ```

     This fetches the Llama 3.1 model for local use.


## Usage

To start the chatbot interface, run the `main.py` script:

```bash
python main.py
```

Follow the on-screen prompts to interact with the different chatbot personalities.

## Project Structure

- `main.py`: Entry point for the chatbot interface.
- `agents.py`: Contains the definitions and behaviors of the Four Sons personas.
- `speakers.py`: Manages dialogue generation and response formatting.
- `trackers.py`: Handles session tracking and message history management.
- `requirements.txt`: Lists the Python dependencies required for the project.

