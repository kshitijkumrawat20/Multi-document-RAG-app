# Use official Python image as base
FROM python:3.12-slim

# Create a non-root user
RUN useradd -m -u 1000 user
USER user
ENV PATH="/home/user/.local/bin:$PATH"

WORKDIR /app

# Install dependencies as user
COPY --chown=user ./requirements.txt requirements.txt
RUN pip install --no-cache-dir --upgrade -r requirements.txt

# Copy all files as user
COPY --chown=user . /app

# Expose Hugging Face Spaces default port
EXPOSE 7860

# Start FastAPI app with Uvicorn on port 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
