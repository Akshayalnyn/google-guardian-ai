import streamlit as st
from app_agent import GuardianAI
from audio2text import processor as audio_processor, model as audio_model
from image2text import describe_image

import torch
import librosa
import datetime
import tempfile
from PIL import Image
import json
import os
import re

# -------------------------------
# User Profile Management
# -------------------------------
PROFILE_FILE = "user_profile.json"


def load_user_profile():
    """Load user profile from file or create default"""
    try:
        if os.path.exists(PROFILE_FILE):
            with open(PROFILE_FILE, "r") as f:
                return json.load(f)
        else:
            # Return default profile
            return {
                "name": "User",
                "emergency_contacts": {
                    "Mom": "+1-6948310",
                    "Dad": "+1-6648380",
                    "Spouse": "+1-67438910",
                    "Emergency": "911",
                },
                "created_at": datetime.datetime.now().isoformat(),
                "last_updated": datetime.datetime.now().isoformat(),
            }
    except Exception as e:
        st.error(f"Error loading profile: {e}")
        return {"name": "User", "emergency_contacts": {}}


def save_user_profile(profile):
    """Save user profile to file"""
    try:
        profile["last_updated"] = datetime.datetime.now().isoformat()
        with open(PROFILE_FILE, "w") as f:
            json.dump(profile, f, indent=4)
        return True
    except Exception as e:
        st.error(f"Error saving profile: {e}")
        return False


def get_user_name():
    """Get current user name from session state or profile file"""
    if "user_profile" not in st.session_state:
        st.session_state.user_profile = load_user_profile()
    return st.session_state.user_profile.get("name", "User")


# -------------------------------
# Init
# -------------------------------
# Initialize session state variables
if "model_mode" not in st.session_state:
    st.session_state.model_mode = "Local"
if "guardian" not in st.session_state:
    st.session_state.guardian = None

# Sidebar for mode selection
st.sidebar.title("Demo Mode Selection")
mode = st.sidebar.radio("Choose Demo Mode:", ["Local", "Demo"], key="model_mode")

# Initialize GuardianAI based on mode
if st.session_state.guardian is None or st.session_state.guardian.mode != mode:
    if mode == "Demo":
        st.session_state.guardian = GuardianAI(model="gemma-3n-e2b-it", mode="Demo")
    else:
        st.session_state.guardian = GuardianAI(
            model="gemma3n:e2b", host="http://127.0.0.1:11502", mode="Local"
        )

# Display current mode
st.write(f"Current Mode: {st.session_state.model_mode}")

# Load user profile
if "user_profile" not in st.session_state:
    st.session_state.user_profile = load_user_profile()

if "chat_history" not in st.session_state:
    st.session_state.chat_history = []

if "contact_log" not in st.session_state:
    st.session_state.contact_log = []

if "nudge" not in st.session_state:
    st.session_state.nudge = ""

if "mode" not in st.session_state:
    st.session_state.mode = "Assistive"

if "awaiting_confirmation" not in st.session_state:
    st.session_state.awaiting_confirmation = False

if "show_emergency" not in st.session_state:
    st.session_state.show_emergency = False


# -------------------------------
# Utilities
# -------------------------------
def process_audio(file_path):
    waveform, sr = librosa.load(file_path, sr=16000, mono=True)
    inputs = audio_processor(audio=waveform, sampling_rate=16000, return_tensors="pt")
    with torch.no_grad():
        generated_ids = audio_model.generate(inputs["input_features"])
        caption = audio_processor.batch_decode(generated_ids, skip_special_tokens=True)[
            0
        ]
    return caption


def chat_with_guardian(message):
    guardian = st.session_state.guardian
    # Use the chat method instead of process_message
    st.session_state.chat_history.append({"role": "user", "content": message})
    response, _ = guardian.chat(message)
    st.session_state.chat_history.append({"role": "assistant", "content": response})
    try:
        matches = re.findall(r"\{[\s\S]*?\}", response)
        for match in matches:
            parsed = json.loads(match)

            action = parsed.get("Action", "").strip().lower()

            if action == "emergency contact" and st.session_state.mode == "Assistive":
                st.session_state.nudge = "🚨 GuardianAI suggests notifying emergency contacts. Do you want to proceed?"
                st.session_state.awaiting_confirmation = "emergency"
                break

            elif action == "nudge":
                st.session_state.nudge = "💛 I noticed some signs of distress. Just checking in — If you are in danger, please let me know."
                st.session_state.awaiting_confirmation = "nudge"
                break

            elif action == "emergency contact":
                if st.session_state.mode == "Autonomous":
                    confirm_emergency_action("yes")
                else:
                    st.session_state.nudge = "🚨 GuardianAI suggests notifying emergency contacts. Do you want to proceed?"
                    st.session_state.awaiting_confirmation = "emergency"
                break
    except Exception as e:
        print("Emergency detection failed:", e)

    return response


