import argparse
import datetime
import json
import os
import sys

import instagram_api
import state
from publish_carousel import bank_len, build_raw_url, load_env_local

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTPUT_DIR = os.path.join(ROOT, "output")


def main():
    load_env_local()

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None)
    parser.add_argument("--slot", default="pm", choices=["am", "pm"])
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    prefix = f"versiculo_{date_str}_{args.slot}"
    meta_path = os.path.join(OUTPUT_DIR, f"{prefix}.meta.json")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    ig_user_id = os.environ["IG_USER_ID"]
    access_token = os.environ["IG_ACCESS_TOKEN"]

    image_url = build_raw_url(meta["image_filename"])
    print("Aguardando imagem ficar publica...")
    instagram_api.wait_for_public_url(image_url)

    print("Criando container...")
    container_id = instagram_api.create_media_container(ig_user_id, access_token, image_url, meta["caption"])

    print("Aguardando o Instagram processar a imagem...")
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
