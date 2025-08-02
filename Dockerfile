FROM python:3.10-slim

# Create a non-root user (UID 1000 is required for Hugging Face Spaces)
RUN useradd -m -u 1000 user

# Set environment variables
ENV HOME=/home/user \
    PATH="/home/user/.local/bin:$PATH" \
    STREAMLIT_HOME=/home/user/.streamlit \
    STREAMLIT_CONFIG_DIR=/home/user/.streamlit

# Set working directory
WORKDIR $HOME/app

# Copy app code and change ownership
COPY --chown=user:user . $HOME/app/

# Create .streamlit directory with proper permissions
RUN mkdir -p /home/user/.streamlit && chown -R user:user /home/user/.streamlit

# Switch to non-root user
USER user

# Install dependencies
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expose the default Streamlit port
EXPOSE 8501

# Run the Streamlit app
ENTRYPOINT ["streamlit", "run", "streamlit_app.py", "--server.port=8501", "--server.headless=true"]
