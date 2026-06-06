from backend.main import app

# Vercel needs the app object to be named 'app' at the top level
# of this file to treat it as the FastAPI entry point.
app = app
