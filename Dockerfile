FROM python:3.10-slim

# Create a non-root user (UID 1000 is required for Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Set environment variables
ENV HOME=/home/user \
    PATH="/home/user/.local/bin:$PATH"

WORKDIR $HOME/app

# Copy app code and config directory first
COPY --chown=user:user . $HOME/app/

# Make sure .streamlit folder exists with config
RUN mkdir -p $HOME/app/.streamlit \
    && echo "\
[server]\n\
headless = true\n\
port = 8501\n\
enableCORS = false\n\
\n\
[client]\n\
showErrorDetails = false\n\
" > $HOME/app/.streamlit/config.toml \
    && chown -R user:user $HOME/app

# Switch to non-root user
USER user

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the default Streamlit port
EXPOSE 8501

# Run the app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py"]
