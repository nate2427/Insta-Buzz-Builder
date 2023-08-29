import streamlit as st
from insta_bot import InstaBot as bot
from db import add_new_persona_config, get_all_persona_configs
from gpt_prompts import get_prompt, update_persona_prompt_template



def login_bot():
    st.session_state.bot = bot()

def generate_comments_page():
    col1, col2 = st.columns([1, 2])

    # Check if 'post_url' exists in session state
    if 'post_url' not in st.session_state:
        st.session_state.post_url = ""

    # Initialize AI comments in session state if not present
    if 'ai_comments' not in st.session_state:
        st.session_state.ai_comments = {}

    if 'post' not in st.session_state:
        st.session_state.post = ""
    
    if 'subreddit' not in st.session_state:
        st.session_state.subreddit = ""
    
    if 'subreddit_description' not in st.session_state:
        st.session_state.subreddit_description = ""
    
    if 'subreddit_summary' not in st.session_state:
        st.session_state.subreddit_summary = ""
    

    st.session_state.post_url = col1.text_input("Instagram post URL", value=st.session_state.post_url)
    search_button = col1.button("search")
    
    if "personas" not in st.session_state:
        st.session_state.personas = get_all_persona_configs()
    if search_button:
        # st.session_state.post_url = post_url
        # with st.spinner("Loading..."):
        if "bot" not in st.session_state:
            login_bot()
        st.session_state.post_info = st.session_state.bot.get_instagram_post(post_url=st.session_state.post_url)
    #     st.session_state.comments = bot.grab_comments(st.session_state.post)
        st.session_state.selected_persona = col2.selectbox("Choose A Persona", st.session_state.personas.keys(), index=0 if 'selected_persona' not in st.session_state else list(st.session_state.personas.keys()).index(st.session_state.selected_persona))
    elif 'selected_persona' in st.session_state:
        st.session_state.selected_persona = col2.selectbox("Choose A Persona", st.session_state.personas.keys(), index=list(st.session_state.personas.keys()).index(st.session_state.selected_persona))

    if 'bot' in st.session_state and "post_info" in st.session_state:
        # sidebar configuration section
        st.sidebar.title("Instagram Post")
        st.sidebar.text_area("Post", f"{st.session_state.post_info.title}", label_visibility="hidden", height=250)
        st.sidebar.text(f"Author: {st.session_state.post_info.author_name}")

        # show selected persona prompt template in sidebar
        persona_prompt = get_prompt(st.session_state.personas[st.session_state.selected_persona])
        persona_prompt_text_area = st.sidebar.text_area("Persona: 🧑🏾‍🦱", persona_prompt, height=250)
        if st.sidebar.button("Update Persona"):
            st.sidebar.info(f"{st.session_state.personas[st.session_state.selected_persona]} \n\n {persona_prompt_text_area}")
            if update_persona_prompt_template(st.session_state.personas[st.session_state.selected_persona], persona_prompt_text_area):
                st.sidebar.success("Updated!")
            else:
                st.sidebar.error("Failed Upating Persona!")

        # Generate Reel AI Summary section
        st.header("Generate Reel AI Summary")
        summary_container = st.empty()
        if st.button("Generate Reel AI Summary"):
            summary_container.empty()
            with st.spinner("Analyzing Reel..."):
                reel_summary = st.session_state.bot.summarize_reel(st.session_state.post_url)
            st.session_state.reel_summary = st.text_area("Summary", reel_summary)
            st.experimental_rerun()
        elif "reel_summary" in st.session_state:
            st.session_state.reel_summary = summary_container.text_area("Summary", f"{st.session_state.reel_summary}", height=150)

        # # write a comment on post section
        st.header("Generate a Comment on the Post")
        comment_container = st.empty()
        comment_but_col1, comment_but_col2, comment_but_col3 = st.columns(3)
        generate_comment_button = comment_but_col1.button("Generate Comment", key="generate_comment")
        regenerate_comment_button = comment_but_col2.button("Regenerate Comment", key="regenerate_comment", disabled="generated_comment" not in st.session_state)
        post_comment_button = comment_but_col3.button("Post Comment", key="post_comment", disabled="generated_comment" not in st.session_state)
        if generate_comment_button:
            with st.spinner("Generating..."):

                ai_generated_comment = st.session_state.bot.generateComment(st.session_state.post_info.title, 1, st.session_state.post_info.media_id, st.session_state.post_info.author_name, st.session_state.bot.username, st.session_state.reel_summary, persona_prompt_text_area)
                comment_container.empty()
            st.session_state.generated_comment = comment_container.text_area("🤖 AI Generated Comment 📝:", f"{ai_generated_comment}", height=200, key="ngenerated_comment_0")
            st.experimental_rerun()
        elif "generated_comment" in st.session_state:
            st.session_state.generated_comment = comment_container.text_area("🤖 AI Generated Comment 📝:", f"{st.session_state.generated_comment}", height=200, key="generated_comment_0")

        if regenerate_comment_button:
            with st.spinner("Regenerating..."):
                ai_regenerated_comment =  st.session_state.bot.regenerateComment(st.session_state.post_info.title, 1, st.session_state.post_info.media_id, st.session_state.post_info.author_name, st.session_state.bot.username, st.session_state.reel_summary, st.session_state.generated_comment,  persona_prompt_text_area)
                comment_container.empty()
            st.session_state.generated_comment = comment_container.text_area("🤖 AI Generated Comment 📝:", f"{ai_regenerated_comment}", height=200, key="regenerated_comment_0")

        if post_comment_button:
            with st.spinner("Posting..."):
                if st.session_state.bot.commentOnPost(st.session_state.generated_comment, st.session_state.post_info.media_id):
                    st.success("Comment Posted!")
                else:
                    st.error("Failed to post comment!")

        # comments section
        st.header("Top Level Comments")
        if "comments" not in st.session_state:
            st.session_state.comments = st.session_state.bot.get_comments_from_post(st.session_state.post_info.media_id)
        for i, comment in enumerate(st.session_state.comments):
            comment_author = comment.user.username
            comment_body = comment.text
            st.text_area("Comment", f"{comment_body}", height=50, label_visibility="hidden", key="comment_{}".format(str(i)), disabled=True)
            container = st.empty()
            st.text(f"Author: {comment_author}")
            # Buttons to interact with comment
            but_col1, but_col2, but_col3 = st.columns(3)
            generate_ai_comment_button = but_col1.button("Generate AI\nResponse", key=f'generate_ai_comment_{i}')
            regenerate_button = but_col2.button("Regenerate Response", key=f'regenerate_{i}', disabled=i not in st.session_state.ai_comments)
            post_reply_button = but_col3.button("Reply to Comment", key=f'post_comment_{i}', disabled=i not in st.session_state.ai_comments)

            # Generate Button Click Handler
            
            if generate_ai_comment_button:
                with st.spinner("Generating..."):
                    ai_comment = st.session_state.bot.generate_reply_to_comment(st.session_state.post_info.title, comment_body,comment_author, st.session_state.bot.username, st.session_state.reel_summary, persona_prompt_text_area)
                
                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{ai_comment}", height=200, key="ai_comment_{}".format(str(i)))
                st.experimental_rerun()
            elif i in st.session_state.ai_comments:
                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{st.session_state.ai_comments[i]}", height=200, key="ai_comment_{}".format(str(i)))


            # Regenerate Button Click Handler
            if regenerate_button:
                container.empty()
                with st.spinner("Regenerating..."):
                    ai_comment = st.session_state.bot.regenerate_reply_to_comment(st.session_state.post_info.title, comment_body,comment_author, st.session_state.bot.username, st.session_state.reel_summary, st.session_state.ai_comments[i], persona_prompt_text_area)

                st.session_state.ai_comments[i] = container.text_area("🤖 AI Generated Comment 📝:", f"{ai_comment}", height=200, key="ai_regen_comment_{}".format(str(i)))


            # Post Comment Button Click Handler
            if post_reply_button:
                with st.spinner("Replying..."):
                    if st.session_state.bot.reply_to_comment(st.session_state.post_info.media_id, comment.pk, st.session_state.ai_comments[i]):
                        container.empty()
                        st.success("Successfully replied to comment!")
                    else:
                        st.error("Failed to reply to comment!")


def add_persona_config():
    persona_name = st.text_input("New Persona Title", placeholder="GPT Instructor")
    persona_prompt_id = st.text_input("Persona Prompt ID", placeholder="gpt_instructor")
    button = st.button("Add Persona")
    # add this persona to the db
    if button:
        if add_new_persona_config(persona_name, persona_prompt_id):
            st.success("Successfully added new persona!")
        else:
            st.error("Failed to add new persona!")

# Set up sidebar
pages = ["Generate Comments", "Add New Persona"]
st.title("🤖 Instagram Buzz Builder 🤖")
selected_page = st.selectbox("Pages", pages, label_visibility="hidden")

# Display selected page
if selected_page == "Generate Comments":
    generate_comments_page()
elif selected_page == "Add New Persona":
    add_persona_config()

