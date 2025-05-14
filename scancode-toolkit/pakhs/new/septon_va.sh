#!/bin/bash

# ASCII Logo
echo -e "\033[1;34m"
cat << "EOF"
    /$$$$$$  /$$$$$$$$ /$$$$$$$  /$$$$$$$$  /$$$$$$  /$$   /$$       /$$    /$$  /$$$$$$        /$$$$$$$$  /$$$$$$   /$$$$$$  /$$      
   /$$__  $$| $$_____/| $$__  $$|__  $$__/ /$$__  $$| $$$ | $$      | $$   | $$ /$$__  $$      |__  $$__/ /$$__  $$ /$$__  $$| $$      
  | $$  \__/| $$      | $$  \ $$   | $$   | $$  \ $$| $$$$| $$      | $$   | $$| $$  \ $$         | $$   | $$  \ $$| $$  \ $$| $$      
  |  $$$$$$ | $$$$$   | $$$$$$$/   | $$   | $$  | $$| $$ $$ $$      |  $$ / $$/| $$$$$$$$         | $$   | $$  | $$| $$  | $$| $$      
   \____  $$| $$__/   | $$____/    | $$   | $$  | $$| $$  $$$$       \  $$ $$/ | $$__  $$         | $$   | $$  | $$| $$  | $$| $$      
   /$$  \ $$| $$      | $$         | $$   | $$  | $$| $$\  $$$        \  $$$/  | $$  | $$         | $$   | $$  | $$| $$  | $$| $$      
  |  $$$$$$/| $$$$$$$$| $$         | $$   |  $$$$$$/| $$ \  $$         \  $/   | $$  | $$         | $$   |  $$$$$$/|  $$$$$$/| $$$$$$$$
   \______/ |________/|__/         |__/    \______/ |__/  \__/          \_/    |__/  |__/         |__/    \______/  \______/ |________/
                                                                                                                                      
                                                                                                                                      
                                                                                                                                      
EOF
echo -e "\033[0m"

###############################################################################
# Spinner Function (with Timer)
###############################################################################
show_spinner() {
    local pid=$1
    local delay=0.1
    local spin_chars=("|" "/" "-" "\\")
    local start_time
    start_time=$(date +%s)

    echo -n "⏳ Processing... 00:00 |"

    while kill -0 "$pid" 2>/dev/null; do
        local elapsed=$(( $(date +%s) - start_time ))
        local minutes=$(( elapsed / 60 ))
        local seconds=$(( elapsed % 60 ))

        for char in "${spin_chars[@]}"; do
            printf "\r⏳ Processing... %02d:%02d %s" "$minutes" "$seconds" "$char"
            sleep "$delay"
        done
    done

    local total_time=$(( $(date +%s) - start_time ))
    local final_minutes=$(( total_time / 60 ))
    local final_seconds=$(( total_time % 60 ))

    printf "\r✅ Completed in %02d:%02d!        \n" "$final_minutes" "$final_seconds"
}

###############################################################################
# Usage / Help
###############################################################################
usage() {
    echo "Usage:"
    echo "  $0 scancode -d <directory> [options]"
    echo "  $0 cyclonedx -i <input.json> [options]"
    echo "  $0 dependencycheck -s <sbom.json> [options]"
    echo
    echo "Subcommands:"
    echo "  scancode          Use ScanCode Toolkit to scan a directory (produces a JSON file)."
    echo
    echo "  cyclonedx         Convert an existing JSON file (e.g., from scancode) to CycloneDX SBOM."
    echo
    echo "  dependencycheck   Run OWASP dep-scan on an existing CycloneDX SBOM."
    echo
    echo "Options for 'scancode' subcommand:"
    echo "  -d <directory>     Directory to scan (required)"
    echo "  -o <output.json>   Path/filename for the ScanCode JSON results (default: scancode-results.json)"
    echo "  -r <reports_dir>   Directory to store output files (default: ./reports)"
    echo "  -S <flags>         Extra flags for ScanCode Toolkit (e.g., \"-clipeu --timeout 600\")"
    echo
    echo "Options for 'cyclonedx' subcommand:"
    echo "  -i <input.json>    Input JSON file (e.g., from scancode) to convert (required)"
    echo "  -o <sbom.json>     Output CycloneDX SBOM (default: cyclonedx-sbom.json)"
    echo "  -r <reports_dir>   Directory to store output files (default: ./reports)"
    echo "  -X <flags>         Extra flags for cyclonedx-py (e.g., \"--format json -e\")"
    echo
    echo "Options for 'dependencycheck' subcommand:"
    echo "  -s <sbom.json>     Existing CycloneDX SBOM to scan (required)"
    echo "  -r <reports_dir>   Directory to store dep-scan results (default: ./reports)"
    echo "  -D <flags>         Extra flags for dep-scan (e.g., \"--profile appsec --deep\")"
    echo
    echo "All logs are written to /tmp/scanner.log"
    echo
    exit 1
}

