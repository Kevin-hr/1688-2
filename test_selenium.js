const { Builder, By, until } = require('selenium-webdriver');
const chrome = require('selenium-webdriver/chrome');
const undetected = require('undetected-chrome-drive');

async function main() {
  console.log('Setting up undetected Chrome...');

  const driver = await undetected();

  console.log('Navigating to urlebird.com...');
  await driver.get('https://urlebird.com/');

  // Wait for page to load
  await driver.wait(until.elementLocated(By.css('body')), 30000);

  console.log('Page loaded!');
  console.log('Title:', await driver.getTitle());
  console.log('URL:', await driver.getCurrentUrl());

  await driver.quit();
}

main().catch(console.error);
