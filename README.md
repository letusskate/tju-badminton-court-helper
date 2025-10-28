# TJU Badminton Court Helper

一个基于 Python Selenium 的微信服务号（H5页面）爬虫工具，能够模拟微信内置浏览器访问仅在微信中可用的网页。

## 功能特性

- ✅ 模拟微信内置浏览器（通过设置 User-Agent）
- ✅ 支持 Android 和 iOS 微信 User-Agent
- ✅ 自动管理 ChromeDriver
- ✅ 支持无头模式运行
- ✅ 提供丰富的 API 用于页面交互
- ✅ 支持截图、Cookie 管理、JavaScript 执行等功能

## 安装

### 前置要求

- Python 3.7+
- Chrome 浏览器

### 安装依赖

```bash
pip install -r requirements.txt
```

## 快速开始

### 基本使用

```python
from wechat_scraper import WeChatBrowserScraper
import time

# 创建爬虫实例
scraper = WeChatBrowserScraper()

try:
    # 启动浏览器
    scraper.start()
    
    # 打开目标网页
    scraper.open_url("https://your-wechat-h5-page.com")
    
    # 等待页面加载
    time.sleep(3)
    
    # 截图
    scraper.take_screenshot("screenshot.png")
    
    # 获取页面源码
    page_source = scraper.get_page_source()
    
finally:
    # 关闭浏览器
    scraper.close()
```

### 使用上下文管理器

```python
from wechat_scraper import WeChatBrowserScraper

with WeChatBrowserScraper() as scraper:
    scraper.open_url("https://your-wechat-h5-page.com")
    # 执行你的操作...
    # 浏览器会自动关闭
```

### 自定义配置

```python
from wechat_scraper import WeChatBrowserScraper

# 使用 iOS 微信 User-Agent
ios_user_agent = (
    "Mozilla/5.0 (iPhone; CPU iPhone OS 14_6 like Mac OS X) "
    "AppleWebKit/605.1.15 (KHTML, like Gecko) Mobile/15E148 "
    "MicroMessenger/8.0.20(0x18001428) NetType/WIFI Language/zh_CN"
)

scraper = WeChatBrowserScraper(
    user_agent=ios_user_agent,  # 自定义 User-Agent
    headless=True,              # 无头模式运行
    window_size=(414, 896),     # iPhone XR 屏幕尺寸
    timeout=15                  # 默认等待超时时间（秒）
)

scraper.start()
# ... 你的代码
scraper.close()
```

## API 文档

### WeChatBrowserScraper 类

主要的爬虫类，提供模拟微信浏览器的功能。

#### 初始化参数

- `user_agent` (str, 可选): 自定义 User-Agent 字符串，默认使用 Android 微信 UA
- `headless` (bool, 可选): 是否以无头模式运行，默认为 False
- `window_size` (tuple, 可选): 浏览器窗口大小 (宽, 高)，默认为 (375, 812)
- `timeout` (int, 可选): 默认等待超时时间（秒），默认为 10

#### 主要方法

##### start()
启动浏览器

##### open_url(url)
导航到指定 URL

**参数:**
- `url` (str): 要访问的 URL

##### wait_for_element(by, value, timeout=None)
等待元素出现在页面上

**参数:**
- `by` (By): 定位方法 (如 By.ID, By.XPATH)
- `value` (str): 定位值
- `timeout` (int, 可选): 等待超时时间

**返回:** WebElement

##### wait_for_element_clickable(by, value, timeout=None)
等待元素可点击

**参数:**
- `by` (By): 定位方法
- `value` (str): 定位值
- `timeout` (int, 可选): 等待超时时间

**返回:** WebElement

##### get_page_source()
获取当前页面的 HTML 源码

**返回:** str - 页面源码

##### take_screenshot(filename)
对当前页面截图

**参数:**
- `filename` (str): 保存截图的文件名

##### execute_script(script, *args)
在浏览器中执行 JavaScript

**参数:**
- `script` (str): 要执行的 JavaScript 代码
- `*args`: 传递给脚本的参数

**返回:** JavaScript 执行结果

##### get_cookies()
获取当前会话的所有 Cookie

**返回:** list - Cookie 字典列表

##### add_cookie(cookie_dict)
向当前会话添加 Cookie

**参数:**
- `cookie_dict` (dict): Cookie 信息字典

##### close()
关闭浏览器

## 配置文件

`config.py` 包含默认配置：

- `WECHAT_USER_AGENT_ANDROID`: Android 微信 User-Agent
- `WECHAT_USER_AGENT_IOS`: iOS 微信 User-Agent
- `DEFAULT_USER_AGENT`: 默认使用的 User-Agent
- `WINDOW_WIDTH`, `WINDOW_HEIGHT`: 默认窗口大小
- `DEFAULT_TIMEOUT`: 默认超时时间
- `HEADLESS`: 是否默认使用无头模式

## 示例

查看 `example.py` 获取更多使用示例：

```bash
python example.py
```

示例包括：
- 基本使用
- 上下文管理器使用
- 自定义配置
- 元素交互
- JavaScript 执行

## 关键特性说明

### 微信 User-Agent

本工具的核心在于设置正确的 User-Agent 使网页认为访问来自微信客户端。关键标识是 `MicroMessenger`：

```python
# Android 微信 User-Agent 示例
wechat_user_agent = (
    "Mozilla/5.0 (Linux; Android 9; SM-G960F Build/PPR1.180610.011) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Mobile "
    "Safari/537.36 MicroMessenger/8.0.30.1810(0x28001030) Process/tools"
)
```

### 防检测机制

工具实现了以下防检测措施：
- 移除 `navigator.webdriver` 属性
- 禁用自动化控制特征
- 设置移动设备仿真
- 配置合适的窗口大小

## 注意事项

1. 确保已安装 Chrome 浏览器
2. ChromeDriver 会自动下载和管理
3. 某些网页可能有额外的验证机制
4. 请遵守网站的使用条款和 robots.txt

## 许可证

查看 LICENSE 文件了解详情。

## 贡献

欢迎提交 Issue 和 Pull Request！