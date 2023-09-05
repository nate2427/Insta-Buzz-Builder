# Instagram Engagement Bot

This repository contains the code for the Instagram Engagement Bot, a tool that helps boost your engagement on Instagram with the help of an AI copilot. The bot and dashboard included in this project provide automation features to enhance your Instagram presence.

The main files involved in running the bot and dashboard are:

`app.py`:
Main script for running the dashboard using Streamlit.
Responsible for handling user interactions and displaying the dashboard interface.

`.env`:
Configuration file that contains the necessary environment variables for the bot and dashboard.
Users should update the values inside this file with their own credentials.

`insta_bot.py`:
Contains the code for the Instagram bot.
Includes functions for automating various engagement actions on Instagram, such as liking posts, following users, and generating personalized comments.

`insta_reels.py`:
Contains additional functionality specific to Instagram reels.
Provides functions for interacting with Instagram reels, such as analyzing video content and generating summaries.

`gpt_prompts.py`:
Contains functions for generating prompts to be used with the OpenAI GPT model.
Helps in generating personalized comments and responses using the GPT model.

`db.py`:
Handles database operations for storing and retrieving persona configurations.
Includes functions for adding new persona configurations and retrieving existing configurations.
These summaries provide a brief overview of each file and its purpose in the project.

Please refer to the individual files for more detailed information about their functionality and usage.

## Installation

1. Clone the repository:
   `$ git clone  git@github.com:nate2427/Insta-Buzz-Builder.git`

2. Install the required dependencies:
   `$ pip install -r requirements.txt`

3. Rename the file `_.env` to `.env` and update the values inside the `.env` file with your own credentials.

4. Run the bot and dashboard:
   `$ streamlit run app.py`

# Usage

Once the bot and dashboard are running, you can use the dashboard to interact with the bot and perform various Instagram automation tasks to boost your engagement. The AI copilot feature helps generate personalized comments to engage with your audience effectively.

# Contributing

Contributions are welcome! If you have any suggestions or improvements, please create a pull request or open an issue.

# License

This project is licensed under the MIT License.
