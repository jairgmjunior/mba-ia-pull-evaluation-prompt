"""
Script para fazer pull de prompts do LangSmith Prompt Hub.

Este script:
1. Conecta ao LangSmith usando credenciais do .env
2. Faz pull dos prompts do Hub
3. Salva localmente em prompts/bug_to_user_story_v1.yml

SIMPLIFICADO: Usa serialização nativa do LangChain para extrair prompts.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from langchain import hub
from utils import save_yaml, check_env_vars, print_section_header

load_dotenv()

PROMPT_IDENTIFIER = "leonanluppi/bug_to_user_story_v1"
OUTPUT_PATH = "prompts/bug_to_user_story_v1.yml"


def _extract_messages(prompt_template) -> tuple[str, str]:
    """Extrai system_prompt e user_prompt de um ChatPromptTemplate."""
    system_prompt = ""
    user_prompt = "{bug_report}"

    for message in prompt_template.messages:
        if not hasattr(message, "prompt") or not hasattr(message.prompt, "template"):
            continue

        template = message.prompt.template
        message_type = message.__class__.__name__

        if "System" in message_type:
            system_prompt = template
        elif "Human" in message_type:
            user_prompt = template

    return system_prompt, user_prompt


def pull_prompts_from_langsmith() -> bool:
    """
    Faz pull do prompt do LangSmith Hub e salva localmente em YAML.

    Returns:
        True se sucesso, False caso contrário
    """
    try:
        print(f"Puxando prompt: {PROMPT_IDENTIFIER}")
        prompt_template = hub.pull(PROMPT_IDENTIFIER)

        system_prompt, user_prompt = _extract_messages(prompt_template)

        if not system_prompt:
            print("❌ Não foi possível extrair o system_prompt do template.")
            return False

        prompt_data = {
            "bug_to_user_story_v1": {
                "description": "Prompt para converter relatos de bugs em User Stories",
                "system_prompt": system_prompt,
                "user_prompt": user_prompt,
                "version": "v1",
                "created_at": "2025-01-15",
                "tags": ["bug-analysis", "user-story", "product-management"],
            }
        }

        if save_yaml(prompt_data, OUTPUT_PATH):
            print(f"✓ Prompt salvo em: {OUTPUT_PATH}")
            return True

        return False

    except Exception as e:
        print(f"❌ Erro ao fazer pull do prompt: {e}")
        return False


def main():
    """Função principal"""
    print_section_header("PULL DE PROMPTS DO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY"]
    if not check_env_vars(required_vars):
        return 1

    success = pull_prompts_from_langsmith()
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
