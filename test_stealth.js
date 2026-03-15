const puppeteer = require('puppeteer-extra');
const StealthPlugin = require('puppeteer-extra-plugin-stealth');
puppeteer.use(StealthPlugin());

(async () => {
  console.log('Launching browser...');
  const browser = await puppeteer.launch({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });
  console.log('Browser launched');

  const page = await browser.newPage();
  console.log('Navigating to urlebird.com...');

  await page.goto('https://urlebird.com/', { timeout: 90000, waitUntil: 'networkidle2' });

  console.log('Page loaded!');
  console.log('Title:', await page.title());
  console.log('URL:', page.url());

  await browser.close();
})();
