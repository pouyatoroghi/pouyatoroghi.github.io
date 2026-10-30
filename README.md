# Mohammad Pouya Toroghi — academic website

A static, responsive academic website at **https://pouyatoroghi.github.io/**. Six separate HTML pages share `styles.css` and a small `theme.js` script. Publishing and browsing require no build step or package installation. Fonts and mathematical typesetting assets are hosted locally, with no framework, CDN, analytics, or paid hosting dependency.

The theme follows the system preference until a visitor chooses **Light** or **Dark**; that choice persists across pages and visits when browser storage is available. Puzzle hints and solutions use native HTML disclosures and work without JavaScript. With JavaScript disabled, all pages remain readable and the theme follows the system preference.

## Preview

Double-click `index.html` to open the website locally. Content, styling, navigation, and the CV work without a server. For an HTTP preview, including consistent theme storage across pages, run `python -m http.server 4173 --bind 127.0.0.1` in this folder and open http://127.0.0.1:4173/.

## Repository and publishing

This folder is connected to the existing [pouyatoroghi/pouyatoroghi.github.io](https://github.com/pouyatoroghi/pouyatoroghi.github.io) repository. Its existing commit history is preserved. Website updates belong only in this repository.

The repository is public and GitHub Pages publishes the **main** branch from **/(root)** at **https://pouyatoroghi.github.io/**. The Actions tab shows deployment progress after each push.

To push a later update, use the commands below from this website folder. No framework, package installation, build command, custom domain, or CNAME file is required. The `.nojekyll` file makes GitHub Pages serve the static files directly.

GitHub documentation: [publishing from a branch](https://docs.github.com/en/pages/getting-started-with-github-pages/configuring-a-publishing-source-for-your-github-pages-site).

## Update the site

- **About, research interests, contact:** edit `index.html`.
- **Research contributions and six PhD directions:** edit `research.html`.
- **Studies and projects in inference, search, decisions, and representation:** edit `projects.html`.
- **Mathematical preparation, education, teaching, honors:** edit `background.html`.
- **Puzzles, hints, solutions:** edit `puzzles.html`; preserve the `<details>` and `<summary>` structure. See the mathematical typesetting instructions below when changing an expression.
- **Four long-term research questions and related reading:** edit `question.html`.
- **Colors, typography, spacing, responsive layouts:** edit `styles.css`.
- **Theme selection and persistence:** edit `theme.js`.
- **Fonts:** Source Sans 3 and Source Serif 4 are bundled in `assets/fonts/` with their SIL Open Font License notices. Keep those notices when redistributing the font files.
- **CV:** replace `assets/CV_Toroghi_Oct2026.pdf`. If you rename it, update CV links across all six HTML pages.
- **Social preview:** the editable design is `assets/social-preview.svg`; `assets/social-preview.png` is the exported image used by sharing services. Update both when changing the preview text.
- **Dates and research status:** update the footer, availability text, and affected research entries as circumstances change.

Navigation, footer, and page metadata are written directly in each HTML file; update every affected page when changing shared information.

Push later changes from this folder:

```powershell
git add index.html research.html projects.html background.html puzzles.html question.html styles.css theme.js assets scripts package.json package-lock.json .nojekyll .gitignore README.md
git commit -m "Update academic website"
git push origin main
```

## Mathematical typesetting

Puzzles contain LaTeX source in `data-tex` attributes and pre-rendered KaTeX HTML with accessible MathML. They display immediately, work without JavaScript, and use bundled fonts in `assets/katex/`. Keep the accompanying license notices.

To change a formula, edit its `data-tex` value and preserve the `<!--/math-->` closing marker. Escape attribute-sensitive characters as HTML entities, such as `&lt;` for a less-than sign. With Node.js 22.12 or later, regenerate the typeset output from this folder:

```powershell
npm ci --ignore-scripts
npm run render:math
```

The pinned KaTeX development dependency is needed only for regenerating mathematics. Commit the changed HTML and any changed vendored assets afterward; GitHub Pages serves the generated files directly.

## Content notes

The October 2026 CV supplies the factual record of education, research, projects, teaching, and honors. Mathematical preparation is supported by teaching responsibilities and studies in inference, search, constraint solving, and learning. The prose explains connections and interests rather than reproducing CV bullet points. Ongoing work remains distinct from completed undergraduate research.

The Questions page develops the owner's stated ambitions through calibrated search, reusable abstractions and discovery, reliable adaptation, and controlled model revision. These and the six PhD directions are prospective interests, not completed results or claims of original theoretical discoveries. Papers under **Related reading** are references by other researchers, not the owner's publications. No publications, accepted papers, research metrics, or project repositories have been invented.

The downloadable PDF is an unchanged copy of the supplied CV and includes the owner's phone number. It is publicly accessible; replace it with a revised public version if the contact details should change.

A Git push updates the repository. The public site updates only after a successful GitHub Pages deployment.

## Local verification

The ignored `.qa` directory contains local checks and screenshots. With the HTTP preview running on port 4173, run `node .qa/multipage.cjs` from this folder. This optional check needs Node.js and Playwright with Chromium; the script uses the bundled Codex Playwright path, or a module path supplied through `PLAYWRIGHT_PATH`. These tools are not needed to publish or use the site.

## Design references

The redesign uses the direct biography, visible research descriptions, and immediate contact links typical of academic homepages. References included [Aleksander Madry](https://madry.mit.edu/), [Jacob Steinhardt](https://jsteinhardt.stat.berkeley.edu/), and the indexed content of [Chelsea Finn's homepage](https://ai.stanford.edu/~cbfinn/). Their text, photographs, and source code are not reused. No portrait is included, as requested.
