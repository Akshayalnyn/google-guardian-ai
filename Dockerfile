FROM python:3.10-slim

# Create a non-root user (UID 1000 is required for Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Set environment variables
ENV HOME=/home/user \
    PATH="/home/user/.local/bin:$PATH"

WORKDIR $HOME/app
USER user

# Copy your app code
COPY --chown=user:user . $HOME/app/

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Explicitly set Streamlit config directory to avoid root access errors
ENV STREAMLIT_HOME=$HOME/.streamlit
ENV STREAMLIT_CONFIG_DIR=$STREAMLIT_HOME

# Expose the default Streamlit port
EXPOSE 8501

# Run your app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port", "8501", "--server.headless", "true"]
