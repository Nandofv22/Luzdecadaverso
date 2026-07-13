import os
import time

import requests

GRAPH_API_VERSION = os.environ.get("GRAPH_API_VERSION", "v21.0")
GRAPH_API_HOST = os.environ.get("GRAPH_API_HOST", "https://graph.instagram.com")
GRAPH_BASE = f"{GRAPH_API_HOST}/{GRAPH_API_VERSION}"


class InstagramApiError(RuntimeError):
    pass


def _check(resp):
    if resp.status_code >= 400:
        raise InstagramApiError(f"{resp.status_code} {resp.text[:800]}")
    return resp.json()


def create_carousel_item(ig_user_id, access_token, image_url):
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        data={"image_url": image_url, "is_carousel_item": "true", "access_token": access_token},
        timeout=60,
    )
    return _check(resp)["id"]


def create_media_container(ig_user_id, access_token, image_url, caption):
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        data={"image_url": image_url, "caption": caption, "access_token": access_token},
        timeout=60,
    )
    return _check(resp)["id"]


def create_carousel_container(ig_user_id, access_token, children_ids, caption):
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media",
        data={
            "media_type": "CAROUSEL",
            "children": ",".join(children_ids),
            "caption": caption,
            "access_token": access_token,
        },
        timeout=60,
    )
    return _check(resp)["id"]


def wait_until_finished(creation_id, access_token, timeout_s=90, interval_s=3):
    deadline = time.time() + timeout_s
    last_status = None
    while time.time() < deadline:
        resp = requests.get(
            f"{GRAPH_BASE}/{creation_id}",
            params={"fields": "status_code", "access_token": access_token},
            timeout=30,
        )
        data = _check(resp)
        last_status = data.get("status_code")
        if last_status == "FINISHED":
            return True
        if last_status == "ERROR":
            raise InstagramApiError(f"Container {creation_id} entrou em erro de processamento: {data}")
        time.sleep(interval_s)
    raise InstagramApiError(f"Timeout esperando container {creation_id} ficar pronto (ultimo status: {last_status})")


def publish_container(ig_user_id, access_token, creation_id):
    resp = requests.post(
        f"{GRAPH_BASE}/{ig_user_id}/media_publish",
        data={"creation_id": creation_id, "access_token": access_token},
        timeout=60,
    )
    return _check(resp)["id"]


def wait_for_public_url(url, timeout_s=90, interval_s=3):
    deadline = time.time() + timeout_s
    last_status = None
    while time.time() < deadline:
        try:
            r = requests.head(url, timeout=10, allow_redirects=True)
            last_status = r.status_code
            if r.status_code == 200:
                return True
        except requests.RequestException as e:
            last_status = str(e)
        time.sleep(interval_s)
    raise InstagramApiError(f"Timed out waiting for {url} to become public (last status: {last_status})")
