# Quick test script for AnalyzeJD API
import requests
import json

# Read the Wipro JD
with open("meta_jd.txt", "r") as f:
    jd_text = f.read()

# Call the API
response = requests.post(
    "http://localhost:8000/analyze",
    json={"job_description": jd_text}
)

# Pretty print the result
result = response.json()
output = json.dumps(result, indent=2)
print(output)

# Save to file for full view
with open("test_output.json", "w") as f:
    f.write(output)
print("\n\nFull output saved to test_output.json")
