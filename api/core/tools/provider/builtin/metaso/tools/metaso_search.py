import asyncio
import hashlib
import random
from typing import Any, Union

from playwright.async_api import async_playwright

from core.tools.entities.tool_entities import ToolInvokeMessage
from core.tools.tool.builtin_tool import BuiltinTool
from extensions.ext_redis import redis_client


async def searchMetaso(query):
    md5 = hashlib.md5()
    md5.update(query.encode('utf-8'))
    query_md5 = md5.hexdigest()
    key = f"metaso_search_{query_md5}"
    result = redis_client.get(key)
    if result:
        return result
    async with async_playwright() as p:
        # 启动 Chromium 浏览器
        # browser = await p.chromium.launch(headless=False)  # headless=False 用于打开浏览器界面
        browser = await p.chromium.launch(
            executable_path="/Applications/Google Chrome.app/Contents/MacOS/Google Chrome",  # 替换为你的 Chrome 可执行文件路径
            headless=True,  # 使用非无头模式，以便看到浏览器界面
        )
        page = await browser.new_page()

        await page.goto('https://metaso.cn/')
        await page.click("//button[contains(text(), '登录/注册')]")
        await page.click('circle[fill="#47B881"]')
        await page.fill('input[placeholder="输入邮箱/手机号"]', '13051597970')
        await asyncio.sleep(random.randint(0, 1000) / 1000)
        await page.fill('input[placeholder="输入登录密码"]', 'cjwmetaso6M!!')
        await asyncio.sleep(random.randint(0, 1000) / 1000)
        await page.click('input[id="desktop-login-policy"]')
        await asyncio.sleep(random.randint(0, 1000) / 1000)
        await page.click("//button[contains(text(), '登 录')]")
        await asyncio.sleep(random.randint(0, 1000) / 1000)

        await page.goto('https://metaso.cn/')
        await page.fill('textarea[placeholder="请输入，Enter键发送，Shift+Enter键换行"]', query)
        await page.click('textarea[placeholder="请输入，Enter键发送，Shift+Enter键换行"]')
        await asyncio.sleep(random.randint(0, 1000) / 1000)
        await page.type('textarea[placeholder="请输入，Enter键发送，Shift+Enter键换行"]', ' ')
        await page.keyboard.press('Enter')
        await page.wait_for_selector("//button[contains(text(), '分享')]")
        await asyncio.sleep(random.randint(0, 2000) / 1000)
        content = await page.inner_text('div[class="markdown-body MuiBox-root css-0"]')
        redis_client.set(key, content, ex=3600 * 24)

        # 操作完成，关闭浏览器
        await browser.close()
    return content


class MetasoSearchTool(BuiltinTool):
    def _invoke(self, user_id: str, tool_parameters: dict[str, Any],
        ) -> Union[ToolInvokeMessage, list[ToolInvokeMessage]]:
        """
            invoke tools
        """
        print(tool_parameters)
        query = tool_parameters['query']
        # TODO: search with serpapi
        result_dict = {}
        asyncio.run(self._build_result(query, result_dict))

        return self.create_text_message(text=result_dict['content'])


    async def _build_result(self, query, result_dict):
        content = await searchMetaso(query)
        result_dict['content'] = content
