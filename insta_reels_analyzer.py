import json
import openai
import logging
from dotenv import load_dotenv
import os

load_dotenv()

# Loads the config
with open('config.json') as config_file:
    data = json.load(config_file)


from instagrapi import Client





# Initialize OpenAI and WhisperASR
openai.api_key = os.getenv("OpenAIAPI_Key")


def login_user(username, password, session_id=""):
    """
    Attempts to log in to Instagram using either the previous session information, session id or the provided username and password.
    :param str username: The username of the account to log in to
    :param str password: The sess of the account to log in to
    :param session_id: string
    """
    try:
        session_data = cl.load_settings("session.json")
    except:
        session_data = {}

    login_via_session_data = False
    login_via_session_id = False
    login_via_password = False

    if session_data:
        try:
            cl.set_settings(session_data)
            cl.login(username, password)
            try:
                cl.get_timeline_feed()
                print("Bot is now active 😈\n")
            except LoginRequired:
                logging.info("Session is invalid, need to log in via username and password")
                old_session_data = cl.get_settings()
                cl.set_settings({})
                cl.set_uuids(old_session_data["uuids"])
                if cl.login(username, password):
                    print("Bot is now active 😈\n")
            else:
                login_via_session_data = True

        except Exception as e:
            logging.info(f"Couldn't log in user using session information: {e}")

    if not login_via_session_data and session_id != "":
        try:
            logging.info(f"Attempting to log in via session id. Session id: {session_id}")
            if cl.login_by_sessionid(session_id):
                login_via_session_id = True
                cl.dump_settings("session.json")
                print("Bot is now active 😈\n")
        except Exception as e:
            logging.info(f"Couldn't log in user using session id: {e}")

    if not login_via_session_data and not login_via_session_id:
        try:
            logging.info(f"Attempting to log in via username and password. Username: {username}")
            if cl.login(username, password):
                login_via_password = True
                cl.dump_settings("session.json")
                print("Bot is now active 😈\n")
        except Exception as e:
            logging.info(f"Couldn't log in user using username and password: {e}")

    if not login_via_password and not login_via_session_data and not login_via_session_id:
        print("Couldn't log in user with either password, session data or session id")
        raise Exception("Couldn't log in user with either password, session data or session id")


# Function to download the Instagram reel
# def download_reel(url):

#     media_pk = cl.media_pk_from_url(url)

#     video_url = cl.media_info(media_pk).video_url
#     media_path = cl.video_download_by_url(video_url, folder='/tmp')
#     print(media_path)
#     return media_path



# Function to transcribe the video
def transcribe_video(audio_file_path):
    audio_file = open(audio_file_path, "rb")
    transcript = openai.Audio.transcribe("whisper-1", audio_file)
    return transcript['text']

# Function to summarize the transcript
def summarize_transcript(transcript):
    prompt = f"The following is a transcript of an instagram reel:\n\n{transcript}"
    completion = openai.ChatCompletion.create(
            model=os.getenv("OpenAIModel"),
            temperature=.76,
            messages=[
                {"role": "system",
                 "content": prompt},
                {"role": "user", "content": "Please provide a detailed summary of at most 100 words. this will be used for training a bot on the reel."}
            ]
        )
    summary = completion.choices[0]["message"]["content"]
    return summary

# Main function
def analyze_reel(video_path):
    transcript = transcribe_video(video_path)
    summary = summarize_transcript(transcript)
    return summary

if __name__ == "__main__":
    # Configurates the logger
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='log.log', encoding='utf-8',
                        level=logging.INFO)

    cl = Client()

    analyze_reel("")
