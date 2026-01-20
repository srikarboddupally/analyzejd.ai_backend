import os

USE_REAL_LLM = os.getenv("USE_REAL_LLM", "false").lower() == "true"
