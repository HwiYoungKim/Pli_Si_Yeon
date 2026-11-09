import asyncio
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--no-sandbox'])
        pg=await b.new_page(viewport={'width':1340,'height':720},device_scale_factor=2)
        await pg.goto('file:///home/claude/build/nav.html'); await pg.wait_for_timeout(400)
        await pg.locator('#s').screenshot(path='/home/claude/build/nav.png'); await b.close()
asyncio.run(main())
