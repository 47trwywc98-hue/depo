#!/usr/bin/env python3
"""www.doganismakinalari.com üzerindeki stok ve iletişim bilgilerini JSON olarak çıkarır."""

from __future__ import annotations

import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Set

import requests
from bs4 import BeautifulSoup
from requests import Response

BASE_URL = "https://www.doganismakinalari.com/"
DATA_FILE = Path(__file__).resolve().parents[1] / "data" / "doganismakinalari-data.json"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Accept-Language": "tr-TR,tr;q=0.9,en-US;q=0.8,en;q=0.7",
}


def absolute_url(path: str) -> str:
    from urllib.parse import urljoin

    return urljoin(BASE_URL, path)


STOCK_PATH_CANDIDATES = [
    BASE_URL,
    absolute_url("urunler/"),
    absolute_url("stok/"),
    absolute_url("kategori/is-makinalari/"),
    absolute_url("urun-kategori/is-makineleri/"),
]

CONTACT_PATH_CANDIDATES = [
    BASE_URL,
    absolute_url("iletisim/"),
    absolute_url("hakkimizda/"),
]

TEL_PATTERN = re.compile(r"\+?\d[\d()\s-]{7,}")
EMAIL_PATTERN = re.compile(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", re.IGNORECASE)


def fetch(url: str, session: requests.Session) -> Optional[Response]:
    try:
        response = session.get(url, headers=HEADERS, timeout=30)
        response.raise_for_status()
        return response
    except requests.RequestException as exc:  # pragma: no cover - ağ bağımlı
        print(f"[WARN] {url} adresi alınamadı: {exc}", file=sys.stderr)
        return None


def iter_candidate_pages(urls: Iterable[str], session: requests.Session) -> Iterable[BeautifulSoup]:
    seen: Set[str] = set()
    for url in urls:
        if url in seen:
            continue
        seen.add(url)
        response = fetch(url, session)
        if not response:
            continue
        yield BeautifulSoup(response.text, "html.parser")


def normalise_phone(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip())


def extract_contact_data(session: requests.Session) -> Dict[str, str]:
    contact: Dict[str, str] = {}

    for soup in iter_candidate_pages(CONTACT_PATH_CANDIDATES, session):
        for link in soup.select('a[href^="tel:"]'):
            number = normalise_phone(link.get_text(strip=True))
            if not number:
                continue
            if "phone" not in contact:
                contact["phone"] = number
            elif "servicePhone" not in contact and number != contact.get("phone"):
                contact["servicePhone"] = number

        if "email" not in contact:
            mail_link = soup.select_one('a[href^="mailto:"]')
            if mail_link:
                contact["email"] = mail_link.get_text(strip=True)
            else:
                match = EMAIL_PATTERN.search(soup.get_text(" "))
                if match:
                    contact["email"] = match.group(0)

        if "address" not in contact:
            address_candidate = soup.select_one("address")
            if address_candidate:
                contact["address"] = address_candidate.get_text(strip=True)
                continue

            text_matches = []
            for element in soup.select("p, span, li"):
                text = element.get_text(separator=" ", strip=True)
                if not text:
                    continue
                if "adres" in text.lower() or TEL_PATTERN.search(text):
                    text_matches.append(text)
            if text_matches:
                # Adres bilgisi içeren en uzun metni kullan
                contact["address"] = max(text_matches, key=len)

        if {"phone", "email", "address"}.issubset(contact.keys()):
            break

    return contact


def extract_machine_specs(container: BeautifulSoup) -> List[str]:
    specs: List[str] = []
    for selector in [
        ".woocommerce-loop-product__title + p",
        ".woocommerce-product-details__short-description",
        ".product-short-description",
        ".excerpt",
        ".card-text",
        "p",
    ]:
        for element in container.select(selector):
            text = element.get_text(separator=" ", strip=True)
            if text and text not in specs and len(text) > 10:
                specs.append(text)
        if specs:
            break
    return specs


def extract_machines(session: requests.Session) -> List[Dict[str, object]]:
    machines: Dict[str, Dict[str, object]] = {}

    for soup in iter_candidate_pages(STOCK_PATH_CANDIDATES, session):
        for product in soup.select("li.product, div.product"):  # WooCommerce listeleri
            link = product.select_one("a[href]")
            if not link:
                continue
            detail_url = link.get("href")
            title_node = product.select_one(".woocommerce-loop-product__title, h2, h3")
            title = title_node.get_text(strip=True) if title_node else None
            if not title:
                continue
            specs = extract_machine_specs(product)
            machines[detail_url] = {
                "title": title,
                "detailUrl": detail_url,
                "specs": specs[:5],
            }

    return list(machines.values())


def save_data(contact: Dict[str, str], machines: List[Dict[str, object]]) -> None:
    data = {
        "lastFetched": datetime.now(tz=timezone.utc).isoformat(),
        "contact": {
            "phone": contact.get("phone", ""),
            "email": contact.get("email", ""),
            "address": contact.get("address", ""),
            "servicePhone": contact.get("servicePhone", contact.get("phone", "")),
        },
        "machines": machines,
    }

    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    DATA_FILE.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[INFO] {DATA_FILE} dosyası {len(machines)} makine ile güncellendi.")


def main() -> int:
    session = requests.Session()
    contact = extract_contact_data(session)
    machines = extract_machines(session)

    if not contact and not machines:
        print("[ERROR] Hiç veri toplanamadı. Lütfen URL'leri kontrol edin.", file=sys.stderr)
        return 1

    save_data(contact, machines)
    return 0


if __name__ == "__main__":
    sys.exit(main())