def handle_audio_upload(audio_file):
    if audio_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp:
            tmp.write(audio_file.read())
            caption = process_audio(tmp.name)

            # Append audio caption as "user" input
            chat_with_guardian(f"[Audio Description] {caption}")

            st.rerun()


def handle_image_upload(image_file):
    if image_file is not None:
        with tempfile.NamedTemporaryFile(delete=False, suffix=".png") as tmp:
            image = Image.open(image_file)
            image.save(tmp.name)
            caption = describe_image(tmp.name)

            chat_with_guardian(f"[Image Description] {caption}")
            st.rerun()


def render_contact_log():
    for who, msg in st.session_state.contact_log:
        st.markdown(
            f"""
            <div style='margin-bottom:16px'>
                <div style='color:#8be9fd;font-weight:bold;margin-bottom:4px'>{who}</div>
                {msg}
            </div>
            """,
            unsafe_allow_html=True,
        )


def render_log():
    guardian = st.session_state.guardian
    if guardian is None:
        st.write("📝 Select a model mode to see conversation logs")
        return
    if not guardian.memory_log:
        st.write("📝 No conversation log entries yet.")
        return

    formatted_lines = []
    for entry in guardian.memory_log:
        timestamp = entry["timestamp"].split("T")[1][:8]
        role = entry["role"].capitalize()
        content = entry["content"]

        # Try parsing any embedded JSON
        matches = re.findall(r"\{[\s\S]*?\}", content)
        parsed = {}
        for json_str in reversed(matches):
            try:
                parsed = json.loads(json_str)
                if all(k in parsed for k in ["Risk", "Analysis", "Action"]):
                    break
            except json.JSONDecodeError:
                continue

        if parsed:
            formatted_lines.append(
                f"[{timestamp}] {role} (Guardian AI Analysis):\n"
                f"  • Risk: {parsed.get('Risk')}\n"
                f"  • Analysis: {parsed.get('Analysis')}\n"
                f"  • Action: {parsed.get('Action')}\n"
            )
        else:
            formatted_lines.append(f"[{timestamp}] {role}: {content}")

    st.code("\n".join(formatted_lines), language="text")


def confirm_emergency_action(choice):
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    user_name = get_user_name()

    # Get current emergency contacts first
    current_emergency_contacts = st.session_state.user_profile.get(
        "emergency_contacts", {}
    )

    if choice == "yes":
        last_message = (
            st.session_state.chat_history[-1]["content"]
            if st.session_state.chat_history
            else "GuardianAI detected an emergency."
        )

        try:
            matches = re.findall(r"\{[\s\S]*?\}", last_message)
            parsed = json.loads(matches[0]) if matches else {}

            formatted_msg = f"""
            <div style='background-color:#2d2d2d;padding:12px;border-left:5px solid red;border-radius:8px;color:#f8f8f2'>
                <strong>🚨 EMERGENCY ALERT:</strong> <span style='color:#ff6b6b'>{user_name} needs assistance</span><br><br>
                <strong>Guardian AI Analysis:</strong><br>
                • <b>Risk</b>: <span style='color:#ff5555'>{parsed.get('Risk', 'Unknown')}</span><br>
                • <b>Analysis</b>: {parsed.get('Analysis', '')}<br>
                • <b>Action</b>: {parsed.get('Action', '')}
            </div>
            """
        except Exception:
            formatted_msg = f"🚨 EMERGENCY ALERT: {user_name} needs assistance.\nGuardian AI Analysis: {last_message}"

        for contact in current_emergency_contacts:
            st.session_state.contact_log.append(
                (f"[{timestamp}] → {contact}", formatted_msg)
            )

        st.session_state.chat_history.append(
            {"role": "user", "content": f"{user_name} confirmed emergency."}
        )
        st.session_state.chat_history.append(
            {
                "role": "guardian",
                "content": f"Sent alert to all contacts:\n{formatted_msg}",
            }
        )

    else:
        st.session_state.chat_history.append(
            {"role": "user", "content": f"{user_name} declined emergency notification."}
        )
        st.session_state.chat_history.append(
            {"role": "guardian", "content": "Okay. No emergency contact was notified."}
        )

    st.session_state.nudge = ""
    st.session_state.awaiting_confirmation = False


