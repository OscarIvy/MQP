import os
import sys
import datetime
import requests
from google import genai

# 1. Read Environment Variables
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO = os.getenv("GITHUB_REPOSITORY")

if not GITHUB_TOKEN or not GEMINI_API_KEY or not REPO:
    print("Error: Missing required environment variables (GITHUB_TOKEN, GEMINI_API_KEY, or GITHUB_REPOSITORY).")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 2. Fetch Closed Issues and Merged PRs from the Past 14 Days
since_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
issues_url = f"https://api.github.com/repos/{REPO}/issues?state=closed&since={since_date}"

response = requests.get(issues_url, headers=headers)
if response.status_code != 200:
    print(f"GitHub API Error: {response.status_code} - {response.text}")
    sys.exit(1)

items = response.json()
completed_items = []

for item in items:
    item_type = "PR" if "pull_request" in item else "Issue"
    completed_items.append(f"- [{item_type} #{item['number']}] {item['title']} (by @{item['user']['login']})")

activity_text = "\n".join(completed_items) if completed_items else "No closed issues or merged PRs found in the past 14 days."

# 3. Generate Summary Using Gemini API (Free Tier)
# 3. Generate Summary Using Gemini API (Free Tier)
from google.genai import types

# 3. Generate Summary Using Gemini API (Free Tier)
try:
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    prompt = f"""
You are an engineering project manager overseeing a quadrotor engineering repository. 

Below is a list of GitHub issues and pull requests completed in the past 14 days:

{activity_text}

Please generate a concise, executive-level bi-weekly summary with the following structure:
1. **Key Accomplishments** (Categorized by subsystem or topic)
2. **Impact & Sprint Progress** (Brief summary of project momentum over the two-week cycle)
3. **Contributors Highlight** (Acknowledge team contributions)
"""

    response = client.models.generate_content(
        model="gemini-2.0-flash",
        contents=prompt,
        config=types.GenerateContentConfig(
            temperature=0.2,
        )
    )
    summary_md = response.text

except Exception as e:
    print(f"Gemini API Error: {e}")
    sys.exit(1)
