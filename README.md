# Mohammad Pouya Toroghi — academic website

A static, responsive academic website at **https://pouyatoroghi.github.io/**. Fourteen separate HTML pages share `styles.css` and a small `theme.js` script. Publishing and browsing require no build step or package installation. Fonts and mathematical typesetting assets are hosted locally, with no framework, CDN, analytics, or paid hosting dependency.

The theme follows the system preference until a visitor chooses **Light** or **Dark**; that choice persists across pages and visits when browser storage is available. Puzzle hints and solutions use native HTML disclosures and work without JavaScript. With JavaScript disabled, all pages remain readable and the theme follows the system preference.

At desktop widths of 1200px and above, a sticky full-width masthead keeps the name and description visible, with compact unshaded navigation on the left and a quiet contents column on the right. Both navigation columns remain below the header while scrolling. The unframed layout fills the browser width and at least its height, with shared gutters for all text. Smaller screens use compact navigation below the sticky identity header and above a single content column. Header height is measured so anchors remain visible after resizing or font loading. Section links are static HTML and work without JavaScript; update the corresponding `.page-outline` links when changing headings.

## Preview

Double-click `index.html` to open the website locally. Content, styling, navigation, and the CV work without a server. For an HTTP preview, including consistent theme storage across pages, run `python -m http.server 4173 --bind 127.0.0.1` in this folder and open http://127.0.0.1:4173/.

## Repository and publishing

