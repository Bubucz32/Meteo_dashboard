const puppeteer = require('puppeteer');
const path = require('path');
const fs = require('fs');

// Seznam stránek s definovanou orientací
const PAGES = [
  // Varianta na šířku (800x480)
  { html: 'index.html', output: 'index_landscape.png', width: 480, height: 800 },
  { html: 'index_dark.html', output: 'index_dark_landscape.png', width: 480, height: 800 },

  // Varianta na výšku (480x800)
//  { html: 'index_portrait.html', output: 'index_portrait.png', width: 480, height: 800 },
  //{ html: 'index_dark_portrait.html', output: 'index_dark_portrait.png', width: 480, height: 800 }
];

(async () => {
  const browser = await puppeteer.launch({
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  const page = await browser.newPage();

  if (!fs.existsSync('out')) {
    fs.mkdirSync('out');
  }

  for (const item of PAGES) {
    console.log(`Renderuji: ${item.html} (${item.width}x${item.height})...`);

    await page.setViewport({
      width: item.width,
      height: item.height,
      deviceScaleFactor: 1
    });

    const filePath = `file://${path.join(__dirname, item.html)}`;
    await page.goto(filePath, { waitUntil: 'networkidle0' });

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
