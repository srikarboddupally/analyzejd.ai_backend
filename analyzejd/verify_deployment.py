import os
import sys

# Add project root to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

try:
    from dotenv import load_dotenv
    load_dotenv()
    print("✅ Loaded .env file")
except ImportError:
    print("⚠️ python-dotenv not installed, skipping .env load")

import warnings
warnings.filterwarnings("ignore")

print("\n--- Verifying Deployment Setup ---\n")

# 1. Check API Keys
gemini_key = os.getenv("GEMINI_API_KEY")
groq_key = os.getenv("GROQ_API_KEY")

if gemini_key:
    print(f"✅ GEMINI_API_KEY found: {gemini_key[:5]}...")
else:
    print("❌ GEMINI_API_KEY missing!")

if groq_key:
    print(f"✅ GROQ_API_KEY found: {groq_key[:5]}...")
else:
    print("❌ GROQ_API_KEY missing!")


# 2. Check Database Connection Logic
from app.database.connection import DATABASE_URL, engine
print(f"✅ Database Config: {DATABASE_URL}")
try:
    with engine.connect() as conn:
        print("✅ Database connection successful!")
except Exception as e:
    print(f"❌ Database connection failed: {e}")


# 3. Check LLM Router Import
try:
    from app.ai.llm_router import LLMRouter
    print("✅ LLMRouter imported successfully")
except Exception as e:
    print(f"❌ Failed to import LLMRouter: {e}")
    import traceback
    traceback.print_exc()

# 4. Check FastAPI App
try:
    from app.main import app
    print("✅ FastAPI app instance created successfully")
except Exception as e:
    print(f"❌ Failed to create FastAPI app: {e}")
    import traceback
    traceback.print_exc()

print("\n--- Verification Complete ---")
