# 🛡️ Guardian AI  
### *Your Personal Multimodal Guardian — Powered by Google Gemma 3n*

<p align="center">
  <img src="logo/logo1.webp" width="150" alt="Guardian AI Logo">
</p>

---

## 🚀 The Story Begins: *A Thought, A Promise, A Guardian*

I started with a vision: **AI that truly understands—privately and on-device**.  
In a world of cloud-first AI, **Guardian AI flips the script**.

It listens (*audio*), sees (*images*), and converses (*text*)—but all **decisions, emotional cue detection, and emergency actions** are made exclusively by **Gemma 3n**. Never outsourced. Never streamed.

While `Whisper` and `BLIP` from Hugging Face assist with **transcription** and **image captioning**,  
**Gemma 3n** remains the ultimate arbiter—**digesting all inputs and deciding**:  
> ➤ *Respond*  ➤ *Nudge*  ➤ *Notify Contacts*  

All under one **holistic judgment framework**.

---

## 🔍 Why This Problem, Why Now

- 🛡️ **Privacy-first imperative**:  
  *Gemma 3n works entirely offline*. Your voice, photos, and thoughts **never leave your device**.

- 🔗 **Multimodal synergy**:  
  Gemma 3n is **the only local model** to seamlessly unify *audio*, *image*, and *text*—offering **context-aware assistance** with zero cloud latency.

- 💡 **Edge-ready intelligence**:  
  Built for real-world usage. This system runs comfortably on ~2 GB RAM using tools like `E2B`, proving the **power of on-device AI**.

> 🧠 **In short**:  
>   **Gemma 3n** is the *brain*;  
>   **Whisper** and **BLIP** are just its *sensory organs*.

---

## 🧠 Core Architecture & Decision Flow

### 1. 🌀 Preprocessing Stage
- 🎙️ **Audio**:  
  Transcribed using `WhisperProcessor` + `WhisperForConditionalGeneration`.

- 🖼️ **Image**:  
  Captioned using `BlipProcessor` + `BlipForConditionalGeneration`.

---

### 2. 🧠 Decision Stage
Processed inputs are unified and passed to:
```python
GuardianAI.chat()
```

* **Gemma 3n** evaluates:

  * Emotional tone  
  * Urgency  
  * Context  

* It then returns structured JSON:

```json
{
  "Action": "nudge" | "emergency_contact",
  "Risk": "High",
  "Analysis": "Expressing self-hatred..."
}
```

---

### 3. ✅ User Empowered Control

If a critical action is recommended:

* A **confirmation prompt** is shown in the UI  
* **No action** is taken without **explicit user consent**  
* Alerts (if approved) are formatted and sent to emergency contacts

> 🔒 **Gemma 3n never delegates**.  
> `Whisper` and `BLIP` just describe;  
> **Gemma 3n decides.**

---

## ✨ Hero Features

✅ **Unified Multimodal Input**  
Text, audio, and images—**all flow into one stream**

🧠 **Gemma 3n as the Mind**  
Every decision is **interpreted, evaluated, and acted on** by Gemma 3n

🔐 **Resilient, Private, On-Device**  
No internet required. No remote trust assumptions.

🛑 **Empowered User Confirmations**  
Critical alerts are **never auto-sent**—you choose.

🎨 **Stylish & Accessible UI**  
Built with Streamlit — featuring **dark theme**, **chat bubbles**, and **alert boxes**

---

## 🚧 Setup & Quick Walkthrough

> **Demo:**  
> Deployed on Streamlit using Gemma 3n inference endpoint *(link coming soon)*.

> **Run Locally in 3 Simple Steps:**

```bash
# 1. Clone the repo and install dependencies
git clone https://github.com/your-username/guardian-ai.git
cd guardian-ai
pip install -r requirements.txt

# 2. Set the Ollama host
set OLLAMA_HOST=127.0.0.1:11502  # Windows
# or export OLLAMA_HOST=127.0.0.1:11502  # Mac/Linux

# 3. Start Ollama server
ollama serve
```

Then simply run the app via:

```bash
streamlit run app.py
```

You’re now ready to explore Guardian AI locally ✨

---

## ❤️ Final Thoughts

**Guardian AI isn’t just software.**  
It’s a **narrative of trust**.

You share your voice. Your visuals.  
And **Gemma 3n listens**—**safely**, **privately**, and **in full control**.

> Whisper and BLIP bring the world in.  
> **Gemma 3n decides what matters.**  
> That’s what makes this truly your *Guardian*.