This folder is connected to the existing [pouyatoroghi/pouyatoroghi.github.io](https://github.com/pouyatoroghi/pouyatoroghi.github.io) repository. Its existing commit history is preserved. Website updates belong only in this repository.

The repository is public. GitHub Pages uses the custom `.github/workflows/pages.yml` workflow to publish the static website from the root of **main** at **https://pouyatoroghi.github.io/**. Each push to main triggers publication; the workflow can also be run manually. It packages the HTML pages, stylesheet, theme script, and assets without rebuilding mathematics or installing packages. Concurrent deployments are serialized. The Actions tab shows deployment progress.

To push a later update, use the commands below from this website folder. No framework, package installation, build command, custom domain, or CNAME file is required. The `.nojekyll` file makes GitHub Pages serve the static files directly.

GitHub documentation: [custom Pages workflows](https://docs.github.com/en/pages/getting-started-with-github-pages/using-custom-workflows-with-github-pages).

## Update the site

- **About, research interests, contact:** edit `index.html`.
- **Research contributions and six PhD directions:** edit `research.html`.
- **Studies and projects in inference, search, decisions, and representation:** edit `projects.html`.
- **Mathematical preparation, education, teaching, honors:** edit `background.html`.
- **Mathematical notebook:** edit `notes.html` for the index; `note-pac-bayes.html`, `note-sequential.html`, `note-denoising.html`, and `note-floor-series.html` contain the full derivations. The original handwritten page is `assets/handwritten-floor-series.jpg`.
- **Applied probability problems:** `note-off-policy.html` derives policy-evaluation bias, variance, and a coverage lower bound; `note-rare-events.html` derives a rare-event estimator and its asymptotic efficiency; `note-adaptive-calibration.html` develops a matrix confidence bound and its implications for sensor experiments. Run `python scripts/check-probability.py` to reproduce their deterministic numerical checks using only the Python standard library.
- **Puzzles, hints, solutions:** edit `puzzles.html`; preserve the `<details>` and `<summary>` structure. See the mathematical typesetting instructions below when changing an expression.
- **Four long-term research questions and related reading:** edit `question.html`.
- **Colors, typography, spacing, responsive layouts:** edit `styles.css`. After changing it, update the `styles.css?v=...` revision in every HTML page so returning browsers request the new stylesheet.
- **Theme selection, persistence, and sticky-header offsets:** edit `theme.js`; update its revision in every HTML page after changes.
- **Fonts:** Source Sans 3 and Source Serif 4 are bundled in `assets/fonts/` with their SIL Open Font License notices. Keep those notices when redistributing the font files.
- **CV:** replace `assets/CV_Toroghi_Oct2026.pdf`. If you rename it, update CV links across all HTML pages.
- **Social preview:** the editable design is `assets/social-preview.svg`; `assets/social-preview.png` is the exported image used by sharing services. Update both when changing the preview text.
- **Dates and research status:** update the footer, availability text, and affected research entries as circumstances change.

Navigation, footer, and page metadata are written directly in each HTML file; update every affected page when changing shared information.

Push later changes from this folder:

```powershell
git add index.html research.html projects.html background.html notes.html note-*.html puzzles.html question.html styles.css theme.js assets scripts package.json package-lock.json .nojekyll .gitignore README.md
git commit -m "Update academic website"
git push origin main
```

## Mathematical typesetting

Puzzles and mathematical notes contain LaTeX source in `data-tex` attributes and pre-rendered KaTeX HTML with accessible MathML. They display immediately, work without JavaScript, and use bundled fonts in `assets/katex/`. Keep the accompanying license notices. The default rendering command processes all eight pages containing mathematics; a filename argument renders only that page.

To change a formula, edit its `data-tex` value and preserve the `<!--/math-->` closing marker. Escape attribute-sensitive characters as HTML entities, such as `&lt;` for a less-than sign. With Node.js 22.12 or later, regenerate the typeset output from this folder:

```powershell
npm ci --ignore-scripts
npm run render:math
```

The pinned KaTeX development dependency is needed only for regenerating mathematics. Commit the changed HTML and any changed vendored assets afterward; GitHub Pages serves the generated files directly.

## Content notes

The October 2026 CV supplies the factual record of education, research, projects, teaching, and honors. Mathematical preparation is supported by teaching responsibilities and studies in inference, search, constraint solving, and learning. The prose explains connections and interests rather than reproducing CV bullet points. Ongoing work remains distinct from completed undergraduate research. Both current projects are manuscripts in preparation for planned ICML submission, as confirmed by the owner on November 1, 2026; neither is represented as submitted or accepted.

The homepage prioritizes verified mathematical teaching responsibilities and academic evidence, with direct links to two expository notes. The Questions page develops the owner's stated ambitions through calibrated search, reusable abstractions and discovery, reliable adaptation, and controlled model revision. These and the six PhD directions are prospective interests, not completed results or claims of original theoretical discoveries. Papers under **Related reading** are references by other researchers, not the owner's publications. No publications, accepted papers, research metrics, or project repositories have been invented.

The mathematical notebook distinguishes the owner's supplied handwritten floor-series calculation from newly prepared expositions of established probability results. The three probability notes derive a PAC-Bayes generalization bound, a Gaussian-mixture confidence sequence, and Gaussian denoising identities. Their worked numerical examples illustrate the mathematics; they are not research experiments or claims of novel results. The photograph is an unchanged copy of the supplied image, accompanied by a complete typeset derivation. No probabilistic reinterpretation of that integral is included.

The three applied analyses now lead the notebook. They use explicit recommendation-session, detector-noise, and sensor-calibration models. Their numbers are analytical or finite-model checks, not results from the owner's research projects or real deployments. The rare-event draw-count comparison concerns relative RMSE under the stated model, not a measured runtime or a confidence-interval guarantee. The older introductory derivations remain available under Supporting derivations.

The downloadable PDF is an unchanged copy of the supplied CV and includes the owner's phone number. It is publicly accessible; replace it with a revised public version if the contact details should change.

The Actions workflow publishes `scripts/check-probability.py` with the static pages and runs it before deployment so the public reproduction links stay usable.

A Git push updates the repository. The public site updates only after a successful GitHub Pages deployment.

## Local verification

The ignored `.qa` directory contains local checks and screenshots. With the HTTP preview running on port 4173, run `node .qa/multipage.cjs` from this folder. This optional check needs Node.js and Playwright with Chromium; the script uses the bundled Codex Playwright path, or a module path supplied through `PLAYWRIGHT_PATH`. These tools are not needed to publish or use the site.

## Design references

The redesign uses the direct biography, visible research descriptions, and immediate contact links typical of academic homepages. References included [Aleksander Madry](https://madry.mit.edu/), [Jacob Steinhardt](https://jsteinhardt.stat.berkeley.edu/), and the indexed content of [Chelsea Finn's homepage](https://ai.stanford.edu/~cbfinn/). Their text, photographs, and source code are not reused. No portrait is included, as requested.
