const undetected_chromedriver = require('undetected-chromedriver');

async function main() {
  console.log('Launching undetected browser...');

  const driver = await undetected_chromedriver.default({
    headless: false,
    args: ['--no-sandbox', '--disable-setuid-sandbox']
  });

  console.log('Browser launched, navigating...');

  await driver.get('https://urlebird.com/');

  console.log('Page loaded!');
  console.log('Title:', await driver.getTitle());
  console.log('URL:', await driver.getCurrentUrl());

  await driver.quit();
}

main().catch(console.error);
