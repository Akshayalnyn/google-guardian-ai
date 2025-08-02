FROM python:3.10-slim

# Create a non-root user (UID 1000 is required for Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Set environment variables
ENV HOME=/home/user \
    PATH="/home/user/.local/bin:$PATH"

# Use HOME as working directory
WORKDIR $HOME/app

# Copy app code and config directory
COPY --chown=user:user . $HOME/app/

# Ensure the .streamlit directory exists and is writable
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

# Switch to non-root user for security
USER user

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the default Streamlit port
EXPOSE 8501

# Set environment variable to fix Streamlit config permission issue
ENV STREAMLIT_CONFIG_DIR=$HOME/app/.streamlit

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py"]
