import os
import sys
import datetime
import requests
from openai import OpenAI

# 1. Read Environment Variables from GitHub Actions
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
REPO = os.getenv("GITHUB_REPOSITORY")  # Automatically provided as "owner/repo" by GitHub

if not GITHUB_TOKEN or not OPENAI_API_KEY or not REPO:
    print("Error: Missing required environment variables (GITHUB_TOKEN, OPENAI_API_KEY, or GITHUB_REPOSITORY).")
    sys.exit(1)

headers = {
    "Authorization": f"Bearer {GITHUB_TOKEN}",
    "Accept": "application/vnd.github+json"
}

# 2. Fetch Closed Issues and Merged PRs from the Past 7 Days
since_date = (datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(days=14)).strftime("%Y-%m-%dT%H:%M:%SZ")
issues_url = f"https://api.github.com/repos/{REPO}/issues?state=closed&since={since_date}"

response = requests.get(issues_url, headers=headers)
if response.status_code != 200:
    print(f"GitHub API Error: {response.status_code} - {response.text}")
    sys.exit(1)

items = response.json()
completed_items = []

for item in items:
    # Identify whether the item is a PR or an Issue
    item_type = "PR" if "pull_request" in item else "Issue"
    completed_items.append(f"- [{item_type} #{item['number']}] {item['title']} (by @{item['user']['login']})")

activity_text = "\n".join(completed_items) if completed_items else "No closed issues or merged PRs found in the past 7 days."

# 3. Generate Summary Using OpenAI API
try:
    client = OpenAI(api_key=OPENAI_API_KEY)
    
    prompt = f"""
You are an engineering project manager overseeing a quadrotor engineering repository. 

Below is a list of GitHub issues and pull requests completed in the past 7 days:

{activity_text}

Please generate a concise, executive-level weekly summary with the following structure:
1. **Key Accomplishments** (Categorized by subsystem or topic)
2. **Impact & Sprint Progress** (Brief summary of project momentum)
3. **Contributors Highlight** (Acknowledge team contributions)
"""

    completion = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[{"role": "user", "content": prompt}]
    )
    summary_md = completion.choices[0].message.content

except Exception as e:
    print(f"OpenAI API Error: {e}")
    sys.exit(1)

# 4. Post Summary as a New GitHub Issue
post_url = f"https://api.github.com/repos/{REPO}/issues"
issue_payload = {
    "title": f"Weekly Engineering Summary ({datetime.date.today()})",
    "body": summary_md,
    "labels": ["documentation"]
}

post_response = requests.post(post_url, headers=headers, json=issue_payload)
if post_response.status_code == 201:
    print("Weekly summary issue created successfully!")
else:
    print(f"Failed to create issue: {post_response.status_code} - {post_response.text}")
    sys.exit(1)
