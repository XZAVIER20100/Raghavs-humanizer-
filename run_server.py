from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from backend.main import app
import os

# Add CORS middleware to allow requests from the React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Serve the frontend static files if they exist
frontend_dist = os.path.join(os.path.dirname(__file__), "frontend", "dist")
if os.path.exists(frontend_dist):
    app.mount("/assets", StaticFiles(directory=os.path.join(frontend_dist, "assets")), name="assets")

    @app.get("/")
    async def serve_frontend():
        return FileResponse(os.path.join(frontend_dist, "index.html"))

    @app.get("/{full_path:path}")
    async def serve_others(full_path: str):
        file_path = os.path.join(frontend_dist, full_path)
        if os.path.exists(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(frontend_dist, "index.html"))
else:
    print(f"Warning: Frontend dist not found at {frontend_dist}. Running API only.")

if __name__ == "__main__":
    import uvicorn
    # Hugging Face Spaces uses port 7860 by default
    port = int(os.environ.get("PORT", 7860))
    print(f"Starting Raghav's Humanizer at http://0.0.0.0:{port}")
    uvicorn.run(app, host="0.0.0.0", port=port, log_level="info")
