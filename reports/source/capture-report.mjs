import {chromium} from '@playwright/test';
import {resolve} from 'node:path';
const browser=await chromium.launch({channel:'chrome',headless:true});
try{
 const page=await browser.newPage({viewport:{width:1360,height:1050},deviceScaleFactor:1.5});
 await page.goto('http://127.0.0.1:4173');
 await page.getByRole('heading',{name:'A little better, every day.'}).waitFor();
 await page.screenshot({path:resolve('reports/assets/dashboard.png')});
 await page.getByRole('button',{name:'Connect your account'}).click();
 await page.screenshot({path:resolve('reports/assets/login.png')});
 await page.getByRole('button',{name:'Close dialog'}).click();
 await page.getByRole('button',{name:'Add problem',exact:true}).click();
 await page.getByLabel('Problem title').fill('Best Time to Buy and Sell Stock');
 await page.getByLabel('Problem URL').fill('https://leetcode.com/problems/best-time-to-buy-and-sell-stock/');
 await page.getByLabel('Your approach').fill('Track the minimum price seen so far and the largest profit at each subsequent price. Time O(n), space O(1).');
 await page.getByRole('textbox',{name:'Mistake or lesson'}).fill('Buy before selling. Update profit only using prices already seen.');
 await page.screenshot({path:resolve('reports/assets/add-problem.png')});
 await page.getByRole('button',{name:'Close dialog'}).click();
 await page.getByRole('button',{name:'Start today’s revision'}).click();
 await page.getByRole('button',{name:'Reveal my approach'}).click();
 await page.screenshot({path:resolve('reports/assets/recall-session.png')});
 await page.getByRole('button',{name:'Close dialog'}).click();
 await page.getByRole('button',{name:'Analytics',exact:true}).click();
 await page.screenshot({path:resolve('reports/assets/analytics.png')});
 await page.getByRole('button',{name:'Mistake notebook',exact:true}).click();
 await page.screenshot({path:resolve('reports/assets/notebook.png')});
 console.log('Captured six project screenshots.');
}finally{await browser.close()}
