import {chromium} from '@playwright/test';
import {resolve} from 'node:path';
const b=await chromium.launch({channel:'chrome',headless:true});
try {
const p=await b.newPage({viewport:{width:1440,height:690},deviceScaleFactor:1.5});
await p.goto('http://127.0.0.1:4173');
const snap=async name=>{await p.waitForTimeout(100);await p.screenshot({path:resolve('reports/assets/'+name+'.png')})};
await snap('overview-wide');
await p.getByRole('button',{name:'Connect your account'}).click();
await p.locator('[role="dialog"]').screenshot({path:resolve('reports/assets/auth-login.png')});
await p.getByRole('button',{name:'New here? Create an account'}).click();
await p.locator('[role="dialog"]').screenshot({path:resolve('reports/assets/auth-register.png')});
await p.getByRole('button',{name:'Close dialog'}).click();
await p.getByRole('button',{name:'Start today’s revision'}).click();
await p.locator('[role="dialog"]').screenshot({path:resolve('reports/assets/recall-hidden.png')});
await p.getByRole('button',{name:'Close dialog'}).click();
for (const [nav,name] of [['My problems','library-wide'],['Revision queue','queue-wide'],['Analytics','analytics-wide'],['Settings','settings-wide'],['Mistake notebook','notebook-wide']]) {
await p.goto('http://127.0.0.1:4173/#'+encodeURIComponent(nav));await snap(name);
}
await p.getByRole('button',{name:'Revision notifications'}).click();await snap('notifications-wide');
console.log('Captured updated report figures.');
}finally{await b.close()}
