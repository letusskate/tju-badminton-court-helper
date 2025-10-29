from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
import json
import requests
import urllib.parse

# 从 config.py 导入 DEFAULT_USER_AGENT、WINDOW_WIDTH/HEIGHT、HEADLESS 等（如果需要）
from config import DEFAULT_USER_AGENT, WINDOW_WIDTH, WINDOW_HEIGHT, HEADLESS, DEFAULT_TIMEOUT

CHROMEDRIVER_PATH = r"./chromedriver-win64/chromedriver-win64/chromedriver.exe"  # 修改为你的路径
TARGET_URL = "http://vfmc.tju.edu.cn/Views/User/UserChoose.html"  # 改为目标 URL

options = Options()
# 不使用 headless（微信可能检测 headless）
if HEADLESS:
    # 如果你确实要 headless，请使用新 headless 模式并注意更容易被检测
    options.add_argument("--headless=new")
# 常规选项
options.add_argument(f"--user-agent={DEFAULT_USER_AGENT}")
options.add_argument(f"--window-size={WINDOW_WIDTH},{WINDOW_HEIGHT}")
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option("useAutomationExtension", False)

# mobile emulation via experimental option (加上 UA)
mobile_emulation = {
    "deviceMetrics": {"width": WINDOW_WIDTH, "height": WINDOW_HEIGHT, "pixelRatio": 3.0},
    "userAgent": DEFAULT_USER_AGENT,
}
options.add_experimental_option("mobileEmulation", mobile_emulation)

# 一些启动参数，尽量减少 Chrome 扩展或安全策略导致的客户端拦截
options.add_argument("--disable-extensions")
options.add_argument("--disable-popup-blocking")
options.add_argument("--no-default-browser-check")
options.add_argument("--disable-client-side-phishing-detection")
options.add_argument("--disable-component-update")
options.add_argument("--disable-background-networking")
options.add_argument("--disable-background-timer-throttling")
options.add_argument("--disable-renderer-backgrounding")
options.add_argument("--disable-features=IsolateOrigins,site-per-process")

# 使用临时 user-data-dir（干净的 profile，避免扩展/配置影响）
import tempfile
_tmp_profile = tempfile.mkdtemp(prefix="selenium_profile_")
options.add_argument(f"--user-data-dir={_tmp_profile}")

# 关闭 Safe Browsing 等可能拦截页面的设置（prefs）
prefs = {
  'profile.default_content_setting_values.notifications': 2,
  'safebrowsing.enabled': False,
  'safebrowsing.disable_download_protection': True,
}
options.add_experimental_option('prefs', prefs)

# 启用 performance + browser 日志以捕获 network 请求头（用于确认服务器端看到的 UA）
# Selenium 4 推荐通过 Options.set_capability 设置 loggingPrefs
options.set_capability('goog:loggingPrefs', {'performance': 'ALL', 'browser': 'ALL'})

service = Service(executable_path=CHROMEDRIVER_PATH)
driver = webdriver.Chrome(service=service, options=options)

# 1) 通过 CDP 覆盖 UA（双保险）
# Enable Network domain first (recommended) then override UA
driver.execute_cdp_cmd('Network.enable', {})
driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": DEFAULT_USER_AGENT})

# 2) 设置设备度量和启用触摸模拟
driver.execute_cdp_cmd('Emulation.setDeviceMetricsOverride', {
    "width": WINDOW_WIDTH,
    "height": WINDOW_HEIGHT,
    "deviceScaleFactor": 3,
    "mobile": True,
})
driver.execute_cdp_cmd('Emulation.setTouchEmulationEnabled', {"enabled": True})

# 3) 设置额外 HTTP headers（例如 Referer、语言）
driver.execute_cdp_cmd('Network.setExtraHTTPHeaders', {"headers": {
    "Referer": "https://servicewechat.com/",  # 根据目标服务调整
    "Accept-Language": "zh-CN,zh;q=0.9"
}})

