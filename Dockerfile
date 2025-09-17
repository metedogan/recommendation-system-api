# Dockerfile

# 1. Use an official, lightweight Python image.
FROM python:3.13-slim

# 2. Set the working directory inside the container.
WORKDIR /app

# 3. Install uv, which will be our package manager.
RUN pip install uv

# 4. Copy only the dependency file to leverage Docker's layer caching.
# If pyproject.toml doesn't change, this layer will be cached, speeding up future builds.
COPY pyproject.toml ./

# 5. Install production dependencies using uv.
# 'uv pip sync' is fast and ensures the environment matches the lockfile exactly.
# '--no-dev' skips development dependencies (like notebook, pytest, etc.).
RUN uv pip sync pyproject.toml

# 6. Copy the rest of the application code into the container.
# This includes your 'src' folder and 'models' folder.
COPY . .

# 7. Expose the port the app runs on.
EXPOSE 8000

# 8. Define the command to run the application.
# We use "--host 0.0.0.0" to make it accessible from outside the container.
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]