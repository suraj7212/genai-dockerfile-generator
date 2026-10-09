
import os
from pathlib import Path
from google import genai

SUPPORTED_LANGUAGES = {
    "1": "python",
    "2": "java",
    "3": "nodejs",
    "4": "go"
}

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY is not configured")

client = genai.Client(api_key=api_key)

MODEL = "gemini-3.8-flash"

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

def generate_dockerfile(language):
    response = client.models.generate_content(
        model=MODEL,
        contents=PROMPT.format(language=language)
    )

    if not response.text:
        raise ValueError("Gemini returned an empty response")

    return response.text.strip()


def main():
    print("\n=== GenAI Dockerfile Generator ===")

    for number, language in SUPPORTED_LANGUAGES.items():
        print(f"{number}. {language.capitalize()}")

    choice = input("\nSelect language (1-4): ").strip()

    if choice not in SUPPORTED_LANGUAGES:
        print("Invalid selection. Choose 1, 2, 3 or 4.")
        return

    language = SUPPORTED_LANGUAGES[choice]

    print(f"\nGenerating Dockerfile for {language}...")

    try:
        dockerfile = generate_dockerfile(language)

        output_dir = Path("generated") / language
        output_dir.mkdir(parents=True, exist_ok=True)

        output_file = output_dir / "Dockerfile"
        output_file.write_text(dockerfile + "\n")

        print("\nGenerated Dockerfile:\n")
        print(dockerfile)

        print(f"\nSaved to: {output_file}")

    except Exception as error:
        print(f"Generation failed: {error}")


if __name__ == "__main__":
    main()

