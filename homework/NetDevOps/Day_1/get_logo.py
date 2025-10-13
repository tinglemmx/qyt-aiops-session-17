import json
import requests
from pathlib import Path
import pprint
from bs4 import BeautifulSoup
from urllib.parse import urljoin
import os

pp = pprint.PrettyPrinter(indent=4)

base_dir = Path(__file__).resolve().parent


def load_and_simplify_headers(json_path, keys_keep=None):
    if keys_keep is None:
        keys_keep = {"Cookie", "User-Agent",
                     "Accept", "Accept-Language", "Referer"}
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    headers_list = data.get("requestHeaders", {}).get("headers", [])
    simplified_headers = {h["name"]: h["value"]
                          for h in headers_list if h["name"] in keys_keep}
    return simplified_headers


def fetch_page(url, headers):
    resp = requests.get(url, headers=headers)
    resp.raise_for_status()
    return resp.text


def extract_image_urls(html, base_url):
    soup = BeautifulSoup(html, "html.parser")
    img_urls = set()
    for img in soup.find_all("img"):
        src = img.get("src")
        if src:
            full_url = urljoin(base_url, src)
            img_urls.add(full_url)
    return list(img_urls)


def download_images(img_urls, headers, save_dir="images"):
    os.makedirs(save_dir, exist_ok=True)
    for img_url in img_urls:
        try:
            r = requests.get(img_url, headers=headers, stream=True, timeout=15)
            r.raise_for_status()
            filename = os.path.join(
                save_dir, os.path.basename(img_url.split("?")[0]))
            with open(filename, "wb") as f:
                for chunk in r.iter_content(8192):
                    f.write(chunk)
            print(f"[OK] {img_url} -> {filename}")
        except Exception as e:
            print(f"[ERR] {img_url} -> {e}")


def fetch_and_download_images(url, headers_json_file, save_dir="images"):
    headers = load_and_simplify_headers(headers_json_file)
    html = fetch_page(url, headers)
    # with open( base_dir/"index.html", "w", encoding="utf-8") as f:
    #     f.write(html)
    img_urls = extract_image_urls(html, url)
    print(f"找到 {len(img_urls)} 张图片")
    download_images(img_urls, headers, save_dir)


if __name__ == '__main__':
    url = 'https://qytsystem.qytang.com/python_enhance/python_enhance_home'
    request_headers_file = base_dir / 'request_headers.json'
    fetch_and_download_images(
        url, request_headers_file, save_dir=base_dir / 'images')
