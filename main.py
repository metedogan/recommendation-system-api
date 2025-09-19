import uvicorn
import sys
import os

def main():
    # Ensure src is in the Python path
    sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), 'src')))
    # Run the FastAPI app from src/api.py
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)


if __name__ == "__main__":
    main()
