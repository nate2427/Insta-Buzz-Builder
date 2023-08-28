import json
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from insta_reels_analyzer import analyze_reel
import promptlayer

 # Loads the config
with open('config.json') as config_file:
    data = json.load(config_file)

promptlayer.api_key = data["PROMPTLAYER_API_KEY"]
openai = promptlayer.openai

class InstaBot:
    def __init__(self):

        self.client = Client()

        # Loads the config
        with open('config.json') as config_file:
            data = json.load(config_file)

        self.username = data['Username']
        self.password = data['Password']

        # Sets the proxy
        proxy = f"http://{data['THUNDER_PROXIES_USER']}:{data['THUNDER_PROXIES_PASS']}@{data['THUNDER_PROXIES_URL']}:{data['THUNDER_PROXIES_PORT']}"
        self.client.set_proxy(proxy)

        # Sets a delay range to mimic user behaviour as recommended by Instagrapi best practices
        self.client.delay_range = [data["RandomDelayMinBetweenInteraction"], data["RandomDelayMaxBetweenInteraction"]]

        # login user
        self.login_user(self.username, self.password)

        data["SessionID"] = self.client.get_settings()["authorization_data"]["sessionid"]
        with open("config.json", "w") as config_file:
            json.dump(data, config_file, indent=4)
        openai.api_key = data['OpenAIAPI_Key']
        print("Logged in.\n\n Running Bot...\n\n")

    def login_user(self, username, password, session_id=""):
        """
        Attempts to log in to Instagram using either the previous session information, session id or the provided username and password.
        :param str username: The username of the account to log in to
        :param str password: The sess of the account to log in to
        :param session_id: string
        """
        try:
            session_data = self.client.load_settings("session.json")
        except:
            session_data = {}

        login_via_session_data = False
        login_via_session_id = False
        login_via_password = False

        if session_data:
            try:
                self.client.set_settings(session_data)
                self.client.login(username, password)
                try:
                    self.client.get_timeline_feed()
                    print("Bot is now active 😈\n")
                except LoginRequired:
                    print("Session is invalid, need to log in via username and password")
                    old_session_data = self.client.get_settings()
                    self.client.set_settings({})
                    self.client.set_uuids(old_session_data["uuids"])
                    if self.client.login(username, password):
                        print("Bot is now active 😈\n")
                else:
                    login_via_session_data = True

            except Exception as e:
                print(f"Couldn't log in user using session information: {e}")

        if not login_via_session_data and session_id != "":
            try:
                print(f"Attempting to log in via session id. Session id: {session_id}")
                if self.client.login_by_sessionid(session_id):
                    login_via_session_id = True
                    self.client.dump_settings("session.json")
                    print("Bot is now active 😈\n")
            except Exception as e:
                print(f"Couldn't log in user using session id: {e}")

        if not login_via_session_data and not login_via_session_id:
            try:
                print(f"Attempting to log in via username and password. Username: {username}")
                if self.client.login(username, password):
                    login_via_password = True
                    self.client.dump_settings("session.json")
                    print("Bot is now active 😈\n")
            except Exception as e:
                print(f"Couldn't log in user using username and password: {e}")

        if not login_via_password and not login_via_session_data and not login_via_session_id:
            print("Couldn't log in user with either password, session data or session id")
            raise Exception("Couldn't log in user with either password, session data or session id")

    def get_instagram_post(self, post_url):
        # Get the media ID from the post URL
        try:
            return self.client.media_oembed(post_url)
        except Exception as e:
            print(e)
            return None
        
    def download_reel(self, url):
        media_pk = self.client.media_pk_from_url(url)

        video_url = self.client.media_info(media_pk).video_url
        media_path = self.client.video_download_by_url(video_url, folder='/tmp')
        return media_path
    
    def summarize_reel(self, url):
        """
            Summarizes a reel by downloading it and analyzing its contents.

            Parameters:
                url (str): The URL of the reel to be summarized.

            Returns:
                The summary of the reel.
        """
        vidoe_path = self.download_reel(url)
        return analyze_reel(vidoe_path)
    def generateComment(self, caption_text, comment_count, media_id, username, targeted_acct, targeted_acct_details, persona_prompt_template):
        """
        Generates a personalised comment to the post specified using OpenAI.

        :param str openai_api_key: Your OpenAI API key
        :param str model: Which OpenAI model to use
        :param str CommentIfOpenAIFails: What to comment if OpenAI fails to generate a comment
        :param str caption_text: The caption of the post
        :param int comment_count: The amount of comments on the post
        :param str media_id: The media id of the post
        :param str username: The username of the posts creator
        :return: A comment to the post
        :rtype: str
        """

        usercontent = f"Write a short and generic Instagram comment, which does not include hashtags.\nYour post is a reel and a detailed summary is here:\n\n{targeted_acct_details}\n\n The comment should not include quotation marks and should be no longer than a 5 second read. Be very entertaining and emotionally engaging. Make them want to engage with @{targeted_acct}.\nThe post's caption:\n'{caption_text}'"

        # Checks if the post already has comments, and if it has, it uses one of the comments as an example
        if comment_count > 0:
            try:
                media_comments = self.client.media_comments(media_id, 1)
                example_comment = media_comments[0].dict()["text"]
                usercontent += f"\n\nAn example of a comment made on the post is:\n'{example_comment}'"
            except Exception as e:
                print(f"An error occurred whilst attempting to get an example comment: {e}")
        try:
            # Gets the post creators biography
            user_info = self.client.user_info(media_id.split("_")[1])
            creators_biography = user_info.dict()["biography"]
            usercontent += f"\n\nThe post creators biography is:\n'{creators_biography}'"
            print("Successfully got the post creators biography")
        except Exception as e:
            print(f"An error occurred whilst attempting to get the post creators biography: {e}")
        usercontent += f"\n\nThe post creators username is:\n'{username}'"
        persona_prompt_template = "You are a top of the line Instagram Community Builder Agency called Buzz Builders who uses the comments section on targeted posts to boost traffic to another account that creates complementary content to the post that is being commented on. You understand the account that you are working for and the name of the account is given below. There is a bit of a description of the user that you are working for below. Use that and your creative writing and community building and engaging skills to provide engaging and quality responses to the posts you are viewing. Make sure to tag the account that you are working for and to also tag the account that you are commenting on. Make sure the post isnt longer than a 10 second read. Engage the two accounts and talk about how their interests are similar and how the community and themselves will benefit from your clients content. You know this is a piece of cake. You've been doing this for over 10 years and have done it for big brands and even individuals like Drake and Taylor Swift. Understand whether the account is a business account or just a regular user. Your responses depend on this. You move with stealth and you use emotional intelligence when connecting with individuals via instagram Posts. You know not to be pushy on getting people to follow directly, but use indirect ways to get people to follow you by making them feel important, inspired, and interested.\n\nAt the end of your comment, mention that individuals intersted in building buzz for their brand to connect with @spiritual_techie who is the owner of Buzz Builders and is bringing a more humanistic aspect to AI in marketing and advertisment. Make that part is quick and short, but make sure to also make that mention. Also, Make it super engaging and ask a good question that will make the poster want to respond. The interesting question is the most important part here!\n\n You are scrolling Instagram, when you find a post..."
        try:
            # Generates the comment
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                temperature=0.45,
                max_tokens=250,
                messages=[
                    {"role": "system",
                    "content": persona_prompt_template},
                    {"role": "user", "content": usercontent}
                ]
            )
            comment_text = completion.choices[0]["message"]["content"]
            return comment_text
        except Exception as e:
            # Returns CommentIfOpenAIFails if an erorr occurres
            print(f"An error occurred whilst attempting to generate a comment: {e}")
            return "Error: Rerun the bot" 
    
    def regenerateComment(self, caption_text, comment_count, media_id, username, targeted_acct, targeted_acct_details, old_comment, persona_prompt_template):
        """
        Generates a personalised comment to the post specified using OpenAI.

        :param str openai_api_key: Your OpenAI API key
        :param str model: Which OpenAI model to use
        :param str CommentIfOpenAIFails: What to comment if OpenAI fails to generate a comment
        :param str caption_text: The caption of the post
        :param int comment_count: The amount of comments on the post
        :param str media_id: The media id of the post
        :param str username: The username of the posts creator
        :return: A comment to the post
        :rtype: str
        """

        usercontent = f"Write a short and generic Instagram comment, which does not include hashtags.\nYour post is a reel and a detailed summary is here:\n\n{targeted_acct_details}\n\n The comment should not include quotation marks and should be no longer than a 5 second read. Be very entertaining and emotionally engaging. Make them want to engage with @{targeted_acct}.\nThe post's caption:\n'{caption_text}'"

        # Checks if the post already has comments, and if it has, it uses one of the comments as an example
        if comment_count > 0:
            try:
                media_comments = self.client.media_comments(media_id, 1)
                example_comment = media_comments[0].dict()["text"]
                usercontent += f"\n\nAn example of a comment made on the post is:\n'{example_comment}'"
            except Exception as e:
                print(f"An error occurred whilst attempting to get an example comment: {e}")
        try:
            # Gets the post creators biography
            user_info = self.client.user_info(media_id.split("_")[1])
            creators_biography = user_info.dict()["biography"]
            usercontent += f"\n\nThe post creators biography is:\n'{creators_biography}'"
            print("Successfully got the post creators biography")
        except Exception as e:
            print(f"An error occurred whilst attempting to get the post creators biography: {e}")
        usercontent += f"\n\nThe post creators username is:\n'{username}'"
        persona_prompt_template = "You are a top of the line Instagram Community Builder Agency called Buzz Builders who uses the comments section on targeted posts to boost traffic to another account that creates complementary content to the post that is being commented on. You understand the account that you are working for and the name of the account is given below. There is a bit of a description of the user that you are working for below. Use that and your creative writing and community building and engaging skills to provide engaging and quality responses to the posts you are viewing. Make sure to tag the account that you are working for and to also tag the account that you are commenting on. Make sure the post isnt longer than a 10 second read. Engage the two accounts and talk about how their interests are similar and how the community and themselves will benefit from your clients content. You know this is a piece of cake. You've been doing this for over 10 years and have done it for big brands and even individuals like Drake and Taylor Swift. Understand whether the account is a business account or just a regular user. Your responses depend on this. You move with stealth and you use emotional intelligence when connecting with individuals via instagram Posts. You know not to be pushy on getting people to follow directly, but use indirect ways to get people to follow you by making them feel important, inspired, and interested.\n\nAt the end of your comment, mention that individuals intersted in building buzz for their brand to connect with @spiritual_techie who is the owner of Buzz Builders and is bringing a more humanistic aspect to AI in marketing and advertisment. Make that part is quick and short, but make sure to also make that mention.\n\n You are scrolling Instagram, when you find a post..."
        usercontent += f"You have already generated a comment:\n\n{old_comment}\n\nUnfortnately, it isnt the best comment. Try again. Make it super engaging and ask a question that will make the poster want to respond."
        try:
            # Generates the comment
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                temperature=0.45,
                max_tokens=250,
                messages=[
                    {"role": "system",
                    "content": persona_prompt_template},
                    {"role": "user", "content": usercontent}
                ]
            )
            comment_text = completion.choices[0]["message"]["content"]
            return comment_text
        except Exception as e:
            # Returns CommentIfOpenAIFails if an erorr occurres
            print(f"An error occurred whilst attempting to generate a comment: {e}")
            return "Error: Rerun the bot" 
        
    def commentOnPost(self, comment, media_id):
        """
        Attemps to comment the specified comment on the post with the given media_id.
        Logs if the attempt is successful or unsuccessful

        :param str comment: The content of the comment to be sent
        :param str media_id: The media_id of the post to comment on
        """

        try:
            # Attempts to comment on a post
            self.client.media_comment(media_id, comment)
            return True
        except Exception as e:
            return False
    
    def get_comments_from_post(self, media_id):
        """
        Gets the comments from the specified post
        """
        try:
            return self.client.media_comments(media_id)
        except Exception as e:
            return None
        
    def generate_reply_to_comment(self, caption_text, comment, commenter_username, targeted_acct, targeted_acct_details, persona_prompt_template):
        """
        Generates a personalised reply to the comment on a post specified using OpenAI.
        """
        usercontent = f"Write a short and entertaining Instagram comment that boosts the engagement of the commenter's comment.\The comment is on a post that is a reel and a detailed summary is here:\n\n{targeted_acct_details}\n\n The reply should not include quotation marks and should be no longer than a 5 second read. Be very entertaining and emotionally engaging. Make them want to engage with @{targeted_acct} (which is the account you are running).\nThe post's caption:\n'{caption_text}'\n\n The comment to be replied to:\n'{comment}' and the author of that comment is @{commenter_username}. Make sure to tag them, but in a cool and fun way, so that they get notified."

        persona_prompt_template = f"You are a top of the line Instagram user called @{targeted_acct} who uses the comments section on targeted posts to build your engagement in the community. You reply back to comments with insight, humor, wit, and always with a question that the original commenter loves to follow up to. You are scrolling Instagram, when you find a post with the above caption and comment, do your thang!"

        try:
            # Generates the comment
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                temperature=0.45,
                max_tokens=250,
                messages=[
                    {"role": "system",
                    "content": persona_prompt_template},
                    {"role": "user", "content": usercontent}
                ]
            )
            comment_text = completion.choices[0]["message"]["content"]
            return comment_text
        except Exception as e:
            # Returns CommentIfOpenAIFails if an erorr occurres
            print(f"An error occurred whilst attempting to generate a comment: {e}")
            return None
        
    def regenerate_reply_to_comment(self, caption_text, comment, commenter_username, targeted_acct, targeted_acct_details, old_comment, persona_prompt_template):
        """
        Generates a personalised reply to the comment on a post specified using OpenAI.
        """
        usercontent = f"Write a short and entertaining Instagram comment that boosts the engagement of the commenter's comment.\The comment is on a post that is a reel and a detailed summary is here:\n\n{targeted_acct_details}\n\n The reply should not include quotation marks and should be no longer than a 5 second read. Be very entertaining and emotionally engaging. Make them want to engage with @{targeted_acct} (which is the account you are running).\nThe post's caption:\n'{caption_text}'\n\n The comment to be replied to:\n'{comment}' and the author of that comment is @{commenter_username}. Make sure to tag them, but in a cool and fun way, so that they get notified."

        persona_prompt_template = f"You are a top of the line Instagram user called @{targeted_acct} who uses the comments section on targeted posts to build your engagement in the community. You reply back to comments with insight, humor, wit, and always with a question that the original commenter loves to follow up to. You are scrolling Instagram, when you find a post with the above caption and comment. You have already created a comment:\n\n{old_comment}\n\nUnfortnately, it isnt the best comment. Try again. Make it super engaging and ask a question that will make the poster want to respond."

        try:
            # Generates the comment
            completion = openai.ChatCompletion.create(
                model="gpt-3.5-turbo-16k",
                temperature=0.45,
                max_tokens=250,
                messages=[
                    {"role": "system",
                    "content": persona_prompt_template},
                    {"role": "user", "content": usercontent}
                ]
            )
            comment_text = completion.choices[0]["message"]["content"]
            return comment_text
        except Exception as e:
            # Returns CommentIfOpenAIFails if an erorr occurres
            print(f"An error occurred whilst attempting to generate a comment: {e}")
            return None
        
    def reply_to_comment(self, media_id, comment_pk, reply):
        """
        Attemps to comment the specified comment on the post with the given media_id.
        Logs if the attempt is successful or unsuccessful
        """
        try:
            # Attempts to comment on a post
            self.client.media_comment(media_id, reply, replied_to_comment_id=comment_pk)
            return True
        except Exception as e:
            return False