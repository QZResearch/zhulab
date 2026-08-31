# Zhu Group website

Hugo + [Blowfish](https://blowfish.page). The homepage uses Blowfish's
`custom` layout, so the whole thing is driven by our own partial rather than
one of the built-in layouts.

## Running it

Blowfish needs **Hugo extended ≥ 0.162.0**.

```bash
brew install hugo          # or: brew upgrade hugo
hugo server -D             # http://localhost:1313
hugo --gc --minify         # production build into public/
```

Set the real `baseURL` in `config/_default/hugo.toml` before deploying.

## Homepage anatomy

`layouts/partials/home/custom.html` renders, top to bottom:

| # | Section | Edit it here |
|---|---------|--------------|
| 1 | Hero (eyebrow, title, lead, buttons, background image) | front matter of `content/_index.md` + `assets/img/hero.jpg` |
| 2 | Intro paragraphs | markdown body of `content/_index.md` |
| 3 | Research area cards (max 4) | pages in `content/research/` — sorted by `weight` |
| 4 | Latest news (max 4) | pages in `content/news/` — newest first |
| 5 | Selected publications (max 4) | `data/publications.yaml`, entries with `featured: true` |
| 6 | The group (max 6) | pages in `content/team/` |
| 7 | "We are recruiting" banner | `join:` block in `content/_index.md` front matter |

Any section with no content simply disappears — delete `content/news/` and the
News block stops rendering.

## Where things live

```
config/_default/     site config: hugo.toml, params.toml, menus.en.toml, languages.en.toml
content/             pages: _index.md (home), research/, news/, publications/, team/, gallery/, join/
static/              favicon set — copied to the site root, overrides the theme's
publications.bib     your BibTeX export — the source of truth for papers
data/                publications.yaml (generated from publications.bib)
scripts/             sync_publications.py, make_favicons.py
assets/css/          custom.css   <- all the yu-* styles used by the homepage
assets/img/          hero.jpg, logo.png, people/
layouts/partials/home/custom.html   the homepage itself
layouts/team/                       list.html (the team page), single.html (a profile)
layouts/gallery/                    list.html (album index), single.html (one album)
assets/js/                          gallery-lightbox.js
layouts/partials/yu/                publication.html, person.html, button.html, team-groups.html
layouts/shortcodes/                 {{< publications >}}
themes/blowfish/     the theme (git clone; don't edit in here)
```

## A note on placeholder text

Everything in `content/` is text a visitor reads, so instructions to *you* live
in HTML comments (`<!-- ... -->`) rather than in the prose — they show when you
edit the file and never render on the page. If you add your own reminders, do
the same.

## Common edits

**Add a paper** — put it in `publications.bib` and run the sync script
(see *Publications from BibTeX* below). It appears on `/publications/`
automatically, grouped by year. Add `featured: true` in the generated YAML to
put it on the homepage. Names listed in `groupAuthors` (in `params.toml`) are
highlighted in every author list.

**Add a person** — create `content/team/<slug>/index.md`. Every member gets
their own profile page at `/team/<slug>/`, and the tiles on the homepage and on
`/team/` link to it. Front matter:

```yaml
title:  "Dr Jane Doe"          # displayed name
role:   "Research fellow"      # shown under the name
group:  "Postdoctoral researchers"   # heading they appear under
weight: 10                     # order within the group
avatar: "jane.jpg"             # a file sitting next to index.md; omit for a letter avatar
avatarAnchor: "Top"            # optional: Top (default) | Center | Smart | Bottom
supervisors:                   # co-supervision; `url` and `org` optional
  - name: "Dr Qiang Zhu"
    url:  "/team/qiang-zhu/"
  - name: "Prof. Haibo Yu"
    org:  "School of Chemistry & Molecular Bioscience, UOW"
    url:  "https://scholars.uow.edu.au/..." 
pubName: "J. Doe"              # matched against data/publications.yaml to build their paper list
email:  "jane@uow.edu.au"
office: "Building 18, Room 2.15"
interests: ["...", "..."]      # right-hand sidebar
experience:                    # positions held, newest first
  - role:  "Research Fellow"
    org:   "University of Wollongong"
    years: "2024 – present"
    note:  "optional extra line"
education:                     # same shape, but `degree:` instead of `role:`
  - degree: "PhD in Computational Chemistry"
    org:    "Nanjing University"
    years:  "2020"
awards:                        # optional, same shape
  - role:  "Award name"
    org:   "Awarding body"
    years: "2025"
links:
  - name: "Google Scholar"
    url:  "https://..."
    icon: "google-scholar"     # any file in themes/blowfish/assets/icons/
alumni: true                   # optional — hides them from the homepage tiles
```

The markdown body below the front matter is the bio. Group headings are ordered
by `teamGroups` in `params.toml`.

### Portraits

The photo goes **inside the person's own folder**, next to their `index.md`:

```
content/team/qiang-zhu/
├── index.md
└── portrait.jpg      <- avatar: "portrait.jpg"
```

It is a page resource, so the filename in `avatar:` is relative to that folder —
no path, no leading slash. Anything Hugo can read works (jpg, png, webp).

Upload it at full size; Hugo generates a 520px crop for the profile page and a
260px one for the tiles, and never touches your original. Around 800px on the
short edge is plenty. The tile is a circle, so a head-and-shoulders shot frames
best.

Both crops are square and anchored at the **top**, which keeps the head on a
portrait-orientation photo. If a particular photo crops badly, add
`avatarAnchor: "Center"` (or `"Smart"`, `"Bottom"`, `"Left"`, `"Right"`) to that
person's front matter. `Smart` lets Hugo pick the region it thinks is most
interesting — good on some photos, wrong on others, so treat it as a fallback
rather than the default.

Leave `avatar` empty and an initial-letter avatar is drawn instead.

### Hiding a group

A group heading only appears if someone is in it, so the usual way to get rid of
**Masters & honours** or **Alumni** is simply to have nobody in them.

To hide a group that *does* have members, name it in `params.toml`:

```toml
hiddenTeamGroups = ["Masters & honours", "Alumni"]
```

That drops it from `/team/` and the homepage. The people's own profile pages are
still built and still reachable by URL — add `draft: true` to a person's front
matter to remove that too.

`supervisors` renders first in the sidebar under the heading **Supervised by**,
so co-supervision is visible without hunting through the bio. A `url` starting
with `/` links to a profile on this site; a full `https://` URL opens in a new
tab, which is what you want for someone outside the group. Leave the field out
on people it doesn't apply to and the heading disappears.

`interests`, `experience`, `education` and `awards` each render as a block in
the right-hand sidebar, and each is skipped entirely if you leave it out. Every
one accepts either plain strings (`- "PhD in Chemistry, Nanjing University,
2020"`) or the structured form above, which sets the role in bold, the place
underneath in grey, and the dates small below that. Mix and match freely — the
two forms can even appear in the same list.

**Add an album** — create `content/gallery/<slug>/`, drop the photos in beside
an `index.md`, and it appears on `/gallery/` automatically. Front matter:

```yaml
title:   "Group retreat, Kiama"
date:    2026-07-04
summary: "One line for the album card."
cover:   "photo-01.jpg"       # optional; defaults to the first image
captions:                     # optional, per file
  photo-01.jpg: "Somebody explaining why the mapping matters"
```

Photos are used in filename order, so name them `photo-01.jpg`, `photo-02.jpg`
and so on — or list them explicitly with an `images:` array to control the
order. Hugo resizes them at build time, so upload straight off the camera or
phone; don't shrink them first. The grid shows square crops and clicking one
opens the full uncropped photo in a lightbox with arrow-key navigation.

**Add news** — a new markdown file in `content/news/` with a `date`.

**Add a research area** — a new markdown file in `content/research/` with
`summary`, `weight`, and `icon`. Icon names come from
`themes/blowfish/assets/icons/` (e.g. `code`, `globe`, `lightbulb`,
`graduation-cap`, `wand-magic-sparkles`).

**Change the colours** — `colorScheme` in `params.toml`. The custom CSS is
written against the theme's colour variables, so the homepage follows along.

## Publications from BibTeX

The site reads `data/publications.yaml`, but you don't write that file by hand
— it is generated from `publications.bib`:

```bash
pip install pyyaml                        # once
python3 scripts/sync_publications.py
```

Export the `.bib` from Zotero (right-click a collection → Export → BibTeX),
EndNote, or your Google Scholar profile, replace `publications.bib`, and
run the script. It **merges** rather than overwrites:

- fields it manages — `title`, `authors`, `journal`, `volume`, `pages`, `year`,
  `doi`, `url` — are refreshed from the `.bib`
- anything you added by hand — `featured`, `tags`, `code`, `pdf` — is matched to
  the paper by DOI and preserved
- papers already in the YAML but missing from the `.bib` are **kept**, and
  listed in the output with a `!` so you can decide what to do

It handles the usual BibTeX awkwardness: LaTeX accents (`M{\"u}ller` → Müller),
either author order (`Zhu, Qiang` or `Qiang Zhu`), surname particles
(`van der Waals`), `others` → *et al.*, `--` → en dash, and DOIs given as full
URLs. Author names are shortened to `Q. Zhu` form to match the site's style.

`--check` exits non-zero if the YAML is out of date, which is what CI uses.

### Automation

`.github/workflows/publications.yml` runs the script and opens a pull request
whenever `publications.bib` changes on the default branch. It also runs
monthly and on demand from the Actions tab — though since the `.bib` is
something you update yourself, the push trigger is the one that does the work.

If you would rather it fetched papers automatically instead, the script is easy
to repoint at OpenAlex or Crossref by ORCID; ask and I'll wire that up. Google
Scholar has no official API, so that one isn't an option.

## The browser-tab icon

`static/` holds the favicon set. Hugo copies that folder to the site root and
site files beat theme files, so the icons there are what a browser shows —
Blowfish already links the standard names from every page.

To restyle, edit `GLYPH` and the three colours at the top of
`scripts/make_favicons.py` and re-run it:

```bash
pip install pillow
python3 scripts/make_favicons.py
```

It writes the tab icons (16/32, a multi-size `.ico`, and an SVG that stays
crisp at any size), the iOS and Android home-screen icons, `site.webmanifest`,
and a matching `assets/img/logo.png`. The design is a single bold letter on
purpose — at 16 pixels anything more detailed turns to mush.

**Browsers cache favicons very aggressively** — harder than any other asset,
and `hugo server` will not clear that for you. After changing the icon, bump
`faviconVersion` in `config/_default/params.toml`:

```toml
faviconVersion = "2"
```

`layouts/partials/favicons.html` appends that as `?v=` to every icon URL, which
is what actually forces a refetch. A hard reload (Cmd/Ctrl+Shift+R) usually
works too, but the version bump is the one that fixes it for everyone else.

To also show the logo in the site header instead of the text "Zhu Group",
uncomment `logo = "img/logo.png"` in `config/_default/languages.en.toml`.

## Deploying to GitHub Pages

The theme is a git submodule, and `.github/workflows/deploy.yml` builds and
publishes on every push to `main`.

**One-time setup**

```bash
git add -A
git commit -m "Initial commit: Zhu Group website"
git branch -M main
git remote add origin https://github.com/YOUR-ORG/YOUR-REPO.git
git push -u origin main
```

Then on GitHub: **Settings → Pages → Build and deployment → Source = GitHub
Actions**. That is the step people forget; without it the workflow builds and
then fails to publish.

The site lands at `https://YOUR-ORG.github.io/YOUR-REPO/`. The workflow reads
that URL from the Pages configuration and passes it to Hugo as `--baseURL`, so
you never hard-code the subpath.

**Cloning it elsewhere** — the theme is a submodule, so a plain `git clone`
gives you an empty `themes/blowfish`:

```bash
git clone --recurse-submodules https://github.com/YOUR-ORG/YOUR-REPO.git
# already cloned? git submodule update --init --recursive
```

**Updating the theme**

```bash
git submodule update --remote themes/blowfish
git commit -am "Update Blowfish"
```

## Deploying elsewhere

Static output, so GitHub Pages, Netlify or Cloudflare Pages all work. Note
`themes/blowfish/` is a plain clone — either commit it, or convert it to a
submodule (`git submodule add https://github.com/nunocoracao/blowfish.git themes/blowfish`)
and make sure your CI checks out submodules.
