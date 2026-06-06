from backend.main import app

# Vercel needs an entry point, it usually looks for 'app'
# We need to ensure the imports work correctly when Vercel invokes this
# As an entry point.
app = app