###############################################################################
# Ensure a Subcommand is Provided
###############################################################################
if [[ $# -lt 1 ]]; then
    usage
fi

SUBCOMMAND="$1"
shift  # Remove the subcommand from the args list

###############################################################################
# Default Values
###############################################################################
DIRECTORY=""
SCANCODE_JSON="scancode-results.json"
INPUT_JSON=""
CYCLONE_OUTPUT="cyclonedx-sbom.json"
SBOM_FILE=""
REPORTS_DIR="./reports"
SCANCODE_FLAGS="-clipeu --json-pp"
CYCLONEDX_FLAGS="--format json -e"
DEPSCAN_FLAGS=""
LOG_FILE="/tmp/scanner.log"

###############################################################################
# Handle Subcommands
###############################################################################
case "$SUBCOMMAND" in

 ###############################################################################
# 1) Subcommand: scancode
###############################################################################
scancode)
  # Parse scancode-specific options
  while getopts "d:o:r:S:h" opt; do
    case $opt in
      d) DIRECTORY="$OPTARG" ;;
      o) SCANCODE_JSON="$OPTARG" ;;
      r) REPORTS_DIR="$OPTARG" ;;
      S) SCANCODE_FLAGS="$OPTARG" ;;
      h) usage ;;
      *) usage ;;
    esac
  done

  # Validate directory
  if [[ -z "$DIRECTORY" ]]; then
    echo "❌ Error: -d <directory> is required for 'scancode'."
    usage
  fi

  # Create reports directory if it doesn't exist
  mkdir -p "$REPORTS_DIR"

  # Build the full path for the ScanCode JSON output
  SCANCODE_JSON="$REPORTS_DIR/$SCANCODE_JSON"

  echo "🚀 [scancode] Scanning directory: $DIRECTORY"
  echo "🔧 ScanCode flags: $SCANCODE_FLAGS"
  echo "📄 ScanCode JSON (output) will be created at: $SCANCODE_JSON"
  echo "📁 Reports directory: $REPORTS_DIR"
  echo "📝 Log file: $LOG_FILE"

  echo "  nohup scancode $SCANCODE_FLAGS "$SCANCODE_JSON" "$DIRECTORY" \
    > "$LOG_FILE" 2>&1 &" 
    
  nohup scancode $SCANCODE_FLAGS "$SCANCODE_JSON" "$DIRECTORY" \
    > "$LOG_FILE" 2>&1 &
  PID=$!
  show_spinner $PID

  echo "✅ ScanCode Completed!"
  echo "   Scan results:  $SCANCODE_JSON"
  echo "🔍 Logs:          $LOG_FILE"
  ;;
  ###########################################################################
  # 2) Subcommand: cyclonedx
  ###########################################################################
  cyclonedx)
    # Parse cyclonedx-specific options
    while getopts "i:o:r:X:h" opt; do
      case $opt in
        i) INPUT_JSON="$OPTARG" ;;
        o) CYCLONE_OUTPUT="$OPTARG" ;;
        r) REPORTS_DIR="$OPTARG" ;;
        X) CYCLONEDX_FLAGS="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
      esac
    done

    # Validate input JSON
    if [[ -z "$INPUT_JSON" ]]; then
      echo "❌ Error: -i <input.json> is required for 'cyclonedx'."
      usage
    fi

    mkdir -p "$REPORTS_DIR"

    # Build full path for the CycloneDX output
    CYCLONE_OUTPUT="$REPORTS_DIR/$CYCLONE_OUTPUT"

    echo "🚀 [cyclonedx] Converting: $INPUT_JSON"
    echo "🔧 cyclonedx-py flags: $CYCLONEDX_FLAGS"
    echo "📄 Output SBOM: $CYCLONE_OUTPUT"
    echo "📁 Reports dir: $REPORTS_DIR"
    echo "📝 Log file:    $LOG_FILE"

    # Convert using cyclonedx-py
    nohup cyclonedx-py $CYCLONEDX_FLAGS \
      -i "$INPUT_JSON" \
      -o "$CYCLONE_OUTPUT" \
      > "$LOG_FILE" 2>&1 &
    PID=$!
    show_spinner $PID

    echo "✅ CycloneDX Conversion Completed!"
    echo "   CycloneDX SBOM: $CYCLONE_OUTPUT"
    echo "🔍 Logs:           $LOG_FILE"
    ;;

  ###########################################################################
  # 3) Subcommand: dependencycheck
  ###########################################################################
  dependencycheck)
    while getopts "s:r:D:h" opt; do
      case $opt in
        s) SBOM_FILE="$OPTARG" ;;
        r) REPORTS_DIR="$OPTARG" ;;
        D) DEPSCAN_FLAGS="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
      esac
    done

    # Validate SBOM file
    if [[ -z "$SBOM_FILE" ]]; then
      echo "❌ Error: -s <sbom.json> is required for 'dependencycheck'."
      usage
    fi

    mkdir -p "$REPORTS_DIR"

    echo "🚀 [dependencycheck] Running dep-scan on: $SBOM_FILE"
    echo "🔧 dep-scan flags: $DEPSCAN_FLAGS"
    echo "📁 Reports dir:    $REPORTS_DIR"
    echo "📝 Log file:       $LOG_FILE"

    nohup depscan --bom "$SBOM_FILE" --reports-dir "$REPORTS_DIR" $DEPSCAN_FLAGS \
      > "$LOG_FILE" 2>&1 &
    PID=$!
    show_spinner $PID

    echo "✅ DepScan Completed!"
    echo "📁 Reports saved in: $REPORTS_DIR"
    echo "🔍 Logs: $LOG_FILE"
    


   ###########################################################################
   # Now ask user if they'd like to serve the final report via an HTML GUI
   ###########################################################################
   read -rp "Do you want to serve the report? (y/n): " answer
   if [[ "$answer" == "y" ]]; then
     # We assume 'depscan-bom.json' is created in $REPORTS_DIR by dep-scan
     DEPSCAN_BOM_JSON="$REPORTS_DIR/depscan-bom.json"
     if [[ ! -f "$DEPSCAN_BOM_JSON" ]]; then
       echo "❌ Error: '$DEPSCAN_BOM_JSON' not found. Cannot generate final report."
       exit 1
     fi

     echo "🔄 Creating final_report.json from depscan-bom.json..."
     # 1) Generate fix_json.py in the reports directory
     cat << 'EOF' > "$REPORTS_DIR/fix_json.py"
