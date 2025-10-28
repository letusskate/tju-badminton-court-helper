# Quick Start Guide - WeChat H5 Browser Scraper

## 快速上手指南

### 1. 安装依赖

```bash
pip install -r requirements.txt
```

### 2. 最简单的使用方式

创建一个新的 Python 文件，比如 `my_scraper.py`：

```python
from wechat_scraper import WeChatBrowserScraper

# 使用上下文管理器（推荐）
with WeChatBrowserScraper() as scraper:
    # 打开你的微信 H5 页面
    scraper.open_url("https://your-wechat-h5-page.com")
    
    # 等待页面加载
    import time
    time.sleep(3)
    
    # 截图保存
    scraper.take_screenshot("wechat_page.png")
    
    # 获取页面源码
    html = scraper.get_page_source()
    print(f"页面 HTML 长度: {len(html)}")
```

### 3. 常见使用场景

#### 场景 1: 登录并访问需要认证的页面

```python
from wechat_scraper import WeChatBrowserScraper
from selenium.webdriver.common.by import By
import time

with WeChatBrowserScraper() as scraper:
    # 打开登录页
    scraper.open_url("https://your-login-page.com")
    
    # 等待并填写表单
    username_input = scraper.wait_for_element(By.ID, "username")
    password_input = scraper.wait_for_element(By.ID, "password")
    
    username_input.send_keys("your_username")
    password_input.send_keys("your_password")
    
    # 提交表单
    submit_btn = scraper.wait_for_element_clickable(By.ID, "submit")
    submit_btn.click()
    
    # 等待登录完成
    time.sleep(3)
    
    # 访问需要认证的页面
    scraper.open_url("https://your-authenticated-page.com")
```

#### 场景 2: 提取页面数据

```python
from wechat_scraper import WeChatBrowserScraper
from selenium.webdriver.common.by import By

with WeChatBrowserScraper() as scraper:
    scraper.open_url("https://your-wechat-h5-page.com")
    
    # 等待特定元素加载
    scraper.wait_for_element(By.CLASS_NAME, "content")
    
    # 使用标准 Selenium API 提取数据
    elements = scraper.driver.find_elements(By.CSS_SELECTOR, ".item")
    
    for element in elements:
        title = element.find_element(By.CLASS_NAME, "title").text
        content = element.find_element(By.CLASS_NAME, "desc").text
        print(f"标题: {title}, 内容: {content}")
```

#### 场景 3: 使用无头模式（后台运行）

```python
from wechat_scraper import WeChatBrowserScraper

# 无头模式 - 不显示浏览器窗口
scraper = WeChatBrowserScraper(headless=True)

try:
    scraper.start()
    scraper.open_url("https://your-wechat-h5-page.com")
    
    # 执行你的操作
    html = scraper.get_page_source()
    
finally:
    scraper.close()
```

#### 场景 4: 使用 iOS 微信 User-Agent

```python
from wechat_scraper import WeChatBrowserScraper
import config

# 使用 iOS 微信 User-Agent
scraper = WeChatBrowserScraper(
    user_agent=config.WECHAT_USER_AGENT_IOS
)

scraper.start()
scraper.open_url("https://your-wechat-h5-page.com")
# ... 你的操作
scraper.close()
```

### 4. 验证 User-Agent 是否正确设置

```python
from wechat_scraper import WeChatBrowserScraper

with WeChatBrowserScraper() as scraper:
    scraper.open_url("https://httpbin.org/headers")
    
    # 通过 JavaScript 获取 User-Agent
    user_agent = scraper.execute_script("return navigator.userAgent;")
    
    if 'MicroMessenger' in user_agent:
        print("✓ 成功模拟微信浏览器！")
        print(f"User-Agent: {user_agent}")
    else:
        print("✗ 未检测到微信 User-Agent")
```

### 5. 常见问题

**Q: 为什么需要设置 User-Agent？**

A: 很多微信服务号的 H5 页面会检查访问者是否来自微信客户端。通过设置包含 `MicroMessenger` 标识的 User-Agent，可以让网页认为我们是从微信浏览器访问的。

**Q: Android 和 iOS User-Agent 有什么区别？**

A: 主要是平台标识不同。有些页面可能对不同平台有不同的处理逻辑，可以根据需要选择使用。默认使用 Android User-Agent。

**Q: 可以自定义 User-Agent 吗？**

A: 可以！在创建 `WeChatBrowserScraper` 时传入 `user_agent` 参数即可。

```python
custom_ua = "your-custom-user-agent-with-MicroMessenger"
scraper = WeChatBrowserScraper(user_agent=custom_ua)
```

**Q: 如何处理需要滚动加载的页面？**

A: 可以使用 JavaScript 来滚动页面：

```python
with WeChatBrowserScraper() as scraper:
    scraper.open_url("https://your-page.com")
    
    # 滚动到页面底部
    scraper.execute_script("window.scrollTo(0, document.body.scrollHeight);")
    
    # 等待内容加载
    import time
    time.sleep(2)
```

### 6. 运行示例代码

本项目提供了多个示例文件：

```bash
# 查看功能演示
python demo.py

# 运行示例代码（需要修改 URL）
python example.py

# 运行单元测试
python -m unittest test_wechat_scraper.py -v
```

### 7. 更多资源

- 完整 API 文档：查看 README.md
- Selenium 官方文档：https://selenium-python.readthedocs.io/
- 问题反馈：在 GitHub 上提交 Issue

---

祝你使用愉快！如果有问题，欢迎提交 Issue 或 Pull Request。
