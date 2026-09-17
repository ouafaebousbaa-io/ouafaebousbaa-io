# ouafaebousbaa-io.github.io

Site personnel de **Ouafae Bousbaa** — <https://ouafaebousbaa-io.github.io/>

HTML/CSS statique, aucun framework, aucun build, aucun JavaScript.

## Structure

```
index.html          page d'accueil (nom, présentation, Écrits, Ailleurs, Contact)
essais/             un fichier HTML par essai
essais/_modele.html modèle à copier (noindex, jamais publié tel quel)
assets/style.css    feuille de style partagée par toutes les pages
sitemap.xml         accueil + un <url> par essai
robots.txt          autorise tout, pointe vers le sitemap
.nojekyll           désactive le traitement Jekyll de GitHub Pages
outils/verifier.py  contrôle de cohérence SEO, à lancer avant chaque commit
```

## Ajouter un essai en 3 étapes

1. **Créer le fichier.** Copier le modèle et remplacer ses marqueurs :

   ```sh
   cp essais/_modele.html essais/mon-essai.html
   ```

   Marqueurs à remplacer dans le nouveau fichier — `{{SLUG}}` (le nom du
   fichier sans `.html`), `{{TITRE}}`, `{{DESCRIPTION}}`, `{{DATE-ISO}}`
   (`2026-09-17`), `{{DATE-LISIBLE}}` (`17 septembre 2026`) — puis **supprimer
   la ligne `<meta name="robots" content="noindex">`**, sans quoi Google
   n'indexera pas la page.

   ```sh
   grep -n '{{\|noindex' essais/mon-essai.html   # doit ne rien renvoyer une fois terminé
   ```

2. **Ajouter une ligne dans `index.html`**, sous `<h2>Écrits</h2>`, à
   l'intérieur du `<ul>` (et retirer le `<li class="vide">` s'il est encore là) :

   ```html
   <li><a href="/essais/mon-essai.html">Titre de l'essai</a> <span class="date">2026</span></li>
   ```

3. **Ajouter une ligne dans `sitemap.xml`**, avant `</urlset>` :

   ```xml
   <url>
     <loc>https://ouafaebousbaa-io.github.io/essais/mon-essai.html</loc>
   </url>
   ```

Puis vérifier et publier :

```sh
python3 outils/verifier.py          # 0 = cohérent, 1 = liste les écarts
git add -A && git commit -m "Ajoute l'essai : Titre" && git push
```

`verifier.py` relit tous les fichiers et signale précisément ce qui manque :
marqueur `{{…}}` oublié, `noindex` resté en place, essai absent de
`index.html` ou de `sitemap.xml`, `author.@id` cassé, `title` mal formé.
GitHub Pages redéploie en une minute environ.

## Identité — à garder identique partout

Ces valeurs apparaissent dans `index.html` (`canonical`, `og:url`,
`rel="me"`, JSON-LD `@id`/`sameAs`), dans chaque essai (`canonical`,
`author.@id`) et dans `sitemap.xml`/`robots.txt`. Si l'une change, la changer
dans **tous** ces endroits.

| | |
|---|---|
| Nom | Ouafae Bousbaa |
| Site | https://ouafaebousbaa-io.github.io/ |
| `@id` du Person | https://ouafaebousbaa-io.github.io/#person |
| GitHub | https://github.com/ouafaebousbaa-io |
| LinkedIn | https://www.linkedin.com/in/ouafae-bousbaa-b40099126/ |
| Goodreads | https://www.goodreads.com/user/show/116270179-ouafae-bousbaa |
| Email | wafaa.bousbaa@gmail.com |

Vérifier la cohérence après toute modification :

```sh
python3 outils/verifier.py
grep -rn 'ouafaebousbaa-io.github.io' --include='*.html' --include='*.xml' --include='*.txt' .
```

Pour ajouter un profil (X, Mastodon…), il faut **trois** ajouts dans
`index.html` : un `<link rel="me">` dans le `<head>`, une entrée dans le
tableau `sameAs` du JSON-LD, et un `<li><a rel="me" …>` dans la section
Ailleurs.

## Déploiement (GitHub Pages)

Le site est servi à la racine du domaine `ouafaebousbaa-io.github.io`, ce qui
suppose que **ce dépôt s'appelle `ouafaebousbaa-io.github.io`** (Settings →
General → Repository name). Les chemins absolus `/assets/style.css` et
`/essais/…` en dépendent.

Activation : Settings → Pages → Source : *Deploy from a branch* → Branch :
`main`, dossier `/ (root)` → Save.

### Domaine personnalisé, plus tard

1. Créer un fichier `CNAME` à la racine contenant le domaine, ex. `ouafaebousbaa.fr`
2. DNS : un `ALIAS`/`ANAME` (ou 4 `A` vers les IP de GitHub Pages) sur l'apex,
   ou un `CNAME` vers `ouafaebousbaa-io.github.io.` pour un sous-domaine
3. Settings → Pages → Custom domain, puis cocher *Enforce HTTPS*
4. Remplacer `https://ouafaebousbaa-io.github.io` par le nouveau domaine dans
   tous les fichiers listés plus haut (le `grep` ci-dessus les trouve tous),
   y compris la constante `BASE` en tête de `outils/verifier.py`
