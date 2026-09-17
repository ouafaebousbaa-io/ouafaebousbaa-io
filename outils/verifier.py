#!/usr/bin/env python3
"""Vérifie la cohérence SEO du site avant un commit.

    python3 outils/verifier.py

Contrôle :
  - le JSON-LD de l'accueil est parsable et décrit bien le Person attendu ;
  - canonical, og:url et Person.url valent tous BASE + "/", et @id BASE + "/#person" ;
  - les rel="me" du <head>, ceux du corps et sameAs listent les mêmes profils ;
  - sitemap.xml est un XML valide qui liste exactement l'accueil ;
  - robots.txt pointe vers le bon sitemap.

Sort avec le code 1 dès qu'un écart est trouvé.
"""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

BASE = "https://ouafaebousbaa-io.github.io"
NOM = "Ouafae Bousbaa"
SITEMAP_NS = "{http://www.sitemaps.org/schemas/sitemap/0.9}"

RACINE = Path(__file__).resolve().parent.parent
ACCUEIL = BASE + "/"
ID_PERSON = ACCUEIL + "#person"


def attribut(html: str, motif: str) -> str | None:
    trouve = re.search(motif, html)
    return trouve.group(1) if trouve else None


def main() -> int:
    ecarts: list[str] = []
    idx = (RACINE / "index.html").read_text(encoding="utf-8")

    # --- JSON-LD ----------------------------------------------------------
    bloc = re.search(r'<script type="application/ld\+json">(.*?)</script>', idx, re.S)
    if bloc is None:
        print("index.html : aucun bloc JSON-LD")
        return 1
    try:
        person = json.loads(bloc.group(1))
    except json.JSONDecodeError as err:
        print(f"index.html : JSON-LD invalide -> {err}")
        return 1

    if person.get("@type") != "Person":
        ecarts.append(f"index.html : @type = {person.get('@type')!r}, attendu 'Person'")
    if person.get("name") != NOM:
        ecarts.append(f"index.html : Person.name = {person.get('name')!r}, attendu {NOM!r}")
    for champ in ("givenName", "familyName", "sameAs", "knowsAbout"):
        if not person.get(champ):
            ecarts.append(f"index.html : champ JSON-LD {champ} manquant")

    # --- URL --------------------------------------------------------------
    for nom, valeur in (
        ("canonical", attribut(idx, r'<link rel="canonical" href="([^"]+)"')),
        ("og:url", attribut(idx, r'property="og:url" content="([^"]+)"')),
        ("Person.url", person.get("url")),
    ):
        if valeur != ACCUEIL:
            ecarts.append(f"index.html : {nom} = {valeur!r}, attendu {ACCUEIL!r}")
    if person.get("@id") != ID_PERSON:
        ecarts.append(f"index.html : @id = {person.get('@id')!r}, attendu {ID_PERSON!r}")

    titre = attribut(idx, r"<title>(.*?)</title>")
    if titre != NOM:
        ecarts.append(f"index.html : title = {titre!r}, attendu {NOM!r}")

    # --- profils ----------------------------------------------------------
    tete = set(re.findall(r'<link rel="me" href="([^"]+)"', idx))
    corps = set(re.findall(r'<a rel="me" href="([^"]+)"', idx))
    mails = {u for u in tete if u.startswith("mailto:")}
    if tete != corps:
        ecarts.append(f"index.html : rel=me <head> != corps -> {sorted(tete ^ corps)}")
    if (tete - mails) != set(person.get("sameAs", [])):
        divergents = sorted((tete - mails) ^ set(person.get("sameAs", [])))
        ecarts.append(f"index.html : rel=me != sameAs -> {divergents}")
    for url in tete | set(person.get("sameAs", [])):
        if "utm_" in url or "?" in url:
            ecarts.append(f"index.html : URL de profil non normalisée -> {url}")

    # --- sitemap et robots -------------------------------------------------
    try:
        locs = [e.text for e in ET.parse(RACINE / "sitemap.xml").getroot().iter(SITEMAP_NS + "loc")]
        if locs != [ACCUEIL]:
            ecarts.append(f"sitemap.xml : {locs} != {[ACCUEIL]}")
    except ET.ParseError as err:
        ecarts.append(f"sitemap.xml : XML invalide -> {err}")

    robots = (RACINE / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {BASE}/sitemap.xml" not in robots:
        ecarts.append("robots.txt : ligne Sitemap incohérente")

    # --- rapport ----------------------------------------------------------
    if ecarts:
        print(f"{len(ecarts)} écart(s) :")
        for e in ecarts:
            print(" -", e)
        return 1

    print(f"Cohérent. Accueil seul, base {BASE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
