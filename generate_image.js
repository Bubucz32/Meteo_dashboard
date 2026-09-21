const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Pomocná funkce pro čekání
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

const PAGES = [
  { html: 'index.html', output: 'index_landscape.png', width: 800, height: 480 },
  { html: 'index_dark.html', output: 'index_dark_landscape.png', width: 800, height: 480 },
  { html: 'index_portrait.html', output: 'index_portrait.png', width: 480, height: 800 },
  { html: 'index_dark_portrait.html', output: 'index_dark_portrait.png', width: 480, height: 800 }
];

(async () => {
  const browser = await puppeteer.launch({
    args: [
      '--no-sandbox',
      '--disable-setuid-sandbox',
      '--allow-file-access-from-files' // Povolí CORS a síťové dotazy z file:// protokolu
    ]
  });
  const page = await browser.newPage();

  // Odchytávání výpisů z konzole přímo v HTML stránce
  page.on('console', msg => console.log('PROHLÍŽEČ LOG:', msg.text()));
  
  // Odchytávání nevychycených chyb v JavaScriptu na stránce
  page.on('pageerror', err => console.log('PROHLÍŽEČ CHYBA JS:', err.toString()));

  // Odchytávání selhaných síťových požadavků (např. Bad API Key, 404, CORS)
  page.on('requestfailed', request => {
    console.log(`PROHLÍŽEČ SÍŤ CHYBA: ${request.url()} - ${request.failure() ? request.failure().errorText : 'neznámá chyba'}`);
  });

  if (!fs.existsSync('out')) {
    fs.mkdirSync('out');
  }

  for (const item of PAGES) {
    if (!fs.existsSync(item.html)) continue;

    console.log(`Renderuji: ${item.html}...`);

    await page.setViewport({
      width: item.width,
      height: item.height,
      deviceScaleFactor: 1
    });

    const filePath = `file://${path.join(__dirname, item.html)}`;
    await page.goto(filePath, { waitUntil: 'load' });

    // Počkáme 4 sekundy na dokončení fetch() dotazů z Weather Underground
    await delay(4000);

    await page.screenshot({
      path: `out/${item.output}`,
      clip: {
        x: 0,
        y: 0,
        width: item.width,
        height: item.height
      }
    });
  }

  await browser.close();
})();
