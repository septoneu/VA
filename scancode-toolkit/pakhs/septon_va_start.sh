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
echo -e "\033[0m"  # Reset color

# Default values
SBOM_FILE=""
REPORTS_DIR="./reports"
LOG_FILE="/tmp/depscan.log"
EXTRA_FLAGS=""

# Help function
usage() {
    echo "Usage: $0 -s <SBOM file> [-r <Reports directory>] [-f <Extra flags>]"
    echo "Options:"
    echo "  -f <SBOM file>         Path to the SBOM file to be analyzed (required)"
    echo "  -r <Reports directory> Directory where reports will be saved (default: ./reports)"
    echo "  -h                     Show this help message"
    exit 1
}

show_spinner() {
    local pid=$1  # Process ID to wait for
    local delay=0.1
    local spin_chars=("|" "/" "-" "\\")  # Spinner animation
    local start_time=$(date +%s)  # Start time for the timer

    echo -n "⏳ Scanning... 00:00 |"

    while kill -0 "$pid" 2>/dev/null; do
        local elapsed=$(( $(date +%s) - start_time ))  # Calculate elapsed time
        local minutes=$(( elapsed / 60 ))
        local seconds=$(( elapsed % 60 ))

        for char in "${spin_chars[@]}"; do
            printf "\r⏳ Scanning... %02d:%02d %s" "$minutes" "$seconds" "$char"
            sleep $delay
        done
    done

    local total_time=$(( $(date +%s) - start_time ))  # Total elapsed time
    local final_minutes=$(( total_time / 60 ))
    local final_seconds=$(( total_time % 60 ))

    printf "\r✅ Scan Completed in %02d:%02d!        \n" "$final_minutes" "$final_seconds"
}


# Parse command-line options
while getopts "f:r:h" opt; do
    case $opt in
        f) SBOM_FILE="$OPTARG" ;;
        r) REPORTS_DIR="$OPTARG" ;;
        h) usage ;;
        *) usage ;;
    esac
done

# Validate required arguments
if [[ -z "$SBOM_FILE" ]]; then
    echo "❌ Error: SBOM file is required."
    usage
fi

# Ensure report directory exists
mkdir -p "$REPORTS_DIR"

# Scanning in the background and capture the process ID
nohup depscan --bom "$SBOM_FILE" --reports-dir "$REPORTS_DIR" > "$LOG_FILE" 2>&1 &
PID=$!

echo "🚀 Scan Started."
echo "📄 Logs: $LOG_FILE"

# Wait for scan to finish
show_spinner $PID

# Print completion message
echo -e "\033[1;32m✅ Dependency Scan Completed!\033[0m"
echo "📁 Reports saved in: $REPORTS_DIR"
echo "🔍 Check logs: $LOG_FILE"