# -------------------------------
# Page Config & Styling
# -------------------------------
st.set_page_config(page_title="Guardian AI", layout="wide")
st.markdown(
    """
<style>
/* Darker chat message background */
div[data-testid="stChatMessage"] {
    background-color: #e2e4ea !important;
    border-radius: 10px;
    padding: 1rem;
    margin-bottom: 1rem;
}

/* Guardian AI Analysis Box */
.analysis-box {
    background-color: #f6f7f9;
    padding: 1rem 1.2rem;
    border-radius: 10px;
    border: 1px solid #ccc;
    font-size: 15px;
    color: #222222;
}

/* Bold labels only */
.analysis-box b {
    font-weight: bold;
}

/* Emergency alert box */
.alert-box {
    background-color: #fa5252;
    color: white;
    padding: 1rem;
    font-weight: bold;
    border-radius: 10px;
    margin-top: 1rem;
    text-align: center;
}

/* Buttons */
div.stButton > button {
    margin: 0.5rem;
    border-radius: 8px;
    font-weight: 600;
}
</style>
""",
    unsafe_allow_html=True,
)


st.markdown(
    """
    <style>
    body {
        background-color: #0e1117;
        color: #f8f8f2;
    }
    .element-container:has(.stChatMessage) {
        padding-bottom: 5px;
    }
    .chat-container {
        background-color: #1e1e2f;
        border-radius: 12px;
        padding: 12px;
        margin-bottom: 10px;
    }
    .nudge-alert {
        background-color: #ff5555;
        color: white;
        padding: 10px;
        border-radius: 10px;
        font-weight: bold;
    }
    .google-colored {
        font-weight: bold;
        text-shadow: 1px 1px 2px #000;
        font-size: 32px;
    }
    .google-colored span:nth-child(1) { color: #4285F4; }
    .google-colored span:nth-child(2) { color: #DB4437; }
    .google-colored span:nth-child(3) { color: #F4B400; }
    .google-colored span:nth-child(4) { color: #0F9D58; }
    .google-colored span:nth-child(5) { color: #4285F4; }
    .google-colored span:nth-child(6) { color: #DB4437; }
    .google-colored span:nth-child(7) { color: #F4B400; }
    .google-colored span:nth-child(8) { color: #0F9D58; }
    </style>
""",
    unsafe_allow_html=True,
)


# -------------------------------
# Sidebar
# -------------------------------
def show_emergency_messages():
    st.session_state.show_emergency = True


def show_chat():
    st.session_state.show_emergency = False


with st.sidebar:

    # User Profile Section
    user_name = get_user_name()
    st.markdown(f"### 👤 Welcome, {user_name}!")

    with st.expander("✏️ Edit Profile"):
        with st.form("profile_form"):
            new_name = st.text_input(
                "Your Name:", value=user_name, placeholder="Enter your name"
            )

            st.markdown("**Emergency Contacts:**")
            current_contacts = st.session_state.user_profile.get(
                "emergency_contacts", {}
            )

            mom_contact = st.text_input(
                "Mom:", value=current_contacts.get("Mom", ""), placeholder="+1-xxx-xxxx"
            )
            dad_contact = st.text_input(
                "Dad:", value=current_contacts.get("Dad", ""), placeholder="+1-xxx-xxxx"
            )
            spouse_contact = st.text_input(
                "Spouse:",
                value=current_contacts.get("Spouse", ""),
                placeholder="+1-xxx-xxxx",
            )
            emergency_contact = st.text_input(
                "Emergency:",
                value=current_contacts.get("Emergency", "911"),
                placeholder="911",
            )

            if st.form_submit_button("💾 Save Profile"):
                # Update profile
                st.session_state.user_profile["name"] = (
                    new_name if new_name.strip() else "User"
                )
                st.session_state.user_profile["emergency_contacts"] = {
                    "Mom": mom_contact,
                    "Dad": dad_contact,
                    "Spouse": spouse_contact,
                    "Emergency": emergency_contact,
                }

                if save_user_profile(st.session_state.user_profile):
                    st.success("✅ Profile saved successfully!")
                    # Force rerun to update emergency contacts throughout the app
                    st.rerun()
                else:
                    st.error("❌ Failed to save profile")

    st.markdown("---")
    st.markdown("### ⚙️ Mode")
    st.radio("Select Mode", ["Assistive", "Autonomous"], key="mode")
    st.markdown("---")

    if st.session_state.show_emergency:
        st.button("🔙 Back to Chat", on_click=show_chat)
    else:
        st.button("📞 View Emergency Messages", on_click=show_emergency_messages)

    with st.expander("📜 Conversation Log"):
        render_log()

# -------------------------------
# Branding Column
# -------------------------------
col1, col2 = st.columns([1, 4], gap="medium")

