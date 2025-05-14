# Use the latest OWASP Dependency-Check image
FROM owasp/dependency-check:latest

# Set the working directory inside the container
WORKDIR /src

# Copy the necessary files to the container
COPY . /src/sbom_converted.json

# Run Dependency-Check with the specified options
CMD ["--scan", "/src/sbom_converted.json", "--project", "HS4U", "--format", "ALL", "--out", "/src/reports"]
