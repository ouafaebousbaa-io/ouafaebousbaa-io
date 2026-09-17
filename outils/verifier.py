#!/usr/bin/env python3
"""Vérifie la cohérence SEO du site avant un commit.

    python3 outils/verifier.py

Contrôle :
  - chaque JSON-LD est parsable ;
  - canonical, og:url et Person.url valent tous BASE + "/" ;
  - les rel="me" du <head>, ceux du corps et sameAs listent les mêmes profils ;
  - sitemap.xml est un XML valide listant l'accueil puis exactement les essais
    publiés (fichiers de essais/ ne commençant pas par "_") ;
  - chaque essai a un canonical propre, un title « Titre — Nom », un
    author.@id pointant vers le Person de l'accueil, et plus aucun marqueur
    {{...}} ni noindex ;
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


def jsonld(html: str) -> list[dict]:
    blocs = re.findall(r'<script type="application/ld\+json">(.*?)</script>', html, re.S)
    return [json.loads(b) for b in blocs]


def attribut(html: str, motif: str) -> str | None:
    trouve = re.search(motif, html)
    return trouve.group(1) if trouve else None


def main() -> int:
    ecarts: list[str] = []

    # --- accueil ---------------------------------------------------------
    idx = (RACINE / "index.html").read_text(encoding="utf-8")
    try:
        person = jsonld(idx)[0]
    except (IndexError, json.JSONDecodeError) as err:
        print(f"index.html : JSON-LD illisible -> {err}")
        return 1

    for nom, valeur in (
        ("canonical", attribut(idx, r'<link rel="canonical" href="([^"]+)"')),
        ("og:url", attribut(idx, r'property="og:url" content="([^"]+)"')),
        ("Person.url", person.get("url")),
    ):
        if valeur != ACCUEIL:
            ecarts.append(f"index.html : {nom} = {valeur!r}, attendu {ACCUEIL!r}")
    if person.get("@id") != ID_PERSON:
        ecarts.append(f"index.html : @id = {person.get('@id')!r}, attendu {ID_PERSON!r}")
    if person.get("name") != NOM:
        ecarts.append(f"index.html : Person.name = {person.get('name')!r}, attendu {NOM!r}")

    tete = set(re.findall(r'<link rel="me" href="([^"]+)"', idx))
    corps = set(re.findall(r'<a rel="me" href="([^"]+)"', idx))
    mails = {u for u in tete if u.startswith("mailto:")}
    if tete != corps:
        ecarts.append(f"index.html : rel=me <head> != corps -> {sorted(tete ^ corps)}")
    if (tete - mails) != set(person.get("sameAs", [])):
        manquants = sorted((tete - mails) ^ set(person.get("sameAs", [])))
        ecarts.append(f"index.html : rel=me != sameAs -> {manquants}")

    # --- essais ----------------------------------------------------------
    essais = sorted(p for p in (RACINE / "essais").glob("*.html") if not p.name.startswith("_"))
    for essai in essais:
        html = essai.read_text(encoding="utf-8")
        rel = f"essais/{essai.name}"
        url = f"{BASE}/{rel}"

        if re.search(r"\{\{[^}]+\}\}", html):
            ecarts.append(f"{rel} : marqueurs {{{{...}}}} non remplacés")
        if "noindex" in html:
            ecarts.append(f"{rel} : la balise noindex du modèle n'a pas été retirée")
        if attribut(html, r'<link rel="canonical" href="([^"]+)"') != url:
            ecarts.append(f"{rel} : canonical incohérent, attendu {url!r}")
        if attribut(html, r'property="og:url" content="([^"]+)"') != url:
            ecarts.append(f"{rel} : og:url incohérent, attendu {url!r}")

        titre = attribut(html, r"<title>(.*?)</title>")
        if not titre or not titre.endswith(f" — {NOM}"):
            ecarts.append(f"{rel} : title = {titre!r}, attendu « Titre — {NOM} »")

        try:
            article = jsonld(html)[0]
        except (IndexError, json.JSONDecodeError) as err:
            ecarts.append(f"{rel} : JSON-LD illisible -> {err}")
            continue
        if article.get("@type") != "Article":
            ecarts.append(f"{rel} : @type = {article.get('@type')!r}, attendu 'Article'")
        for champ in ("headline", "datePublished", "inLanguage"):
            if not article.get(champ):
                ecarts.append(f"{rel} : champ JSON-LD {champ} manquant")
        if article.get("inLanguage") not in (None, "fr"):
            ecarts.append(f"{rel} : inLanguage = {article['inLanguage']!r}, attendu 'fr'")
        if article.get("author", {}).get("@id") != ID_PERSON:
            ecarts.append(f"{rel} : author.@id ne référence pas {ID_PERSON}")
        if f'href="/"' not in html:
            ecarts.append(f"{rel} : pas de lien retour vers l'accueil")
        if rel not in idx:
            ecarts.append(f"{rel} : absent de la liste « Écrits » de index.html")

    # --- sitemap et robots ------------------------------------------------
    try:
        locs = [e.text for e in ET.parse(RACINE / "sitemap.xml").getroot().iter(SITEMAP_NS + "loc")]
    except ET.ParseError as err:
        ecarts.append(f"sitemap.xml : XML invalide -> {err}")
        locs = None
    attendus = [ACCUEIL] + [f"{BASE}/essais/{e.name}" for e in essais]
    if locs is not None and locs != attendus:
        ecarts.append(f"sitemap.xml : {locs} != {attendus}")

    robots = (RACINE / "robots.txt").read_text(encoding="utf-8")
    if f"Sitemap: {BASE}/sitemap.xml" not in robots:
        ecarts.append("robots.txt : ligne Sitemap incohérente")

    # --- rapport ----------------------------------------------------------
    if ecarts:
        print(f"{len(ecarts)} écart(s) :")
        for e in ecarts:
            print(" -", e)
        return 1

    print(f"Cohérent. Accueil + {len(essais)} essai(s), base {BASE}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
