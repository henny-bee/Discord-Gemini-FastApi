
![FastAPI Logo](https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png)

# Discord Gemini Chatbot

A powerful Discord bot integrated with Google's Gemini AI, featuring persistent message history storage using MongoDB and a FastAPI backend.

## Project Overview

This project is a sophisticated Discord chatbot that leverages Google's Generative AI (Gemini) to provide intelligent conversational responses. Unlike simple bots, it maintains context by storing chat history in a MongoDB database, allowing for coherent multi-turn conversations. The application is built with a modern asynchronous architecture using Python, FastAPI, and Motor.

## Architecture

The project follows a modular structure to ensure scalability and maintainability:

*   **`app/core`**: Handles core application configuration (environment variables) and database connections (MongoDB).
*   **`app/models`**: Defines Pydantic models and database schemas for data validation and structure.
*   **`app/services`**: Contains the business logic, effectively separating concerns.
    *   `gemini_service.py`: Manages interactions with the Google Gemini API.
    *   `storage_service.py`: Handles asynchronous database operations with MongoDB.
*   **`app/bot`**: Manages the Discord bot lifecycle.
    *   `client.py`: The main bot client setup.
    *   `events.py`: Handles Discord events like `on_message`.
    *   `commands.py`: Defines slash commands (e.g., `/forget`).
*   **`app/api`**: Exposes FastAPI routes for external interaction or monitoring.

### Data Flow

1.  **Discord Event**: User sends a message or issues a command in Discord.
2.  **Bot Client**: The `discord.py` client receives the event.
3.  **Event Handling**: `app/bot` processes the event.
4.  **Service Layer**: The bot delegates complex logic to `app/services`.
    *   Retrieves context/history from **MongoDB**.
    *   Sends prompt + context to **Gemini AI**.
5.  **Response**: The service returns the generated response, which the bot sends back to Discord.

## Tech Stack

*   **Language**: Python 3.10+
*   **Web Framework**: FastAPI
*   **Database**: MongoDB
*   **Database Driver**: Motor (Async Python driver for MongoDB)
*   **Bot Framework**: Discord.py
*   **LLM**: Google Generative AI (Gemini)
*   **Data Validation**: Pydantic

## Prerequisites

Before running the application, ensure you have the following installed:

*   [Python 3.10+](https://www.python.org/downloads/)
*   [MongoDB](https://www.mongodb.com/try/download/community) (Local instance or Atlas URI)

## Installation & Setup

1.  **Clone the repository:**

    ```bash
    git clone https://github.com/henny-bee/Discord-Gemini-FastApi.git
    cd discord-gemini-chatbot
    ```

2.  **Create a virtual environment:**

    ```bash
    python -m venv venv
    
    # Windows
    venv\Scripts\activate
    
    # Linux/macOS
    source venv/bin/activate
    ```

3.  **Install dependencies:**

    ```bash
    pip install -r requirements.txt
    ```

4.  **Configuration:**

    Copy the example environment file and rename it to `.env`:

    ```bash
    cp .env.example .env
    # On Windows command prompt: copy .env.example .env
    ```

    Open `.env` and fill in your credentials:

    ```env
    DISCORD_BOT_TOKEN=your_discord_bot_token
    GEMINI_API_KEY=your_google_gemini_api_key
    MONGODB_URI=mongodb:
    ```

## Running the Application

Start the application using `uvicorn`. This command launches both the FastAPI server and the Discord bot (as a background task).

```bash
uvicorn app.main:app --reload
```

## Usage

Once the bot is running and invited to your server, you can use the following Slash Commands:

*   `/forget [persona]`
    *   **Description**: Clears the conversation history for the current channel.
    *   **Optional Argument**: `persona` - Sets a specific persona/instruction for the bot to adopt after clearing memory (e.g., "You are a helpful coding assistant").

*   `/createthread [name]`
    *   **Description**: Creates a new private thread in the current channel where the bot will automatically reply to every message.
    *   **Argument**: `name` - The name of the thread to create.
