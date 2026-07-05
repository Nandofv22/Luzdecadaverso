import argparse
import datetime
import json
import os
import sys

import instagram_api
import state

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTPUT_DIR = os.path.join(ROOT, "output")
DATA_PATH = os.path.join(ROOT, "data", "mensagens.json")
ENV_LOCAL = os.path.join(ROOT, ".env.local")


def load_env_local():
    if not os.path.exists(ENV_LOCAL):
        return
    with open(ENV_LOCAL, encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, _, value = line.partition("=")
            os.environ.setdefault(key.strip(), value.strip())


def bank_len():
    with open(DATA_PATH, encoding="utf-8") as f:
        return len(json.load(f)["mensagens"])


def build_raw_url(image_filename):
    repo = os.environ.get("GITHUB_REPOSITORY")
    branch = os.environ.get("GITHUB_REF_NAME", "main")
    if not repo:
        raise RuntimeError("GITHUB_REPOSITORY nao definido (defina manualmente pra teste local ou rode dentro do GitHub Actions)")
    return f"https://raw.githubusercontent.com/{repo}/{branch}/output/{image_filename}"


def main():
    load_env_local()

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None)
    parser.add_argument("--slot", default="am", choices=["am", "pm"])
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    prefix = f"carrossel_{date_str}_{args.slot}"
    meta_path = os.path.join(OUTPUT_DIR, f"{prefix}.meta.json")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    ig_user_id = os.environ["IG_USER_ID"]
    access_token = os.environ["IG_ACCESS_TOKEN"]

    image_urls = [build_raw_url(fn) for fn in meta["image_filenames"]]
    print("Aguardando imagens ficarem publicas...")
    for url in image_urls:
        instagram_api.wait_for_public_url(url)

    print("Criando itens do carrossel...")
    children_ids = [
        instagram_api.create_carousel_item(ig_user_id, access_token, url) for url in image_urls
    ]

    print("Montando container do carrossel...")
    container_id = instagram_api.create_carousel_container(ig_user_id, access_token, children_ids, meta["caption"])

    print("Aguardando o Instagram processar o carrossel...")
    instagram_api.wait_until_finished(container_id, access_token)

    print("Publicando...")
    media_id = instagram_api.publish_container(ig_user_id, access_token, container_id)
    print(f"Publicado! media_id={media_id}")

    new_idx = state.advance_index("mensagem_index", bank_len())
    print(f"State avancado: mensagem_index -> {new_idx}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
