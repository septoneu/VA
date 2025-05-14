import requests

# Manufacturer API URL and credentials
SBOM_URL = "http://localhost:5000/api/v1/sbom"
API_KEY = "abc12345-secure-key"  # Dummy API Key

def fetch_sbom():
    # Prompt the user to input the TOTP code
    totp_code = input("Enter the TOTP code from your authenticator app: ")

    headers = {
        "Authorization": f"ApiKey {API_KEY}",
        "X-TOTP-Code": totp_code
    }
    response = requests.get(SBOM_URL, headers=headers)

    # Check if the request was successful
    if response.status_code == 200:
        with open("downloaded_sbom_converted.json", "wb") as file:
            file.write(response.content)
        print("Successfully retrieved and saved SBOM.")
    elif response.status_code == 401:
        print("Unauthorized access. Check your API key and TOTP code.")
    else:
        print("Error:", response.json().get("error"))

if __name__ == "__main__":
    fetch_sbom()