#!/usr/bin/env python3
import json

with open("depscan-bom.json", "r", encoding="utf-8") as file:
    raw_data = file.read().strip()

json_objects = raw_data.split("\n")
parsed_json = [json.loads(obj) for obj in json_objects]

with open("final_report.json", "w", encoding="utf-8") as output_file:
    json.dump(parsed_json, output_file, indent=4)

print("✅ JSON fixed! Saved as 'final_report.json'")
EOF

     # 2) Make the Python script executable and run it from inside $REPORTS_DIR
     chmod +x "$REPORTS_DIR/fix_json.py"
     pushd "$REPORTS_DIR" > /dev/null
       nohup ./fix_json.py > /tmp/scanner_fixjson.log 2>&1 &
       PID2=$!
       show_spinner $PID2
     popd > /dev/null

     echo "✅ final_report.json created inside $REPORTS_DIR."

     echo "🔄 Creating index.html in $REPORTS_DIR..."
     # 3) Create index.html in the same $REPORTS_DIR
     cat << 'EOF' > "$REPORTS_DIR/index.html"
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>SEPTON Vulnerability Assessment</title>
  <style>
    /* Basic reset and body styling */
    * {
      margin: 0;
      padding: 0;
      box-sizing: border-box;
    }
    body {
      font-family: Arial, sans-serif;
      background: #e4f5ec; /* Light green background */
      color: #333;
      padding: 20px;
    }
    header {
      text-align: center;
      margin-bottom: 25px;
    }
    header h1 {
      font-size: 2em;
      color: rgb(0, 128, 96);
      text-transform: uppercase;
      letter-spacing: 1px;
    }
    .container {
      max-width: 1200px;
      margin: 0 auto;
    }
    .vuln-row {
      background: #fff;
      margin-bottom: 10px;
      padding: 15px;
      border-radius: 6px;
      box-shadow: 0 1px 3px rgba(0, 0, 0, 0.1);
      position: relative;
    }
    .vuln-summary {
      display: flex;
      align-items: center;
      justify-content: space-between;
      margin-bottom: 5px;
    }
    .vuln-name {
      font-weight: bold;
      font-size: 1rem;
      color: #23764e;
    }
    .severity-button {
      cursor: pointer;
      border: none;
      padding: 6px 12px;
      font-size: 0.9rem;
      font-weight: 600;
      border-radius: 4px;
      color: #fff;
    }
    .severity-critical { background: #c9302c; }
    .severity-high     { background: #f0ad4e; }
    .severity-medium   { background: #e5c600; color: #000; }
    .severity-low      { background: #5cb85c; }
    .details {
      margin-top: 10px;
      display: none;
      border-top: 1px solid #ddd;
      padding-top: 10px;
    }
    .vuln-meta {
      margin: 8px 0;
      line-height: 1.5;
    }
    .related-urls {
      margin-top: 8px;
      list-style-type: disc;
      padding-left: 20px;
    }
    .related-urls li a {
      color: #23764e;
      text-decoration: none;
    }
    .related-urls li a:hover {
      text-decoration: underline;
    }
    /* Updated styles for the LLM answer box */
    .llm-answer {
      margin-top: 10px;
      padding: 15px;
      background: linear-gradient(135deg, #f0f9f4, #e4f5ec);
      border: 2px solid #23764e;
      border-radius: 8px;
      box-shadow: 0 2px 4px rgba(35, 118, 78, 0.2);
      font-size: 0.95rem;
      color: #333;
      transition: transform 0.2s ease, box-shadow 0.2s ease;
    }
    .llm-answer:hover {
      transform: translateY(-2px);
      box-shadow: 0 4px 8px rgba(35, 118, 78, 0.3);
    }
    .ask-button {
      margin-top: 10px;
      padding: 6px 12px;
      font-size: 0.9rem;
      border: none;
      border-radius: 4px;
      background: #23764e;
      color: #fff;
      cursor: pointer;
    }
    /* Modal Styles */
    .modal-overlay {
      position: fixed;
      top: 0;
      left: 0;
      right: 0;
      bottom: 0;
      background: rgba(35, 118, 78, 0.5); /* Semi-transparent using primary color */
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
    }
    .modal {
      background: #fff;
      border-radius: 8px;
      padding: 20px;
      max-width: 500px;
      width: 90%;
      box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
    }
    .modal-header {
      font-size: 1.2rem;
      color: #23764e;
      margin-bottom: 10px;
    }
    .modal textarea {
      width: 100%;
      height: 80px;
      margin-bottom: 10px;
      padding: 10px;
      border: 1px solid #23764e;
      border-radius: 4px;
      font-size: 1rem;
    }
    .modal button {
      padding: 8px 16px;
      border: none;
      border-radius: 4px;
      cursor: pointer;
      font-size: 1rem;
      background: #23764e;
      color: #fff;
    }
    .modal .cancel-btn {
      background: #c9302c;
      margin-left: 10px;
    }
  </style>
</head>
<body>
  <header>
    <img src="https://septon-project.eu/wp-content/uploads/2023/02/septon-logo-EMC.png" alt="SEPTON Logo" style="max-width:150px; display:block; margin: 0 auto 10px auto;">
    <h1>Vulnerability Assessment Report</h1>
  </header>

  <div class="container" id="vulnerabilitiesContainer"></div>

  <script>
    // Map severity to CSS class
    function getSeverityClass(severity) {
      const sev = severity ? severity.toUpperCase() : "";
      switch (sev) {
        case "CRITICAL": return "severity-critical";
        case "HIGH":     return "severity-high";
        case "MEDIUM":   return "severity-medium";
        case "LOW":      return "severity-low";
        default:         return "";
      }
    }

    // Toggle details section
    function toggleDetails(detailsId) {
      const details = document.getElementById(detailsId);
      details.style.display = (!details.style.display || details.style.display === "none") ? "block" : "none";
    }

    // Create and open a modal for user question input
    function openQuestionModal(vuln) {
      return new Promise((resolve, reject) => {
        const overlay = document.createElement("div");
        overlay.className = "modal-overlay";
        
        const modal = document.createElement("div");
        modal.className = "modal";
        
        const header = document.createElement("div");
        header.className = "modal-header";
        header.textContent = "Ask about " + vuln.id;
        modal.appendChild(header);
        
        const textarea = document.createElement("textarea");
        textarea.placeholder = "Enter your question here...";
        modal.appendChild(textarea);
        
        const btnContainer = document.createElement("div");
        
        const submitBtn = document.createElement("button");
        submitBtn.textContent = "Submit";
        btnContainer.appendChild(submitBtn);
        
        const cancelBtn = document.createElement("button");
        cancelBtn.textContent = "Cancel";
        cancelBtn.className = "cancel-btn";
        btnContainer.appendChild(cancelBtn);
        
        modal.appendChild(btnContainer);
        overlay.appendChild(modal);
        document.body.appendChild(overlay);
        
        submitBtn.onclick = () => {
          const question = textarea.value.trim();
          document.body.removeChild(overlay);
          resolve(question);
        };
        cancelBtn.onclick = () => {
          document.body.removeChild(overlay);
          resolve(null);
        };
      });
    }

    // Function to ask LLM for details on a vulnerability using the modal
    async function askLLMForVuln(vuln, answerContainer) {
      const question = await openQuestionModal(vuln);
      if (!question) {
        answerContainer.textContent = "Question canceled.";
        return;
      }
      
      const systemPrompt = "You are a cybersecurity AI assistant. When answering, provide only the final, concise answer without any internal chain-of-thought or reasoning steps. Do not include any explanation of how you arrived at your answer.";
      const userPrompt = `Vulnerability Details:
ID: ${vuln.id}
Package: ${vuln.package}
Severity: ${vuln.severity}
CVSS: ${vuln.cvss_score}
Description: ${vuln.short_description}

Question: ${question}`;

      // NOTE: Exposing your API key client-side is not secure. In production, proxy this via your backend.
      const API_KEY = "";
      const OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions";
      const payload = {
        model: "deepseek/deepseek-r1:free",
        messages: [
          {role: "system", content: systemPrompt},
          {role: "user", content: userPrompt}
        ],
        max_tokens: 500
      };

      answerContainer.innerHTML = "<em>Loading answer...</em>";

      try {
        const response = await fetch(OPENROUTER_URL, {
          method: "POST",
          headers: {
            "Authorization": `Bearer ${API_KEY}`,
            "Content-Type": "application/json"
          },
          body: JSON.stringify(payload)
        });
        const json = await response.json();
        if (json.choices && json.choices.length > 0) {
          const answer = json.choices[0].message.content;
          answerContainer.textContent = answer;
        } else {
          answerContainer.textContent = "No answer received.";
        }
      } catch (err) {
        console.error("Error asking LLM:", err);
        answerContainer.textContent = "Error: " + err;
      }
    }

    // Fetch vulnerabilities from JSON file and build the page
    fetch("final_report.json")
      .then(response => response.json())
      .then(data => {
        const container = document.getElementById("vulnerabilitiesContainer");
        data.forEach((vuln, index) => {
          const row = document.createElement("div");
          row.classList.add("vuln-row");

          const summary = document.createElement("div");
          summary.classList.add("vuln-summary");

          const nameSpan = document.createElement("span");
          nameSpan.classList.add("vuln-name");
          nameSpan.textContent = `${vuln.id} - ${vuln.package}`;

          const severityButton = document.createElement("button");
          severityButton.textContent = vuln.severity ? vuln.severity.toUpperCase() : "UNKNOWN";
          severityButton.classList.add("severity-button", getSeverityClass(vuln.severity));

          const detailsId = `details-${index}`;
          severityButton.onclick = () => toggleDetails(detailsId);

          summary.appendChild(nameSpan);
          summary.appendChild(severityButton);

          const detailsDiv = document.createElement("div");
          detailsDiv.classList.add("details");
          detailsDiv.id = detailsId;

          const cvss = document.createElement("div");
          cvss.classList.add("vuln-meta");
          cvss.innerHTML = `<strong>CVSS Score:</strong> ${vuln.cvss_score || "N/A"}`;

          const versions = document.createElement("div");
          versions.classList.add("vuln-meta");
          versions.innerHTML = `
            <strong>Version:</strong> ${vuln.version || "N/A"}<br />
            <strong>Fix Version:</strong> ${vuln.fix_version || "N/A"}
          `;

          const desc = document.createElement("div");
          desc.classList.add("vuln-meta");
          desc.innerHTML = `<strong>Description:</strong> ${vuln.short_description || "No description"}`;

          let urlsSection = null;
          if (vuln.related_urls && vuln.related_urls.length > 0) {
            urlsSection = document.createElement("div");
            urlsSection.classList.add("vuln-meta");
            urlsSection.innerHTML = `<strong>Related URLs:</strong>`;
            const urlsList = document.createElement("ul");
            urlsList.classList.add("related-urls");
            vuln.related_urls.forEach(url => {
              const li = document.createElement("li");
              const link = document.createElement("a");
              link.href = url;
              link.target = "_blank";
              link.rel = "noopener noreferrer";
              link.textContent = url;
              li.appendChild(link);
              urlsList.appendChild(li);
            });
            urlsSection.appendChild(urlsList);
          }

          detailsDiv.appendChild(cvss);
          detailsDiv.appendChild(versions);
          detailsDiv.appendChild(desc);
          if (urlsSection) detailsDiv.appendChild(urlsSection);

          // Create Ask LLM button and answer container
          const askButton = document.createElement("button");
          askButton.classList.add("ask-button");
          askButton.textContent = "Ask LLM about this vulnerability";
          const answerContainer = document.createElement("div");
          answerContainer.classList.add("llm-answer");
          detailsDiv.appendChild(askButton);
          detailsDiv.appendChild(answerContainer);

          askButton.onclick = () => {
            askLLMForVuln(vuln, answerContainer);
          };

          row.appendChild(summary);
          row.appendChild(detailsDiv);
          container.appendChild(row);
        });
      })
      .catch(err => {
        console.error("Error fetching vulnerabilities:", err);
      });
  </script>
</body>
</html>


EOF

     echo "✅ Created 'index.html' in $REPORTS_DIR."

     echo
     echo "🚀 Starting a simple HTTP server on port 8000 from directory: $REPORTS_DIR"
     echo "Press Ctrl+C to stop the server."
     echo "Open this link in your browser:"
     echo "  http://main.infili.com:8000/index.html"
     echo

     # 4) Now cd into reports dir & serve the files
     pushd "$REPORTS_DIR" > /dev/null
       python3 -m http.server --bind 0.0.0.0 8000
     popd > /dev/null
   else
     echo "Not serving the report. Exiting."
   fi
   ;;

  ###########################################################################
  # Invalid Subcommand
  ###########################################################################
  *)
    echo "❌ Error: Invalid subcommand '$SUBCOMMAND'."
    usage
    ;;
esac
