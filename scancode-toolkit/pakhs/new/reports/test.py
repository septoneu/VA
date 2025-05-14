import json
import requests
import math
import re

# ---------------------
# 1) Load vulnerabilities from file
# ---------------------
with open("final_report.json", "r", encoding="utf-8") as f:
    vulnerabilities = json.load(f)

CHUNK_SIZE = 5  # Number of vulnerabilities per chunk
chunks = [
    vulnerabilities[i:i+CHUNK_SIZE]
    for i in range(0, len(vulnerabilities)-308, CHUNK_SIZE)
]
print(vulnerabilities[0])
print(len(vulnerabilities))
# ---------------------
# Global API settings
# ---------------------
API_KEY = "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"  # Replace with your actual OpenRouter key
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

HEADERS = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

def extract_json_array(text):
    """
    Extracts the JSON array from a text string.
    Returns the longest substring starting with '[' and ending with ']',
    or None if no such substring is found.
    """
    # Remove triple backticks and "json" markers
    cleaned_text = text.replace("```json", "").replace("```", "")
    # Find all substrings that start with [ and end with ]
    matches = re.findall(r'\[.*\]', cleaned_text, re.DOTALL)
    if matches:
        candidate = max(matches, key=len).strip()
        if not candidate.endswith("]"):
            print("⚠️ Warning: Extracted JSON does not end with a closing bracket. It may be truncated.")
        return candidate
    return None

def categorize_vulnerabilities(vuln_chunk):
    """
    Sends a chunk of vulnerabilities to DeepSeek LLaMA to categorize them by priority.
    Returns a Python list of dict with keys: ["id", "priority", "reason"].
    """
    # Build a bullet list of vulnerabilities
    bullet_list = "\n".join(
        f"- ID: {v['id']}, Severity: {v['severity']}, CVSS: {v.get('cvss_score', 'N/A')}, Fix version: {v.get('fix_version','N/A')}"
        for v in vuln_chunk
    )

    # Updated system prompt to force pure JSON output
    system_prompt = (
        "You are a cybersecurity AI assistant with deep knowledge of vulnerability assessment. "
        "When provided with vulnerability details, you should analyze the data and decide on the appropriate priority level—'immediate', 'soon', or 'defer'—for fixing each vulnerability. "
        "Do not rely on any pre-specified numerical thresholds; use your own expertise instead. "
        "Return only a JSON array where each object includes exactly these keys: \"id\", \"priority\", and \"reason\"."
    )

    user_message = (
        f"Here is a list of vulnerabilities:\n\n{bullet_list}\n\n"
        "For each vulnerability, analyze the details (such as severity, CVSS score, and fix version) and decide on the correct priority level without any explicit rules from me. "
        "Return your answer as a JSON array in the following format (and nothing else):\n"
        "[\n"
        "  {\"id\": \"<CVE-ID>\", \"priority\": \"immediate/soon/defer\", \"reason\": \"<short explanation>\"},\n"
        "  ...\n"
        "]"
    )

    data_payload = {
        # "model": "deepseek/deepseek-r1-distill-llama-70b:free",
        "model": "deepseek/deepseek-r1:free",
        
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message}
        ],
        "max_tokens": 1500  # Increased from 1000
    }
    
    response = requests.post(OPENROUTER_URL, headers=HEADERS, json=data_payload)
    response_json = response.json()
    
    if "choices" in response_json and response_json["choices"]:
        content = response_json["choices"][0]["message"]["content"]
        # Try to extract the JSON array from the content
        extracted = extract_json_array(content)
        if extracted:
            try:
                results = json.loads(extracted)
                return results
            except json.JSONDecodeError as e:
                print("❌ Failed to parse JSON even after extraction. Extracted content:\n", extracted)
                return []
        else:
            print("❌ No JSON array found in model output:\n", content)
            return []
    else:
        print("❌ Unexpected API response:\n", response_json)
        return []

# ---------------------
# 4) Loop over chunks, send to the model, and collect results
# ---------------------
all_results = []
for i, chunk in enumerate(chunks, 1):
    print(f"Processing chunk {i}/{len(chunks)} with {len(chunk)} vulnerabilities...")
    chunk_results = categorize_vulnerabilities(chunk)
    all_results.extend(chunk_results)

# ---------------------
# 5) Merge results back into full vulnerability data
# ---------------------
# Create a dict for quick look-up
vuln_map = {v["id"]: v for v in vulnerabilities}

for result in all_results:
    cve_id = result.get("id")
    if cve_id in vuln_map:
        vuln_map[cve_id]["priority"] = result.get("priority", "unknown")
        vuln_map[cve_id]["reason"] = result.get("reason", "")

final_list = list(vuln_map.values())

# ---------------------
# 6) Save final output to JSON
# ---------------------
with open("vulnerabilities_prioritized.json", "w", encoding="utf-8") as f:
    json.dump(final_list, f, indent=4)

print("✅ Done! Check 'vulnerabilities_prioritized.json' for your categorized vulnerabilities.")
