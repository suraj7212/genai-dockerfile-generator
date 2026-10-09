# GenAI-Powered Dockerfile Generator

A Python-based DevOps project that uses Google's Gemini API
to generate Dockerfiles using Generative AI.

## Features
- Generate Dockerfiles using Gemini AI
- Support Python, Java, Node.js and Go
- Follow Docker best practices through prompt engineering
- Automatically save generated Dockerfiles

## Technologies
- Python
- Google Gemini API
- Docker
- Prompt Engineering

## Installation

Install dependencies:

pip install -r requirements.txt

Set your Gemini API key:

export GEMINI_API_KEY="your_api_key"

Run the application:

python generate_dockerfile.py

Select a programming language from the menu.

## Output

Generated Dockerfiles are saved in:

generated/<language>/Dockerfile

## Note

AI-generated Dockerfiles should be reviewed and tested
before using them in production.
