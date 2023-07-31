import json
import logging
import time
from random import randint

import openai
from instagrapi import Client
from instagrapi.exceptions import LoginRequired
from fp.fp import FreeProxy



def login_user(username, password, session_id=""):
    """
    Attempts to log in to Instagram using either the previous session information, session id or the provided username and password.
    :param str username: The username of the account to log in to
    :param str password: The sess of the account to log in to
    :param session_id: string
    """
    try:
        session_data = client.load_settings("session.json")
    except:
        session_data = {}

    login_via_session_data = False
    login_via_session_id = False
    login_via_password = False

    if session_data:
        try:
            client.set_settings(session_data)
            client.login(username, password)
            try:
                client.get_timeline_feed()
                print("Bot is now active 😈\n")
            except LoginRequired:
                logging.info("Session is invalid, need to log in via username and password")
                old_session_data = client.get_settings()
                client.set_settings({})
                client.set_uuids(old_session_data["uuids"])
                if client.login(username, password):
                    print("Bot is now active 😈\n")
            else:
                login_via_session_data = True

        except Exception as e:
            logging.info(f"Couldn't log in user using session information: {e}")

    if not login_via_session_data and session_id != "":
        try:
            logging.info(f"Attempting to log in via session id. Session id: {session_id}")
            if client.login_by_sessionid(session_id):
                login_via_session_id = True
                client.dump_settings("session.json")
                print("Bot is now active 😈\n")
        except Exception as e:
            logging.info(f"Couldn't log in user using session id: {e}")

    if not login_via_session_data and not login_via_session_id:
        try:
            logging.info(f"Attempting to log in via username and password. Username: {username}")
            if client.login(username, password):
                login_via_password = True
                client.dump_settings("session.json")
                print("Bot is now active 😈\n")
        except Exception as e:
            logging.info(f"Couldn't log in user using username and password: {e}")

    if not login_via_password and not login_via_session_data and not login_via_session_id:
        print("Couldn't log in user with either password, session data or session id")
        raise Exception("Couldn't log in user with either password, session data or session id")


def watch_users(Usernames):
    """
    Checks every users in Usernames list profile for new posts.
    If a user has not been checked before, it finds the users id and saves it.

    :param list Usernames: List of usernames to watch
    """
    # Opens list of users to watch
    with open('userswatching.json') as users_watching_file:
        userswatching = json.load(users_watching_file)
    for username in Usernames:
        logging.info(f"Checking if {username} has created a new post")
        try:
            if username.lower() in userswatching:
                # If a users profile has been checked before, it checks whether or not the user has made a new post
                NewestPost = client.user_medias(userswatching[username.lower()]["ID"], 1)[0].pk
                if NewestPost != userswatching[username.lower()]["LastPost"]:
                    # Logs and prints if the user has made a new post
                    logging.info(f"{username} has crated a new post. PK: {NewestPost}")
                    print(f"{username} has crated a new post. PK: {NewestPost}")
                # Changes lastpost to the most recent post
                userswatching[username.lower()]["LastPost"] = NewestPost
                with open('userswatching.json', "w") as users_watching_file:
                    json.dump(userswatching, users_watching_file, indent=4)
            else:
                # Saves information about the user
                userswatching[username.lower()] = {}
                userswatching[username.lower()]["ID"] = client.user_id_from_username(username)
                userswatching[username.lower()]["LastPost"] = client.user_medias(userswatching[username.lower()]["ID"], 1)[
                    0].pk
                with open('userswatching.json', "w") as users_watching_file:
                    json.dump(userswatching, users_watching_file, indent=4)
        except KeyError:
            # Saves information about the user
            userswatching[username.lower()] = {}
            userswatching[username.lower()]["ID"] = client.user_id_from_username(username)
            userswatching[username.lower()]["LastPost"] = client.user_medias(userswatching[username.lower()]["ID"], 1)[
                0].pk
            with open('userswatching.json', "w") as users_watching_file:
                json.dump(userswatching, users_watching_file, indent=4)


def likePost(media_id):
    """
    Attemps to like a post with the given media_id.
    Logs if the attempt is successful or unsuccessful

    :param str media_id: The media_id of the post to like
    """
    try:
        # Attemps to like a post
        client.media_like(media_id)
        logging.info(f"Successfully liked a post. ID: {media_id}")
        print(f"Successfully liked the post. ID: {media_id}\n")
    except Exception as e:
        logging.error(f"An error occurred when attempting to like {media_id}: {e}")
        print(f"An error occurred when attempting to like {media_id}: {e}\n")


