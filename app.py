import streamlit as st
import praw

# Initialize Reddit API client
reddit = praw.Reddit(
    client_id=st.secrets["reddit"]["client_id"],
    client_secret=st.secrets["reddit"]["client_secret"],
    user_agent=st.secrets["reddit"]["user_agent"],
)

# Initialize session state for shared browsing
if "post_index" not in st.session_state:
    st.session_state.post_index = 0

# Title and description
st.title("Reddit Together")
st.write("Browse Reddit with a friend in real-time!")

# Input for subreddit
subreddit_name = st.text_input("Enter a subreddit (e.g., 'python')", "python")

# Fetch posts from Reddit
def fetch_posts(subreddit_name):
    try:
        subreddit = reddit.subreddit(subreddit_name)
        return [
            {"title": post.title, "url": post.url, "score": post.score}
            for post in subreddit.hot(limit=50)
        ]
    except Exception as e:
        st.error(f"Failed to fetch posts: {e}")
        return []

posts = fetch_posts(subreddit_name)

# Navigation buttons
col1, col2 = st.columns([1, 1])
with col1:
    if st.button("Previous") and st.session_state.post_index > 0:
        st.session_state.post_index -= 1
with col2:
    if st.button("Next") and st.session_state.post_index < len(posts) - 1:
        st.session_state.post_index += 1

# Display current post
if posts:
    post = posts[st.session_state.post_index]
    st.write(f"### {post['title']}")
    st.write(f"👍 {post['score']} upvotes")
    st.write(f"[Read more]({post['url']})")
else:
    st.write("No posts to display.")
