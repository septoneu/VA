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
    local start_time=$(date +%s)

    echo -n "⏳ Processing... 00:00 |"

    while kill -0 "$pid" 2>/dev/null; do
        local elapsed=$(( $(date +%s) - start_time ))
        local minutes=$(( elapsed / 60 ))
        local seconds=$(( elapsed % 60 ))

        for char in "${spin_chars[@]}"; do
            printf "\r⏳ Processing... %02d:%02d %s" "$minutes" "$seconds" "$char"
            sleep $delay
        done
    done

    local total_time=$(( $(date +%s) - start_time ))
    local final_minutes=$(( total_time / 60 ))
    local final_seconds=$(( total_time % 60 ))

    printf "\r✅ Completed in %02d:%02d!        \n" "$final_minutes" "$final_seconds"
}

###############################################################################
# Help / Usage
###############################################################################
usage() {
    echo "Usage:"
    echo "  $0 scancode -d <directory> [options]"
    echo "  $0 dependencycheck -s <sbom.json> [options]"
    echo
    echo "Subcommands:"
    echo "  scancode          1) Use ScanCode Toolkit to scan a directory"
    echo "                    2) Convert results to CycloneDX SBOM (JSON)"
    echo
    echo "  dependencycheck   Run OWASP depedency check on an existing SBOM (JSON)"
    echo
    echo "Options for 'scancode' subcommand:"
    echo "  -d <directory>      Directory to scan (required)"
    echo "  -o <output.json>    Path for the ScanCode JSON results (default: scancode-results.json)"
    echo "  -b <sbom.json>      Path for the final CycloneDX SBOM (default: scancode-sbom.json)"
    echo "  -r <reports_dir>    Directory to store output files (default: ./reports)"
    echo "  -S <flags>          Extra flags for ScanCode Toolkit (e.g., -clipeu --timeout 600, etc.)"
    echo "  -C <flags>          Extra flags for cyclonedx-py (e.g., --exclude tests)"
    echo
    echo "Options for 'dependencycheck' subcommand:"
    echo "  -s <sbom.json>      Existing CycloneDX SBOM to scan (required)"
    echo "  -r <reports_dir>    Directory to store dep-scan results (default: ./reports)"
    echo "  -D <flags>          Extra flags for dep-scan (e.g., --profile appsec --deep)"
    echo
    echo "All logs are written to /tmp/scanner.log"
    echo
    exit 1
}

###############################################################################
# Main Script
###############################################################################
if [[ $# -lt 1 ]]; then
    usage
fi

SUBCOMMAND="$1"
shift

# Defaults
DIRECTORY=""
SCANCODE_JSON="scancode-results.json"
SBOM_FILE="scancode-sbom.json"
REPORTS_DIR="./reports"
SCANCODE_FLAGS="-clipeu --json-pp"
CYCLONEDX_FLAGS="--format json -e"
DEPSCAN_FLAGS=""
LOG_FILE="/tmp/scanner.log"

case "$SUBCOMMAND" in
  ###########################################################################
  # Subcommand: scancode
  ###########################################################################
  scancode)
    while getopts "d:o:b:r:S:C:h" opt; do
      case $opt in
        d) DIRECTORY="$OPTARG" ;;
        o) SCANCODE_JSON="$OPTARG" ;;
        b) SBOM_FILE="$OPTARG" ;;
        r) REPORTS_DIR="$OPTARG" ;;
        S) SCANCODE_FLAGS="$OPTARG" ;;
        C) CYCLONEDX_FLAGS="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
      esac
    done

    # Validate directory
    if [[ -z "$DIRECTORY" ]]; then
      echo "❌ Error: -d <directory> is required for 'scancode'."
      usage
    fi

    # Ensure reports directory exists
    mkdir -p "$REPORTS_DIR"

    # Build final paths
    SCANCODE_JSON="$REPORTS_DIR/$SCANCODE_JSON"
    SBOM_FILE="$REPORTS_DIR/$SBOM_FILE"

    echo "🚀 [scancode] Scanning directory: $DIRECTORY"
    echo "🔧 ScanCode flags: $SCANCODE_FLAGS"
    echo "📄 Saving scan results to: $SCANCODE_JSON"
    echo "📁 Reports dir: $REPORTS_DIR"
    echo "📝 Log file: $LOG_FILE"

    # 1. Run scancode-toolkit in background
    nohup scancode $SCANCODE_FLAGS "$DIRECTORY" "$SCANCODE_JSON" > "$LOG_FILE" 2>&1 &
    PID=$!
    show_spinner $PID

    # 2. Convert to CycloneDX SBOM
    echo "🚀 Converting to CycloneDX SBOM (JSON)..."
    echo "🔧 cyclonedx-py flags: $CYCLONEDX_FLAGS"
    nohup cyclonedx-py $CYCLONEDX_FLAGS -i "$SCANCODE_JSON" -o "$SBOM_FILE" >> "$LOG_FILE" 2>&1 &
    PID=$!
    show_spinner $PID

    echo "✅ Done!"
    echo "   ScanCode JSON:    $SCANCODE_JSON"
    echo "   CycloneDX SBOM:   $SBOM_FILE"
    echo "🔍 Check logs:       $LOG_FILE"
    ;;

  ###########################################################################
  # Subcommand: dependencycheck
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

    # Ensure reports directory exists
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
    ;;
    
  ###########################################################################
  # Invalid Subcommand
  ###########################################################################
  *)
    echo "❌ Error: Invalid subcommand '$SUBCOMMAND'."
    usage
    ;;
esac