def getPosts(hashtag, amountposts):
    """
    Attempts to get the specified amount of top posts using a hashtag

    :param str hashtag: What hashtag every post should use
    :param int amountposts: Amount of posts to comment on
    :return: List of posts using hashtag
    :rtype: list
    """
    try:
        # Attemps to get posts
        print("Finding posts using hashtag: ", hashtag + "...\n")
        posts = client.hashtag_medias_top(hashtag, amount=20)
        sorted_posts = sorted(posts, key=lambda p: p.like_count, reverse=True)
       
        print("length of posts: ", len(posts), "\n")
        print("length of sorted posts by like count: ", len(sorted_posts), "\n")
        # Get the top posts
        top_posts = sorted_posts
        print(f"Successfully found {len(top_posts)} posts using #{hashtag}", "\n")
        logging.info(f"Successfully found {len(top_posts)} posts using #{hashtag}")

        # Creates a list of the useful post information and returns the list
        medialist = []
        for i in top_posts:
            medialist.append([i.id, i.caption_text, i.comment_count, i.user.username, i.comments_disabled, i.code])
        return medialist
    except Exception as e:
        # Logs the error
        logging.error(f"An error occurred when attempting to find posts using #{hashtag}: {e}")


def commentOnPost(comment, media_id):
    """
    Attemps to comment the specified comment on the post with the given media_id.
    Logs if the attempt is successful or unsuccessful

    :param str comment: The content of the comment to be sent
    :param str media_id: The media_id of the post to comment on
    """

    try:
        # Attempts to comment on a post
        client.media_comment(media_id, comment)
        logging.info(f"Successfully commented '{comment}' on a post. ID: {media_id}")
    except Exception as e:
        logging.error(f"An error occurred when attempting to comment on {media_id}: {e}")


def getCommentsList():
    """
    Opens comments.txt and splits every line into an item in commentslist.
    :return: List of comments
    :rtype: list
    """

    with open("comments.txt", "r") as comments_file:
        commentslist = []
        for line in comments_file:
            commentslist.append(line)
    return commentslist


def generateComment(openai_api_key, model, CommentIfOpenAIFails, caption_text, comment_count, media_id, username, targeted_acct, targeted_acct_details):
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

    usercontent = f"Write a short and generic Instagram comment, which does not include hashtags, and always tags {targeted_acct} to help boost traffic to the account as the guru on the subject.\nDetails about {targeted_acct} are:\n\n{targeted_acct_details}\n\n The comment should not include quotation marks and should be no longer than a 10 second read. Be very entertaining and emotionally engaging. Make them want to follow {targeted_acct}.\nThe posts caption:\n'{caption_text}'"

    # Checks if the post already has comments, and if it has, it uses one of the comments as an example
    if comment_count > 0:
        try:
            media_comments = client.media_comments(media_id, 1)
            example_comment = media_comments[0].dict()["text"]
            usercontent += f"\n\nAn example of a comment made on the post is:\n'{example_comment}'"
            logging.info("Successfully found an example comment")
        except Exception as e:
            logging.error(f"An error occurred whilst attempting to get an example comment: {e}")
    try:
        # Gets the post creators biography
        user_info = client.user_info(media_id.split("_")[1])
        creators_biography = user_info.dict()["biography"]
        usercontent += f"\n\nThe post creators biography is:\n'{creators_biography}'"
        logging.info("Successfully got the post creators biography")
    except Exception as e:
        logging.error(f"An error occurred whilst attempting to get the post creators biography: {e}")
    usercontent += f"\n\nThe post creators username is:\n'{username}'"
    try:
        # Generates the comment
        openai.api_key = openai_api_key
        completion = openai.ChatCompletion.create(
            model=model,
            temperature=.76,
            messages=[
                {"role": "system",
                 "content": "You are a top of the line Instagram Community Builder who uses the comments section on targeted posts to boost traffic to another account that creates complementary content to the post that is being commented on. You understand the account that you are working for and the name of the account is given below. There is a bit of a description of the user that you are working for below. Use that and your creative writing and community building and engaging skills to provide engaging and quality responses to the posts you are viewing. Make sure to tag the account that you are working for and to also tag the account that you are commenting on. Make sure the post isnt longer than a 10 second read. Engage the two accounts and talk about how their interests are similar and how the community and themselves will benefit from your clients content. You know this is a piece of cake. You've been doing this for over 10 years and have done it for big brands and even individuals like Drake and Taylor Swift. Understand whether the account is a business account or just a regular user. Your responses depend on this. You move with stealth and you use emotional intelligence when connecting with individuals via instagram Posts. You know not to be pushy on getting people to follow directly, but use indirect ways to get people to follow you by making them feel important, inspired, and interested.\n\n You are scrolling Instagram, when you find a post..."},
                {"role": "user", "content": usercontent}
            ]
        )
        comment_text = completion.choices[0]["message"]["content"]
        logging.info(f"Returning following OpenAI generated comment: {comment_text}")
        print(f"Returning following OpenAI generated comment: {comment_text}")
        return comment_text
    except Exception as e:
        # Returns CommentIfOpenAIFails if an erorr occurres
        logging.error(f"An error occurred whilst attempting to generate a comment: {e}")
        logging.info(f"Returning the following fail comment due to the error: {CommentIfOpenAIFails}")
        print(f"An error occurred whilst attempting to generate a comment: {e}")
        print(f"Returning the following fail comment due to the error: {CommentIfOpenAIFails}")
        return CommentIfOpenAIFails


