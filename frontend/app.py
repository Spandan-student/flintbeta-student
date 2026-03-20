import streamlit as st
from streamlit_float import *
st.set_page_config(layout="wide")
import time
import requests
from PIL import Image
from io import BytesIO

def display_url_image(url):
    try:
        # Fetch the image content from the URL
        # Adding a User-Agent header can help avoid some server blocks
        headers = {"User-Agent": "Mozilla/5.0"}
        response = requests.get(url, headers=headers)
        response.raise_for_status() # Raise an exception for bad status codes (4XX or 5XX)

        # Open the image using Pillow from the byte stream
        image = Image.open(BytesIO(response.content))
        
        # Display the image
        image.show() 

    except requests.exceptions.RequestException as e:
        print(f"Error fetching image: {e}")
    except IOError as e:
        print(f"Error opening image: {e}")

# Initialize float feature
float_init()

# Initialize session state variables
if 'step' not in st.session_state:
    st.session_state.step = 0
if 'q_idx' not in st.session_state:
    st.session_state.q_idx = 0
if 'answers' not in st.session_state:
    st.session_state.answers = []
if 'user_info' not in st.session_state:
    st.session_state.user_info = {}

@st.cache_data
def load_questions():
    import json
    import os
    current_dir = os.path.dirname(os.path.abspath(__file__))
    file_path = os.path.join(current_dir, "questions.json")
    with open(file_path, "r", encoding="utf-8") as f:
        return json.load(f)

questions = load_questions()

def next_step():
    st.session_state.step += 1

# Injecting custom CSS to center text and buttons
st.markdown("""
    <style>
    /* Center all headers and markdown text */
    h1, h2, h3, p, div[data-testid="stMarkdownContainer"] {
        text-align: center !important;
    }
    
    /* Center buttons properly */
    div[data-testid="stButton"] {
        display: flex;
        justify-content: center !important;
        width: 100%;
    }
    div[data-testid="stButton"] button {
        margin: 0 auto;
    }

    /* Center form widget labels */
    div[data-testid="stWidgetLabel"] > div {
        display: flex;
        justify-content: center !important;
        width: 100%;
    }
    
    /* Center the radio buttons group and increase font size for options */
    div[data-testid="stRadio"] {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    div[data-testid="stRadio"] > div[role="radiogroup"] {
        width: max-content;
        margin: auto;
    }
    div[data-testid="stRadio"] div[role="radiogroup"] label p {
        font-size: 1.5rem !important; /* Increase option font size */
    }
    
    /* Center text inputs and their sizes */
    div[data-testid="stTextInput"] {
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    div[data-testid="stTextInput"] > div:nth-child(2) {
        width: 70%;
    }
    </style>
""", unsafe_allow_html=True)

# Use columns to keep the content centered and prevent it from spanning the entire wide layout
_, center_col, _ = st.columns([1, 2, 1])

with center_col:
    if st.session_state.step == 0:
        st.title("Welcome To Flint")
        st.subheader("A Personalised Dating App exclusively for BMSIT")
        st.success("It will take only 5 minutes to fill the form. Trust Me! 🙂")
        st.warning("This is the Data Collection Phase. The app will be launched very soon!")
        if st.button("👉 Next"):
            next_step()
            st.rerun()

    elif st.session_state.step == 1:
        st.title("User Information")
        st.write("Please enter your credentials below:")
        
        username = st.text_input("Username")
        email = st.text_input("Email ID")

        if st.button("✅ Done!"):
            if username and email:
                st.session_state.user_info = {"username": username, "email": email}
                next_step()
                st.rerun()
            else:
                st.error("Please fill in all credentials before proceeding.")

    elif st.session_state.step == 2:
        if st.session_state.q_idx < len(questions):
            curr_q = questions[st.session_state.q_idx]
            st.title(f"Question {st.session_state.q_idx + 1} of {len(questions)}")
            st.subheader(curr_q.get("scene", ""))
            st.subheader(curr_q["q"])
            
            # Handle options that contain images (list of dicts) vs standard text options
            opts_data = curr_q.get("opts", [])
            
            if len(opts_data) > 0 and isinstance(opts_data[0], dict):
                # Use columns to lay out images beautifully side by side, making them the clickable options 
                cols = st.columns(len(opts_data))
                for idx, opt in enumerate(opts_data):
                    with cols[idx]:
                        # Image display
                        st.markdown(
                            f"<div style='display: flex; justify-content: center;'>"
                            f"<img src='{opt['logo']}' style='width: 140px; height: 140px; object-fit: contain; border-radius: 10px; background: white; margin-bottom: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); padding: 10px;'>"
                            f"</div>", 
                            unsafe_allow_html=True
                        )
                        # Option Button (Acts as the answer selector)
                        if st.button(f"{opt['name']}", key=f"img_btn_{st.session_state.q_idx}_{idx}"):
                            st.session_state.answers.append(opt["name"])
                            st.session_state.q_idx += 1
                            if st.session_state.q_idx >= len(questions):
                                next_step()
                            st.rerun()
                            
            else:
                # Standard text options logic
                ans = st.radio("Select an answer:", opts_data, key=f"radio_{st.session_state.q_idx}")
                
                if st.button("👉 Next Question" if st.session_state.q_idx < len(questions) - 1 else "🙂 Submit"):
                    st.session_state.answers.append(ans)
                    st.session_state.q_idx += 1
                    if st.session_state.q_idx >= len(questions):
                        next_step()
                    st.rerun()

    elif st.session_state.step == 3:
        st.title("It's Done! Thanks for your time 🙂")
        # st.success(f"Thank you, {st.session_state.user_info.get('username')}! Your answers have been recorded.")
        
        # st.subheader("Your Submission:")
        # for i, ans in enumerate(st.session_state.answers):
        #     st.write(f"**Q{i+1}: {questions[i]['q']}**")
        #     st.write(f"Selected: {ans}")
        #     st.write("---")
        
        # if st.button("Restart"):
        st.success(f"Thank a lot, {st.session_state.user_info.get('username')}! Your answers have been recorded.")
        time.sleep(5)
        st.session_state.clear()
        st.rerun()

# Add a floating footer to the bottom of the page
footer_container = st.container()
with footer_container:
    st.markdown(
        """
        <div style='display: flex; justify-content: center; padding: 15px; border-top: 1px solid #ccc; width: 100%;'>
            © FlintBeta - Made with ❤️ by Spandy    
        </div>
        """, 
        unsafe_allow_html=True
    )
footer_container.float("bottom: 0; background-color: var(--default-backgroundColor); z-index: 1000;")



