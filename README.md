# DILAB IVY Project

Interactive Video (IVY) is an interactive chatbot Agent built with Gradio that communicates with the MCM API to answer user questions.

## Setup

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/ivy-chatbot.git
    cd ivy-chatbot
    ```

2. **Create and activate a virtual environment (optional but recommended):**

    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. **Install the required dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4. **Run the application:**

    ```bash
    python main.py
    ```

## Project Structure

- **main.py:** The main application file that sets up the Gradio interface and handles user interactions.
- **requirements.txt:** A list of Python dependencies required for the project.
- ** test_scripts** A directory containing testing scripts for local development and sanity checks upon deployment.

## Notes

- Ensure your environment variables are set correctly.
- Modify the MCM API URL and API key as needed.
