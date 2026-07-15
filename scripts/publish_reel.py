import argparse
import datetime
import json
import os
import sys

import instagram_api
from publish_carousel import build_raw_url, load_env_local

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
OUTPUT_DIR = os.path.join(ROOT, "output")


def main():
    load_env_local()

    parser = argparse.ArgumentParser()
    parser.add_argument("--date", default=None)
    args = parser.parse_args()

    date_str = args.date or datetime.date.today().isoformat()
    prefix = f"reel_{date_str}"
    meta_path = os.path.join(OUTPUT_DIR, f"{prefix}.meta.json")
    with open(meta_path, encoding="utf-8") as f:
        meta = json.load(f)

    ig_user_id = os.environ["IG_USER_ID"]
    access_token = os.environ["IG_ACCESS_TOKEN"]

    video_url = build_raw_url(meta["video_filename"])
    print("Aguardando video ficar publico...")
    instagram_api.wait_for_public_url(video_url)

    print("Criando container do Reels...")
    container_id = instagram_api.create_reels_container(ig_user_id, access_token, video_url, meta["caption"])

    print("Aguardando o Instagram processar o video (pode demorar mais que imagem)...")
    instagram_api.wait_until_finished(container_id, access_token, timeout_s=300, interval_s=5)

    print("Publicando...")
    media_id = instagram_api.publish_container(ig_user_id, access_token, container_id)
    print(f"Publicado! media_id={media_id}")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"FAILED: {e}", file=sys.stderr)
        sys.exit(1)
