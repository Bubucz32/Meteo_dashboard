const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Seznam vašich HTML stránek a název výstupního obrázku
const PAGES = [
  { html: 'stranka1.html', output: 'stranka1.png' },
  { html: 'stranka2.html', output: 'stranka2.png' }
];

(async () => {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  // Rozlišení pro 7.4" E-Paper (800 x 480 px)
  await page.setViewport({ width: 800, height: 480 });

  if (!fs.existsSync('out')) {
    fs.mkdirSync('out');
  }

  for (const item of PAGES) {
    const filePath = `file://${path.join(__dirname, item.html)}`;
    console.log(`Renderuji: ${item.html}...`);
    
    await page.goto(filePath, { waitUntil: 'networkidle0' });
    await page.screenshot({ path: `out/${item.output}` });
  }

  await browser.close();
})();