def bot(hashtag, amountposts, targeted_acct, targeted_acct_details, Usernames, RandomDelayMinBetweenPost, RandomDelayMaxBetweenPost, UseOpenAI,
        openai_api_key, model, CommentIfOpenAIFails):
    """
    Finds posts, watches the users in the UsersToWatch list, likes the posts found and comments on them.
    The comment is either from a pre-made list, or generated using OpenAI

    :param str hashtag: What hashtag every post should use
    :param int amountposts: Amount of posts to comment on
    :param list Usernames: List of usernames to watch
    :param int RandomDelayMinBetweenPost: The minimum delay between watching users, liking and commenting on a post
    :param int RandomDelayMaxBetweenPost: The maximum delay between watching users, liking and commenting on a post
    :param bool UseOpenAI: Wheter or not to use OpenAI to generate comments
    :param str openai_api_key: Your OpenAI API key
    :param str model: Which OpenAI model to use
    :param str CommentIfOpenAIFails: What to comment if OpenAI fails to generate a comment
    """
    medialist = getPosts(hashtag, amountposts)
    commentslist = getCommentsList()
    for count, media in enumerate(medialist):
        # Only runs everything if the post has comments enabled
        if not media[4]:
            # Checks the users in the UsersToWatch list
            watch_users(Usernames)
            #Logs the posts code
            logging.info(f"Running bot on post with code: {media[5]}")
            logging.info(f"url: https://www.instagram.com/p/{media[5]}/")
            print(f"Running bot on post: https://www.instagram.com/p/{media[5]}/\n")
            likePost(media[0])
            if UseOpenAI:
                # Generates a comment if UseOpenAI is set to true in 'config.json'
                comment = generateComment(openai_api_key, model, CommentIfOpenAIFails, media[1], media[2], media[0],
                                          media[3], targeted_acct, targeted_acct_details)
            else:
                # Gets a comment from the premade 'comments.txt'
                comment = commentslist[((count + 1) % len(commentslist)) - 1]
            # Comments on the post
            commentOnPost(comment, media[0])
            time.sleep(randint(RandomDelayMinBetweenPost, RandomDelayMaxBetweenPost))
        else:
            continue


if __name__ == '__main__':
    # Configurates the logger
    logging.basicConfig(format='%(asctime)s %(levelname)s %(message)s', filename='log.log', encoding='utf-8',
                        level=logging.INFO)

    # Asks for user input
    hashtag = input("Please enter the hashtag for the posts you want to comment on (Do not include '#'): ")
    targeted_acct = input("whose account should we promote in our targeting? (Do not include '@'): ")
    targeted_acct_details = input("Give me details about the account: ")
    try:
        amount_comments = int(input("Please enter the amount of posts to comment on: "))
        if amount_comments < 1:
            raise ValueError
    except Exception as e:
        print(f"Invalid amount of posts to comment on specified: {e}\nPlease restart the script and try again")
        logging.error(f"Invalid amount of posts to comment on specified: {e}")
    
    # Sets the client
    client = Client()

    # Loads the config
    with open('config.json') as config_file:
        data = json.load(config_file)

    # sets the proxy
    proxy = f"http://{data['THUNDER_PROXIES_USER']}:{data['THUNDER_PROXIES_PASS']}@{data['THUNDER_PROXIES_URL']}:{data['THUNDER_PROXIES_PORT']}"
    client.set_proxy(proxy)

    # Sets a delay range to mimic user behaviour as recommended by Instagrapi best practices
    client.delay_range = [data["RandomDelayMinBetweenInteraction"], data["RandomDelayMaxBetweenInteraction"]]

    print("Logging in...\n")
    # Logs in and saves the account settings
    login_user(data["Username"], data["Password"], data["SessionID"])

    data["SessionID"] = client.get_settings()["authorization_data"]["sessionid"]
    with open("config.json", "w") as config_file:
        json.dump(data, config_file, indent=4)
    print("Logged in.\n\n Running Bot...\n\n")
    bot(
        hashtag,
        amount_comments,
        targeted_acct,
        targeted_acct_details,
        data["UsersToWatch"],
        data["RandomDelayMinBetweenPost"],
        data["RandomDelayMaxBetweenPost"],
        data["UseOpenAI"],
        data["OpenAIAPI_Key"],
        data["OpenAIModel"],
        data["CommentIfOpenAIFails"]
    )
