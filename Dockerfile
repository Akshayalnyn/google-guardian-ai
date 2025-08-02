# 1️⃣ Use Python image
FROM python:3.10-slim

# 2️⃣ Avoid permission issues on HF (runs as UID1000)
RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

# 3️⃣ Install system deps (if needed)
RUN apt update && \
    pip install --no-cache-dir --upgrade pip

# 4️⃣ Copy files
COPY --chown=user:$(id -u) . $HOME/app/

# 5️⃣ Install Python deps
RUN pip install --no-cache-dir -r requirements.txt

# 6️⃣ Set entrypoint
EXPOSE 8501
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.headless", "true"]
