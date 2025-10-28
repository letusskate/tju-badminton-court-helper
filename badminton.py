from wechat_scraper import WeChatBrowserScraper

from selenium.webdriver.common.by import By

import time

# 使用上下文管理器（推荐）
with WeChatBrowserScraper() as scraper:
    # 打开你的微信 H5 页面
    scraper.open_url("http://vfmc.tju.edu.cn/Views/User/UserChoose.html")

    # 找登录按钮
    button = scraper.wait_for_element(By.XPATH, "/html/body/div/div[2]/div[1]")
    button.click()

    # # 登录
    # username_input = scraper.wait_for_element(By.ID, "username")
    # password_input = scraper.wait_for_element(By.ID, "password")
    
    # username_input.send_keys("your_username")
    # password_input.send_keys("your_password")
    
    # ## 提交表单
    # submit_btn.click()
    
    # 等待登录完成
    time.sleep(30)

    # # 访问需要认证的页面
    # scraper.open_url("https://your-authenticated-page.com")
    