with col1:
    # Try to load logo, fallback gracefully if not found
    logo_path = os.path.join(os.path.dirname(__file__), "logo", "logo1.webp")
    if os.path.exists(logo_path):
        st.image(logo_path, width=100)
    else:
        st.markdown("### 🛡️")  # Fallback emoji if logo not found

    st.markdown(
        """
        <h2 class='google-colored'>
            <span>G</span><span>u</span><span>a</span><span>r</span><span>d</span><span>i</span><span>a</span><span>n</span>
        </h2>
        """,
        unsafe_allow_html=True,
    )
    st.caption("⚙️ powered by Gemma 3n")

# -------------------------------
# Conditional View: Chat or Emergency Messages
# -------------------------------
with col2:
    if st.session_state.show_emergency:
        st.subheader("📞 Emergency Contact Messages")
        render_contact_log()
    else:
        st.subheader("💬 Your Conversation")

        # Chat History
        if not st.session_state.chat_history:
            st.write("💬 No conversation yet. Send a message to start chatting!")

        for item in st.session_state.chat_history:
            if item["role"] == "user":
                with st.chat_message("user"):
                    st.markdown(f"**You:** {item['content']}")
            elif item["role"] == "assistant":
                with st.chat_message("assistant"):
                    try:
                        matches = re.findall(r"\{[\s\S]*?\}", item["content"])
                        parsed = {}
                        if matches:
                            for json_str in reversed(matches):
                                try:
                                    parsed = json.loads(json_str)
                                    break
                                except json.JSONDecodeError:
                                    continue

                        if parsed:
                            # st.markdown("**Guardian AI Analysis**")
                            st.markdown(
                                """
                <div style="background-color:#f9f9f9; padding: 12px; border-radius: 8px; color: #000000; font-size: 16px;">
                    <div style="font-weight: bold; margin-bottom: 10px;">Guardian AI Analysis</div>
                    <div><span style="font-weight: bold;">Risk:</span> {risk}</div>
                    <div><span style="font-weight: bold;">Analysis:</span> {analysis}</div>
                    <div><span style="font-weight: bold;">Action:</span> {action}</div>
                </div>
            """.format(
                                    risk=parsed.get("Risk", "Unknown"),
                                    analysis=parsed.get("Analysis", ""),
                                    action=parsed.get("Action", ""),
                                ),
                                unsafe_allow_html=True,
                            )
                        else:
                            st.markdown(f"{item['content']}")
                    except Exception:
                        st.markdown(f"{item['content']}")

        if st.session_state.nudge:
            st.markdown(
                f"<div class='nudge-alert'>{st.session_state.nudge}</div>",
                unsafe_allow_html=True,
            )

            if st.session_state.awaiting_confirmation:
                col_yes, col_no = st.columns(2)
                if col_yes.button("✅ Yes - Notify"):
                    confirm_emergency_action("yes")
                    st.rerun()
                if col_no.button("❌ No - Don't Notify"):
                    confirm_emergency_action("no")
                    st.rerun()

        # ✅ Unified Input Section (Text + Audio + Image)
        if not st.session_state.awaiting_confirmation:
            form_key = f"chat_form_{len(st.session_state.chat_history)}"
            with st.form(key=form_key, clear_on_submit=True):
                user_input = st.text_input("Type a message...")
                submitted = st.form_submit_button("Send")
                if submitted and user_input:
                    chat_with_guardian(user_input)
                    st.rerun()

            audio_key = f"audio_file_{len(st.session_state.chat_history)}"
            audio_file = st.file_uploader(
                "Upload Audio", type=["wav", "mp3"], key=audio_key
            )
            if (
                audio_file
                and st.session_state.get("last_audio_file") != audio_file.name
            ):
                st.session_state.last_audio_file = audio_file.name
                handle_audio_upload(audio_file)

            image_key = f"image_file_{len(st.session_state.chat_history)}"
            image_file = st.file_uploader(
                "Upload Image", type=["jpg", "jpeg", "png"], key=image_key
            )
            if (
                image_file
                and st.session_state.get("last_image_file") != image_file.name
            ):
                st.session_state.last_image_file = image_file.name
                handle_image_upload(image_file)

            if st.session_state.nudge:
                st.markdown(
                    f"<div class='nudge-alert'>{st.session_state.nudge}</div>",
                    unsafe_allow_html=True,
                )

                if st.session_state.awaiting_confirmation:
                    col_yes, col_no = st.columns(2)
                    if col_yes.button("✅ Yes - Notify"):
                        confirm_emergency_action("yes")
                    if col_no.button("❌ No - Don't Notify"):
                        confirm_emergency_action("no")
