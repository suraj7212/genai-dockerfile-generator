
#!/usr/bin/env python3

import json
import os
import random
import shutil
import subprocess
import sys
import time

from datetime import datetime, timezone
from pathlib import Path

from google import genai
from google.genai import errors


# ==========================================
# CONFIGURATION
# ==========================================

SUPPORTED_LANGUAGES = {
    "1": "python",
    "2": "java",
    "3": "nodejs",
    "4": "go"
}

MODEL = os.getenv("GEMINI_MODEL", "gemini-3.8-flash")

OUTPUT_ROOT = Path("generated")

MAX_RETRIES = 3
BASE_DELAY = 2


# ==========================================
# DOCKERFILE GENERATION PROMPT
# ==========================================

PROMPT = """
Generate a Dockerfile for a {language} application.

Requirements:
- Use an appropriate official base image
- Use multi-stage builds where useful
- Optimize dependency caching
- Set a working directory
- Copy application source code
- Run as a non-root user
- Use an appropriate CMD or ENTRYPOINT
- Follow Docker security best practices

Return only valid Dockerfile instructions.
Do not include Markdown code fences or explanations.
"""


# ==========================================
# GEMINI API WITH RETRY HANDLING
# ==========================================

def generate_dockerfile(client, language):

    for attempt in range(MAX_RETRIES + 1):

        try:
            print(
                f"\nCalling Gemini API "
                f"(Attempt {attempt + 1}/{MAX_RETRIES + 1})..."
            )

            response = client.models.generate_content(
                model=MODEL,
                contents=PROMPT.format(language=language)
            )

            content = (response.text or "").strip()

            if not content:
                raise ValueError(
                    "Gemini returned an empty response"
                )

            if content.startswith("```"):
                raise ValueError(
                    "Gemini returned Markdown instead of a Dockerfile"
                )

            print("Dockerfile generated successfully!")

            return content

        except errors.APIError as error:

            status_code = getattr(error, "code", None)

            retryable_codes = {
                429, 500, 502, 503, 504
            }

            if (
                status_code not in retryable_codes
                or attempt == MAX_RETRIES
            ):
                raise

            delay = (
                BASE_DELAY * (2 ** attempt)
                + random.uniform(0, 1)
            )

            print(
                f"Temporary Gemini API error "
                f"(HTTP {status_code})."
            )

            print(
                f"Retry {attempt + 1}/{MAX_RETRIES} "
                f"in {delay:.1f} seconds..."
            )

            time.sleep(delay)

    raise RuntimeError(
        "Gemini API retry attempts exhausted"
    )


# ==========================================
# HADOLINT VALIDATION
# ==========================================

def validate_dockerfile(dockerfile_path):

    if not shutil.which("hadolint"):
        raise RuntimeError(
            "Hadolint is not installed or not available in PATH"
        )

    try:
        result = subprocess.run(
            [
                "hadolint",
                "--format",
                "json",
                str(dockerfile_path)
            ],
            capture_output=True,
            text=True,
            timeout=30,
            check=False
        )

    except subprocess.TimeoutExpired:
        raise RuntimeError(
            "Hadolint validation timed out after 30 seconds"
        )

    try:
        findings = json.loads(
            result.stdout or "[]"
        )

    except json.JSONDecodeError:
        raise RuntimeError(
            "Unable to parse Hadolint output: "
            + (result.stderr or result.stdout)
        )

    if not isinstance(findings, list):
        raise RuntimeError(
            "Unexpected Hadolint JSON response"
        )

    if result.returncode not in (0, 1):
        raise RuntimeError(
            f"Hadolint execution failed "
            f"(exit code {result.returncode}): "
            f"{result.stderr}"
        )

    if result.returncode == 1 and not findings:
        raise RuntimeError(
            "Hadolint failed without returning findings: "
            + (result.stderr or "Unknown error")
        )

    return {
        "passed": result.returncode == 0,
        "findings": findings
    }


# ==========================================
# MAIN APPLICATION
# ==========================================

def main():

    print("\n=== GenAI Dockerfile Generator V2 ===")

    for number, language in SUPPORTED_LANGUAGES.items():
        print(
            f"{number}. {language.capitalize()}"
        )

    choice = input(
        "\nSelect language (1-4): "
    ).strip()

    if choice not in SUPPORTED_LANGUAGES:
        print(
            "Invalid selection. Choose 1, 2, 3 or 4."
        )
        return 1

    api_key = os.getenv("GEMINI_API_KEY")

    if not api_key:
        print(
            "ERROR: GEMINI_API_KEY is not configured"
        )
        return 1

    language = SUPPORTED_LANGUAGES[choice]

    output_dir = OUTPUT_ROOT / language

    output_file = output_dir / "Dockerfile"

    report_file = (
        output_dir / "validation_report.json"
    )

    try:

        print(
            f"\nGenerating Dockerfile for "
            f"{language} using {MODEL}..."
        )

        client = genai.Client(
            api_key=api_key,
            http_options={
                "timeout": 60000,
                "retry_options": {
                    "attempts": 1
                }
            }
        )

        dockerfile = generate_dockerfile(
            client,
            language
        )

        output_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        output_file.write_text(
            dockerfile + "\n",
            encoding="utf-8"
        )

        print(
            f"\nSaved Dockerfile: {output_file}"
        )

        print(
            "\nRunning Hadolint validation..."
        )

        validation = validate_dockerfile(
            output_file
        )

        report = {
            "timestamp_utc": datetime.now(
                timezone.utc
            ).isoformat(),
            "language": language,
            "model": MODEL,
            "dockerfile": str(output_file),
            "validation_passed": validation["passed"],
            "finding_count": len(
                validation["findings"]
            ),
            "findings": validation["findings"]
        }

        report_file.write_text(
            json.dumps(
                report,
                indent=2
            ) + "\n",
            encoding="utf-8"
        )

        if validation["passed"]:

            print(
                "\nPASS: Hadolint found no issues "
                "at its configured failure threshold."
            )

        else:

            print(
                f"\nFAIL: Hadolint reported "
                f"{len(validation['findings'])} finding(s):"
            )

            for finding in validation["findings"]:

                print(
                    f"Line {finding.get('line', '?')}: "
                    f"{finding.get('code', '?')} "
                    f"[{finding.get('level', '?')}] - "
                    f"{finding.get('message', '')}"
                )

        print(
            f"\nValidation report saved: "
            f"{report_file}"
        )

        if validation["passed"]:
            return 0

        return 2

    except Exception as error:

        print(
            f"\nERROR: "
            f"{type(error).__name__}: {error}"
        )

        return 1


# ==========================================
# ENTRY POINT
# ==========================================

if __name__ == "__main__":

    try:
        sys.exit(main())

    except (KeyboardInterrupt, EOFError):

        print("\nOperation cancelled.")

        sys.exit(130)
