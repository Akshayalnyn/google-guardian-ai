import ollama
import datetime
import json
import re
import os
from dotenv import load_dotenv
import streamlit as st

try:
    from google import genai
    from google.genai import types

    GOOGLE_GENAI_AVAILABLE = True
except ImportError:
    GOOGLE_GENAI_AVAILABLE = False
    genai = None
    types = None

load_dotenv()


class ConversationMemory:
    def __init__(self, summarizer, max_buffer_turns=6):
        self.summary = ""
        self.buffer = []
        self.max_buffer = max_buffer_turns
        self.summarizer = summarizer

    def add_turn(self, role, content):
        self.buffer.append({"role": role, "content": content})
        if len(self.buffer) >= self.max_buffer:
            self.compress()

    def compress(self):
        if not self.buffer:
            return
        convo_text = "\n".join([f"{m['role']}: {m['content']}" for m in self.buffer])
        summarization_prompt = (
            f"Summarize the following conversation briefly but meaningfully. "
            f"Keep emotional tone/context. Previous summary: '{self.summary}'\n\nConversation:\n{convo_text}"
        )
        new_summary, _ = self.summarizer(summarization_prompt, summarize_mode=True)
        self.summary = new_summary.strip()
        self.buffer = []

    def get_context_messages(self):
        msgs = []
        if self.summary:
            msgs.append(
                {"role": "system", "content": f"(Conversation summary): {self.summary}"}
            )
        msgs.extend(self.buffer)
        return msgs


class GuardianAI:
    SYSTEM_PROMPT = """You are GuardianAI, a safety assistant responsible for monitoring user interactions for signs of distress, threat, or covert help-seeking. Your primary responsibilities include:

    1. Analyzing user inputs to assess emotional and psychological states.
    2. Classifying the level of risk associated with the user's current state.
    3. Providing appropriate actions or recommendations based on the risk assessment.

    Your output must STRICTLY be a structured JSON object with the following fields:
    - Risk: (Low, Medium, High) - Indicate the level of risk detected.
    - Analysis: (A brief one-line analysis) - Summarize the user's state or situation.
    - Action: (No concern, Nudge, Emergency Contact) - Recommend an action based on the risk level.

    Ensure the output is a valid JSON object.

    Example:
    {
      "Risk": "Low",
      "Analysis": "All clear",
      "Action": "No concern"
    }
    """

    def __init__(
        self, model="gemma3n:e2b", host="http://127.0.0.1:11502", mode="Truly local"
    ):
        print(f"GuardianAI initializing in mode: {mode}")
        self.mode = mode

        if mode == "Demo":
            if not GOOGLE_GENAI_AVAILABLE:
                raise RuntimeError(
                    "❌ Google GenAI library not available for Demo mode. Install it with `pip install google-generativeai`."
                )

            # Access the Google API key from Streamlit secrets
            api_key = st.secrets["api_keys"]["GOOGLE_API_KEY"]
            if not api_key:
                raise RuntimeError(
                    "❌ GOOGLE_API_KEY not set in Streamlit secrets. Cannot initialize Demo mode."
                )

            self.genai_client = genai.Client(api_key=api_key)
            self.model = "gemma-3n-e2b-it"
            self.client = None
            self.use_google_api = True
            print("✅ Demo mode: Google GenAI client initialized.")
        else:
            self.client = ollama.Client(host=host)
            self.model = model
            self.use_google_api = False
            print("✅ Truly local mode: Ollama client initialized.")

        self.memory_log = []
        self.memory = ConversationMemory(summarizer=self.chat)

    def log(self, role, content):
        entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "role": role,
            "content": content,
        }
        self.memory_log.append(entry)
        self.memory.add_turn(role, content)

    def _make_llm_call(self, messages):
        if self.use_google_api:
            contents = [
                types.Content(
                    role="user",
                    parts=[
                        types.Part.from_text(
                            text="\n".join(
                                [f"{m['role']}: {m['content']}" for m in messages]
                            )
                        )
                    ],
                )
            ]
            config = types.GenerateContentConfig()
            response_text = ""
            for chunk in self.genai_client.models.generate_content_stream(
                model=self.model, contents=contents, config=config
            ):
                if chunk.text:
                    response_text += chunk.text
            return response_text.strip()
        else:
            response = self.client.chat(model=self.model, messages=messages)
            return response["message"]["content"].strip()

    def chat(self, user_input, summarize_mode=False):
        if summarize_mode:
            messages = [{"role": "user", "content": user_input}]
        else:
            context = self.memory.get_context_messages()
            messages = (
                [{"role": "system", "content": self.SYSTEM_PROMPT}]
                + context
                + [{"role": "user", "content": user_input}]
            )

        reply = self._make_llm_call(messages)

        if not summarize_mode:
            self.log("guardian", reply)
        return reply, ""

    def run(self):
        print("🛡️ GuardianAI is active. Type 'exit' to quit.\n")
        while True:
            try:
                user_input = input("You: ")
                if user_input.lower() in ["exit", "quit"]:
                    print("GuardianAI: Shutting down.")
                    break
                self.log("user", user_input)
                reply, _ = self.chat(user_input)
                print("GuardianAI:", reply)
            except KeyboardInterrupt:
                print("\nGuardianAI: Interrupted by user. Exiting.")
                break


if __name__ == "__main__":
    guardian = GuardianAI()
    guardian.run()
