"""
Script para fazer push de prompts otimizados ao LangSmith Prompt Hub.

Este script:
1. Lê os prompts otimizados de prompts/bug_to_user_story_v2.yml
2. Valida os prompts
3. Faz push PÚBLICO para o LangSmith Hub
4. Adiciona metadados (tags, descrição, técnicas utilizadas)

SIMPLIFICADO: Código mais limpo e direto ao ponto.
"""

import os
import sys
from dotenv import load_dotenv
from langsmith import Client
from langchain_core.prompts import ChatPromptTemplate
from utils import load_yaml, check_env_vars, print_section_header, validate_prompt_structure

load_dotenv()

PROMPT_FILE = "prompts/bug_to_user_story_v2.yml"
PROMPT_KEY = "bug_to_user_story_v2"


def push_prompt_to_langsmith(prompt_name: str, prompt_data: dict) -> bool:
    """
    Faz push do prompt otimizado para o LangSmith Hub (PÚBLICO).

    Args:
        prompt_name: Nome do prompt
        prompt_data: Dados do prompt

    Returns:
        True se sucesso, False caso contrário
    """
    username = os.getenv("USERNAME_LANGSMITH_HUB")
    if not username:
        print("❌ USERNAME_LANGSMITH_HUB não configurado no .env")
        return False

    repo_handle = f"{username}/{prompt_name}"

    try:
        system_template = prompt_data.get("system_prompt", "")
        user_template = prompt_data.get("user_prompt", "{bug_report}")

        prompt = ChatPromptTemplate.from_messages([
            ("system", system_template),
            ("user", user_template),
        ])

        description = prompt_data.get("description", "Prompt otimizado para bug to user story")
        tags = prompt_data.get("tags", [])

        client = Client()
        url = client.push_prompt(
            repo_handle,
            object=prompt,
            is_public=True,
            description=description,
            tags=tags,
        )

        print(f"✓ Prompt publicado com sucesso: {url}")
        return True

    except Exception as e:
        print(f"❌ Erro ao fazer push do prompt: {e}")
        return False


def validate_prompt(prompt_data: dict) -> tuple[bool, list]:
    """
    Valida estrutura básica de um prompt (versão simplificada).

    Args:
        prompt_data: Dados do prompt

    Returns:
        (is_valid, errors) - Tupla com status e lista de erros
    """
    return validate_prompt_structure(prompt_data)


def main():
    """Função principal"""
    print_section_header("PUSH DE PROMPTS OTIMIZADOS AO LANGSMITH HUB")

    required_vars = ["LANGSMITH_API_KEY", "USERNAME_LANGSMITH_HUB"]
    if not check_env_vars(required_vars):
        return 1

    print(f"Carregando prompt de {PROMPT_FILE}...")
    yaml_data = load_yaml(PROMPT_FILE)
    if not yaml_data:
        return 1

    if PROMPT_KEY not in yaml_data:
        print(f"❌ Chave '{PROMPT_KEY}' não encontrada no YAML.")
        print(f"   Chaves disponíveis: {list(yaml_data.keys())}")
        return 1

    prompt_data = yaml_data[PROMPT_KEY]

    print("Validando estrutura do prompt...")
    is_valid, errors = validate_prompt(prompt_data)
    if not is_valid:
        print("❌ Validação falhou:")
        for error in errors:
            print(f"   - {error}")
        return 1

    print("✓ Estrutura do prompt válida.")

    print(f"Publicando '{PROMPT_KEY}' no LangSmith Hub...")
    if push_prompt_to_langsmith(PROMPT_KEY, prompt_data):
        print("\n✅ Processo concluído com sucesso!")
        return 0

    print("\n❌ Falha ao publicar o prompt.")
    return 1


if __name__ == "__main__":
    sys.exit(main())
