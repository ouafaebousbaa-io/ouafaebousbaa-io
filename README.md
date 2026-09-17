# ouafaebousbaa-io.github.io

Site personnel de **Ouafae Bousbaa** — <https://ouafaebousbaa-io.github.io/>

Une seule page, HTML/CSS statique, aucun framework, aucun build, aucun
JavaScript. Objectif : faire remonter le nom et les profils dans Google.

## Structure

```
index.html          la page (nom, présentation, Ailleurs, Contact)
assets/style.css    feuille de style
sitemap.xml         l'accueil
robots.txt          autorise tout, pointe vers le sitemap
.nojekyll           désactive le traitement Jekyll de GitHub Pages
outils/verifier.py  contrôle de cohérence SEO, à lancer avant chaque commit
```

## Identité — à garder identique partout

Ces valeurs apparaissent dans `index.html` (`canonical`, `og:url`,
`rel="me"`, JSON-LD `@id`/`url`/`sameAs`) et dans `sitemap.xml` /
`robots.txt`. Si l'une change, la changer dans **tous** ces endroits.

| | |
|---|---|
| Nom | Ouafae Bousbaa |
| Site | https://ouafaebousbaa-io.github.io/ |
| `@id` du Person | https://ouafaebousbaa-io.github.io/#person |
| GitHub | https://github.com/ouafaebousbaa-io |
| LinkedIn | https://www.linkedin.com/in/ouafae-bousbaa-b40099126/ |
| Goodreads | https://www.goodreads.com/user/show/116270179-ouafae-bousbaa |

Après toute modification :

```sh
python3 outils/verifier.py   # 0 = cohérent, 1 = liste les écarts
```

Il relit `index.html`, `sitemap.xml` et `robots.txt` et signale les écarts :
JSON-LD illisible, `canonical` / `og:url` / `@id` divergents, `rel="me"` et
`sameAs` désynchronisés, URL de profil polluée par des paramètres de suivi,
sitemap ou ligne `Sitemap:` incohérents.

Aucune adresse email n'apparaît sur la page, ni en `mailto:` ni dans le
JSON-LD : la section Contact renvoie vers LinkedIn. Une page indexée qui
expose une adresse en clair se fait récolter par les robots à spam.

## Ajouter un profil

Trois ajouts dans `index.html`, sans quoi `verifier.py` proteste : un
`<link rel="me">` dans le `<head>`, une entrée dans le tableau `sameAs` du
JSON-LD, et un `<li><a rel="me" …>` dans la section Ailleurs.

## Vérifier le rendu en local

```sh
python3 -m http.server 8000   # puis http://127.0.0.1:8000/
```

Passer par un serveur et non par `file://` : les chemins absolus
(`/assets/style.css`) ne se résolvent qu'à la racine d'un hôte.

## Déploiement (GitHub Pages)

Le site est servi à la racine de `ouafaebousbaa-io.github.io`, ce qui suppose
que **ce dépôt s'appelle `ouafaebousbaa-io.github.io`** — c'est la règle des
sites utilisateur : le nom du dépôt doit être exactement
`<login>.github.io`. Les chemins absolus `/assets/style.css` et le canonical
en dépendent.

Un dépôt qui porte ce nom est publié automatiquement depuis sa branche par
défaut ; il n'y a rien à activer dans Settings → Pages. Si la page ne sort
pas au bout de quelques minutes : Settings → Pages → Source *Deploy from a
branch* → Branch `main`, dossier `/ (root)` → Save.

### Domaine personnalisé, plus tard

1. Créer un fichier `CNAME` à la racine contenant le domaine, ex. `ouafaebousbaa.fr`
2. DNS : un `ALIAS`/`ANAME` (ou les 4 `A` vers les IP de GitHub Pages) sur
   l'apex, ou un `CNAME` vers `ouafaebousbaa-io.github.io.` pour un sous-domaine
3. Settings → Pages → Custom domain, puis cocher *Enforce HTTPS*
4. Remplacer `https://ouafaebousbaa-io.github.io` partout, y compris la
   constante `BASE` en tête de `outils/verifier.py` :

   ```sh
   grep -rn 'ouafaebousbaa-io.github.io' --include='*.html' --include='*.xml' --include='*.txt' --include='*.py' .
   ```

## Publier des essais, plus tard

Le dossier `essais/` et son modèle ont été retirés. Le nécessaire est
toujours dans l'historique git :

```sh
git show 1840f2a --stat     # « Ajoute le modèle d'essai »
git checkout 1840f2a -- essais/
```
