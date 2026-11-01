// Install development dependencies: npm ci --ignore-scripts
// Render: npm run render:math -- [relative-html-file ...]
// Edit the data-tex attribute, preserve the <!--/math--> marker, then rerun.
const fs = require('node:fs');
const path = require('node:path');
const katex = require('katex');

const root = path.resolve(__dirname, '..');
const version = '0.19.1';
if (katex.version !== version) throw new Error(`Expected KaTeX ${version}, got ${katex.version}`);
const decodeAttribute = value => value.replace(/&(amp|lt|gt|quot|apos|#\d+|#x[\da-f]+);/gi, (_, entity) => {
  const named = { amp: '&', lt: '<', gt: '>', quot: '"', apos: "'" };
  if (entity[0] !== '#') return named[entity.toLowerCase()];
  return String.fromCodePoint(entity[1].toLowerCase() === 'x' ? parseInt(entity.slice(2), 16) : Number(entity.slice(1)));
});

for (const file of process.argv.slice(2).length ? process.argv.slice(2) : ['puzzles.html', 'note-pac-bayes.html', 'note-sequential.html', 'note-denoising.html', 'note-floor-series.html', 'note-off-policy.html', 'note-rare-events.html', 'note-adaptive-calibration.html']) {
  const target = path.resolve(root, file);
  if (!target.startsWith(root + path.sep) || !target.endsWith('.html')) throw new Error('Use an HTML file inside the site.');
  const source = fs.readFileSync(target, 'utf8');
  let count = 0;
  const rendered = source.replace(/<(span|div)(\s[^>]*\bdata-tex="([^"]*)"[^>]*)>[\s\S]*?<!--\/math--><\/\1>/g,
    (_, tag, attributes, encodedTex) => {
      const displayMode = /\bdata-display="true"/.test(attributes);
      const html = katex.renderToString(decodeAttribute(encodedTex), {
        displayMode, output: 'htmlAndMathml', throwOnError: true, strict: 'error', trust: false,
      });
      count++;
      return `<${tag}${attributes}>${html}<!--/math--></${tag}>`;
    });
  const expected = (source.match(/\bdata-tex=/g) || []).length;
  if (count !== expected) throw new Error(`${file}: found ${expected} math sources but rendered ${count}; check wrappers and markers.`);
  if (rendered !== source) fs.writeFileSync(target, rendered);
  console.log(`${file}: ${count} expressions rendered with KaTeX ${version}.`);
}

const packageRoot = path.dirname(require.resolve('katex/package.json'));
const assets = path.join(root, 'assets', 'katex');
fs.mkdirSync(assets, { recursive: true });
fs.copyFileSync(path.join(packageRoot, 'dist', 'katex.min.css'), path.join(assets, 'katex.min.css'));
fs.cpSync(path.join(packageRoot, 'dist', 'fonts'), path.join(assets, 'fonts'), { recursive: true });
fs.copyFileSync(path.join(packageRoot, 'LICENSE'), path.join(assets, 'LICENSE.txt'));
fs.writeFileSync(path.join(assets, 'VERSION.txt'), `KaTeX ${version}\nhttps://katex.org/\n`);
