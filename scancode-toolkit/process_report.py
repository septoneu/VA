import json
import sys

# Load the Dependency-Check report (not actually needed here, just for future reference)
def load_report(report_path):
    print(f"Loading report from {report_path}")
    try:
        with open(report_path, 'r') as file:
            report = json.load(file)
            print("Report loaded successfully.")
            return report
    except FileNotFoundError:
        print(f"Error: File not found at {report_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: Failed to decode JSON in the file: {e}")
        sys.exit(1)

# Problem Version of the function
problem_version = """
def get_remediation_suggestion(cve_id):
    print(f"Fetching remediation details for CVE {cve_id}")
    url = f"https://services.nvd.nist.gov/rest/json/cve/1.0/{cve_id}"
    response = requests.get(url)

    # Debugging: log the response details
    print(f"Response Status Code: {response.status_code}")
    if response.status_code != 200:
        print(f"Error: Failed to fetch data for {cve_id}")
        return "No remediation suggestion available"

    print(f"Response Text: {response.text[:100]}...")  # Print a preview of the response text

    # Try to parse the response as JSON
    try:
        data = response.json()
    except json.JSONDecodeError as e:
        print(f"Error decoding JSON for CVE {cve_id}: {e}")
        return "No remediation suggestion available"

    try:
        # Extract remediation suggestion (example structure)
        suggestion = data['result']['CVE_Items'][0]['impact']['baseMetricV3']['remediation']
    except (KeyError, IndexError):
        suggestion = "No remediation suggestion available"
    
    return suggestion
"""

# Suggested Version of the function (includes API key and retry logic)
suggested_version = """
def get_remediation_suggestion(cve_id):
    print(f"Fetching remediation details for CVE {cve_id}")
    url = f"https://services.nvd.nist.gov/rest/json/cve/1.0/{cve_id}"
    
    headers = {'apiKey': 'YOUR_NVD_API_KEY'}  # Add your NVD API key here
    max_retries = 3
    delay = 2  # Seconds between retries

    for attempt in range(max_retries):
        response = requests.get(url, headers=headers)
        print(f"Response Status Code: {response.status_code}")

        if response.status_code == 200:
            try:
                data = response.json()
                suggestion = data['result']['CVE_Items'][0]['impact']['baseMetricV3']['remediation']
                return suggestion
            except (KeyError, IndexError, json.JSONDecodeError):
                print(f"Error decoding JSON for CVE {cve_id}")
                return "No remediation suggestion available"
        else:
            print(f"Error: Failed to fetch data for {cve_id}, retrying in {delay} seconds...")
            time.sleep(delay)

    return "No remediation suggestion available"
"""

# Save the Problematic and Suggested Version to a file
def save_versions(output_path):
    comparison = {
        "Problem Version": problem_version,
        "Suggested Version": suggested_version
    }

    print(f"Saving problematic and suggested versions to {output_path}")
    try:
        with open(output_path, 'w') as file:
            json.dump(comparison, file, indent=4)
        print("Comparison file saved successfully.")
    except Exception as e:
        print(f"Error saving the comparison file: {e}")
        sys.exit(1)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: process_report.py <output_comparison_file>")
        sys.exit(1)

    output_file = sys.argv[1]
    save_versions(output_file)
