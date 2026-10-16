# GenAI-Powered Dockerfile Generator

A Python-based DevOps automation tool that uses Google's
Gemini API to generate Dockerfiles and automatically
validate them using Hadolint.

## Features

### V1 - Dockerfile Generation
- Generate Dockerfiles using Google Gemini API
- Supports Python, Java, Node.js, and Go
- Structured prompts following DevOps best practices
- Multi-stage builds where appropriate
- Non-root container execution
- Automatic Dockerfile saving

### V2 - Reliability and Validation
- Automatic Hadolint validation
- Gemini API retry handling with exponential backoff
- Detection of Dockerfile linting issues
- JSON validation reports
- Error handling for temporary API failures

## Tech Stack

- Python
- Google Gemini API
- Docker
- Hadolint
- Git and GitHub

## How It Works

1. User selects a programming language.
2. Python sends a structured prompt to Gemini.
3. Gemini generates a Dockerfile.
4. Python saves the generated Dockerfile.
5. Hadolint automatically validates the Dockerfile.
6. A JSON validation report is saved.

## Installation

Requirements:
- Python 3.10+
- Hadolint installed and available in PATH
- Google Gemini API key

Create a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Configure your API key:

```bash
export GEMINI_API_KEY="your_api_key"
export GEMINI_MODEL="gemini-3.8-flash"
```

The model ID must be supported by your Gemini API account.

## Run

```bash
python3 dockerfile_generator_v2.py
```

Select a programming language from the menu.

## Output

The application saves:

- `generated/<language>/Dockerfile`
- `generated/<language>/validation_report.json`

## Real Testing Results

During Java Dockerfile generation:

- Gemini API returned HTTP 503 twice.
- Automatic retry recovered on the third attempt.
- Hadolint detected one informational finding:
  DL3066 - Non-numeric user ID.
- The finding was saved in a JSON report.

See `examples/java/` for sample output.

## Current Limitations

- Generated Dockerfiles are not automatically built.
- Hadolint findings are not automatically fixed.
- Generated files require review before production use.

## Planned V3

- AI-powered Dockerfile error correction
- Automatic revalidation
- Controlled correction loop
- Before-and-after validation reports

## Author

Suraj Lavhale

DevOps Engineer | AWS | Kubernetes | GenAI