# 4) 在页面脚本加载前注入脚本：隐藏 navigator.webdriver，注入 WeixinJSBridge 等
driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
    "source": """
// 隐藏 webdriver 标志
try{ Object.defineProperty(navigator, 'webdriver', { get: () => undefined }); }catch(e){}

// 基本的 userAgent 覆盖（备份）
try{ Object.defineProperty(navigator, 'userAgent', { get: () => '%s' }); }catch(e){}

// 更强力的覆盖：覆盖 Navigator.prototype.userAgent 以及 navigator.__proto__
try {
  Object.defineProperty(Navigator.prototype, 'userAgent', { get: function() { return '%s'; }, configurable: true });
} catch(e) {}
try {
  if (window.navigator && window.navigator.__proto__) {
    Object.defineProperty(window.navigator.__proto__, 'userAgent', { get: function() { return '%s'; }, configurable: true });
  }
} catch(e) {}

// 覆盖其他可能被检测的字段
try { Object.defineProperty(navigator, 'appVersion', { get: () => '%s' }); } catch(e){}
try { Object.defineProperty(navigator, 'platform', { get: () => 'Linux armv8l' }); } catch(e){}
try { Object.defineProperty(navigator, 'vendor', { get: () => 'Apple Computer, Inc.' }); } catch(e){}

// 注入微信 JSBridge 的最小 stub（避免页面因缺少而失败）
window.WeixinJSBridge = window.WeixinJSBridge || { invoke: function(){}, on: function(){}, call: function(){} };
window.__wxjs_environment = window.__wxjs_environment || 'browser';
""" % (DEFAULT_USER_AGENT, DEFAULT_USER_AGENT, DEFAULT_USER_AGENT, DEFAULT_USER_AGENT)
})

# 打开页面并等待
driver.get(TARGET_URL)
time.sleep(5)  # 初始等待，页面会执行检测脚本

# 调试：打印 navigator.userAgent 与页面 title
print("navigator.userAgent:", driver.execute_script("return navigator.userAgent"))
print("title:", driver.title)

# 保存截图与源码以便排查
out_dir = os.path.join(os.getcwd(), "debug_wechat")
os.makedirs(out_dir, exist_ok=True)
png_path = os.path.join(out_dir, "page.png")
html_path = os.path.join(out_dir, "page_source.html")
driver.save_screenshot(png_path)
with open(html_path, "w", encoding="utf-8") as f:
  f.write(driver.page_source)
print(f"Saved screenshot -> {png_path}")
print(f"Saved page source -> {html_path}")

# ===== 尝试点击页面中会导航到第二个页面的第一个候选元素 =====
second_png = os.path.join(out_dir, "page_2.png")
second_html = os.path.join(out_dir, "page_source_2.html")

# 找登录按钮
button = driver.find_element(By.XPATH, "/html/body/div/div[2]/div[1]")
button.click()

# 保存第二页截图与源码
driver.save_screenshot(second_png)
with open(second_html, 'w', encoding='utf-8') as f2:
    f2.write(driver.page_source)
print('Saved second page screenshot ->', second_png)
print('Saved second page source ->', second_html)
print('navigator.userAgent (second page):', driver.execute_script('return navigator.userAgent'))

