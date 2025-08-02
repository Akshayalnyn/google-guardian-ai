---
title: Google Guardian AI
sdk: docker
app_port: 8501       # streamlit default port; tailors internal HTTP listener
emoji: 🛡️
colorFrom: blue
colorTo: cyan
---

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
Every decision is **interpreted, evaluated, and acted on** by Gemma 3n using Ollama

🔐 **Resilient, Private, On-Device**  
No internet required. No remote trust assumptions.

🛑 **Empowered User Confirmations**  
Critical alerts are **never auto-sent** in assistive mode—you choose between assistive and automated usage.

🎨 **Stylish & Accessible UI**  
Built with Streamlit — featuring **sleek theme**, **chat bubbles**, and **alert boxes**

---

## 🚧 Setup & Quick Walkthrough

> **Demo:**  
> Deployed on Streamlit using Gemma 3n inference endpoint *(link coming soon)*.

<img width="1000" height="720" alt="image" src="https://github.com/user-attachments/assets/e104d480-6e5d-4f2a-82ad-b9ed801a121f" />



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
## 🧭 Future Work

Guardian AI is just getting started. Here's what lies ahead:

- 🔮 **Ollama Multimodal Integration**  
  As soon as `Ollama` adds multimodal support, we’ll unify *image*, *audio*, and *text* input streams directly within the same model context—removing the need for separate sensory extractors.

- 🎥 **Real-time Video Intelligence**  
  Integrate with **Google’s Video Intelligence Streaming API** for live video analysis—detecting dangerous scenarios, weapon presence, or abnormal movement patterns in real time.

- 🧷 **Violence & Safety Keyword Flags**  
  Add a semantic filter that constantly listens for high-risk phrases (e.g., *“he’s hurting me”*, *“I can’t breathe”*, *“please stop”*)—and intelligently cross-checks with tone and visual cues for context.

- 📞 **Covert Emergency Signaling**  
  Implement encoded action mechanisms. For instance:  
  > *“I’d like to order a pepperoni pizza”*  
  could be parsed as a silent cry for help when combined with emotional or visual distress cues.

- 🕵️ **Context-aware Suppression of False Alarms**  
  Add an internal memory buffer that can track ongoing state and reduce alert noise by validating urgency across multiple consecutive frames or utterances.

- 🗣️ **Multi-Lingual Emotional Cue Recognition**  
  Expand Gemma 3n’s capacity to understand emotions across regional Indian languages, dialects, and speech patterns—enhancing inclusivity.

- 🤝 **Integration with Local Emergency Protocols**  
  Allow community-specific configuration (e.g., dial *112* in India instead of *911*), with optional fallback to SMS/emails if calls aren’t feasible.

- 🧭 **AI-Suggested Safe Zones**  
  Use geolocation (optional, with permission) to guide the user to verified *safe zones* nearby—like police stations, women’s shelters, or hospitals.

---
## ❤️ Final Thoughts

**Guardian AI isn’t just software.**  
It’s a **narrative of trust**.

You share your voice. Your visuals.  
And **Gemma 3n listens**—**safely**, **privately**, and **in full control**.

> Whisper and BLIP bring the world in.  
> **Gemma 3n decides what matters.**  
> That’s what makes this truly your *Guardian*.