# 如果第二页被 Chrome 拦截（常见为 ERR_BLOCKED_BY_CLIENT），尝试用 requests 直接拉取并把 HTML 作为 data URL 注入浏览器
second_src = driver.page_source.lower()
if 'err_blocked_by_client' in second_src or '已被屏蔽' in second_src:
  print('Second page appears blocked by Chrome in-browser. Attempting requests fallback...')
  try:
    sess = requests.Session()
    # 拷贝 cookie 到 requests
    for c in driver.get_cookies():
      sess.cookies.set(c['name'], c.get('value', ''), domain=c.get('domain'))

    headers = {
      'User-Agent': DEFAULT_USER_AGENT,
      'Referer': driver.current_url,
      'Accept-Language': 'zh-CN,zh;q=0.9'
    }
    resp = sess.get(driver.current_url, headers=headers, timeout=15)
    print('Fallback fetch status_code:', resp.status_code)
    fallback_path = os.path.join(out_dir, 'page_2_fallback.html')
    with open(fallback_path, 'w', encoding='utf-8') as ff:
      ff.write(resp.text)
    print('Saved fallback HTML ->', fallback_path)
    if resp.status_code == 200 and resp.text.strip():
      # 对返回的 HTML 做简单清理：去掉页面内显式的 "非微信环境提示" 脚本
      # 有些页面通过 JS 检测 navigator.userAgent 并在非微信环境时替换 DOM，
      # 我们在这里把这类检测脚本移除或屏蔽，以防页面内部再次替换为“请在微信客户端打开链接”。
      try:
        import re
        original_html = resp.text
        # 1) 屏蔽 if (!isWeixin) {...} 这类结构（非贪婪模式匹配大括号内内容）
        cleaned = re.sub(r"if\s*\(\s*!\s*isWeixin\s*\)\s*\{.*?\}", "/* removed isWeixin check */", original_html, flags=re.DOTALL|re.IGNORECASE)
        # 2) 另外把常见的简写形式也替换掉（if(!isWeixin)）
        cleaned = re.sub(r"if\s*\(\s*!isWeixin\s*\)\s*\{.*?\}", "/* removed isWeixin check */", cleaned, flags=re.DOTALL|re.IGNORECASE)
        # 3) 在页面顶部注入一个小脚本，作为保险：尽量在页面脚本执行前强制把 navigator.userAgent 中加入 MicroMessenger
        inject_script = "<script>try{Object.defineProperty(navigator,'userAgent',{get:function(){return '%s';},configurable:true});}catch(e){};</script>" % DEFAULT_USER_AGENT
        # 3b) 再注入一段防护脚本，用来拦截 document.write/writeln、innerHTML setter、location.replace/assign
        protect_script = '''<script>(function(){
  function shouldBlock(html){
    try{ return typeof html === 'string' && (html.indexOf('请在微信客户端打开链接')!==-1 || html.indexOf('抱歉，出错了')!==-1); }catch(e){return false}
  }
  var _doc_write = document.write.bind(document);
  document.write = function(){ try{ if(!shouldBlock(arguments[0])) return _doc_write.apply(document, arguments); console.log('blocked document.write'); }catch(e){} };
  document.writeln = function(){ try{ if(!shouldBlock(arguments[0])) return _doc_write.apply(document, arguments); console.log('blocked document.writeln'); }catch(e){} };
  try{
    var desc = Object.getOwnPropertyDescriptor(Element.prototype, 'innerHTML');
    if(desc && desc.set){
      var origSet = desc.set;
      Object.defineProperty(Element.prototype, 'innerHTML', {
        get: desc.get,
        set: function(v){ try{ if(shouldBlock(v)){ console.log('blocked innerHTML set'); return; } return origSet.call(this, v); }catch(e){} },
        configurable: true,
        enumerable: desc.enumerable
      });
    }
  }catch(e){}
  try{ var _replace = location.replace; location.replace = function(u){ console.log('blocked location.replace',u); }; var _assign = location.assign; location.assign = function(u){ console.log('blocked location.assign',u); }; }catch(e){}
  try{ window.WeixinJSBridge = window.WeixinJSBridge || { invoke:function(){}, on:function(){}, call:function(){}, publish:function(){}, subscribe:function(){}, config:function(){}, getEnv:function(){} }; window.__wxjs_environment = window.__wxjs_environment || 'browser'; }catch(e){}
})();</script>'''
        # 将注入脚本插入到 <head> 的开头（如果没有 head，则简单放到开头）
        if '<head' in cleaned.lower():
          cleaned = re.sub(r'(?i)(<head[^>]*>)', r"\1" + inject_script + protect_script, cleaned, count=1)
        else:
          cleaned = inject_script + protect_script + cleaned

        sanitized_path = os.path.join(out_dir, 'page_2_fallback_sanitized.html')
        with open(sanitized_path, 'w', encoding='utf-8') as sf:
          sf.write(cleaned)
        print('Saved sanitized fallback HTML ->', sanitized_path)

        # 把清理后的 HTML 作为 data URL 加载（避免 Chrome 本地拦截）
        data_url = 'data:text/html;charset=utf-8,' + urllib.parse.quote(cleaned)
        driver.get(data_url)
        time.sleep(2)
        # 保存渲染后的页面
        driver.save_screenshot(os.path.join(out_dir, 'page_2_fallback_render.png'))
        with open(os.path.join(out_dir, 'page_2_fallback_render.html'), 'w', encoding='utf-8') as rf:
          rf.write(driver.page_source)
        print('Loaded sanitized fallback HTML into browser and saved rendered snapshot.')
      except Exception as ee:
        print('Error sanitizing/loading fallback HTML:', ee)
  except Exception as e:
    print('Requests fallback failed:', e)

# 解析 performance 日志，寻找 Network.requestWillBeSent 事件里的请求头（用于确认服务器看到的 UA）
try:
  logs = driver.get_log('performance')
  found = False
  for entry in logs:
    try:
      msg = json.loads(entry['message'])['message']
    except Exception:
      continue
    if msg.get('method') == 'Network.requestWillBeSent':
      params = msg.get('params', {})
      req = params.get('request', {})
      url = req.get('url', '')
      headers = req.get('headers', {})
      # 匹配目标 URL 或包含目标文档 URL
      if TARGET_URL.split('?')[0] in url or TARGET_URL.split('?')[0] in params.get('documentURL', ''):
        ua = headers.get('User-Agent') or headers.get('user-agent')
        print('Network request for', url)
        print('Request headers User-Agent:', ua)
        found = True
  if not found:
    # 打印第一个可用的 requestUserAgent 作为样本
    for entry in logs[:50]:
      try:
        msg = json.loads(entry['message'])['message']
        if msg.get('method') == 'Network.requestWillBeSent':
          headers = msg.get('params', {}).get('request', {}).get('headers', {})
          if headers:
            print('Sample request headers User-Agent:', headers.get('User-Agent') or headers.get('user-agent'))
            break
      except Exception:
        continue

  # 尝试从 performance 日志中找到 responseReceived 事件并获取响应体（document 类型）
  try:
    for entry in logs:
      try:
        msg = json.loads(entry['message'])['message']
      except Exception:
        continue
      if msg.get('method') == 'Network.responseReceived':
        params = msg.get('params', {})
        response = params.get('response', {})
        r_url = response.get('url', '')
        if TARGET_URL.split('?')[0] in r_url and params.get('type') == 'Document':
          requestId = params.get('requestId')
          try:
            body = driver.execute_cdp_cmd('Network.getResponseBody', {'requestId': requestId})
            resp_text = body.get('body', '')
            resp_path = os.path.join(out_dir, 'document_response_body.html')
            with open(resp_path, 'w', encoding='utf-8') as rf:
              rf.write(resp_text)
            print('Saved document response body ->', resp_path)
            print('Response body snippet:', resp_text[:1000])
          except Exception as e:
            print('Could not get response body via CDP:', e)
          break
  except Exception as e:
    print('Error while extracting response bodies:', e)

  # 打印 browser console logs
  try:
    browser_logs = driver.get_log('browser')
    if browser_logs:
      print('---- Browser console logs ----')
      for bl in browser_logs:
        print(bl)
  except Exception as e:
    print('Could not fetch browser logs:', e)

except Exception as e:
  print('Failed to parse performance logs:', e)

time.sleep(1)
driver.quit()