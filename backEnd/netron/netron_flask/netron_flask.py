from flask import Flask
from flask import jsonify
import os
from selenium import webdriver
from selenium.webdriver import DesiredCapabilities
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
# import Action chains 
from selenium.webdriver.common.action_chains import ActionChains
# import KEYS
from selenium.webdriver.common.keys import Keys

browser = None
app = Flask(__name__)

@app.route('/modelmarket_netron/<name>')
def hello_name(name):
    browser.get('http://localhost/modelmarket/netron/index.html?model=%s' % name)
    print(browser.get_log('browser'))
    WebDriverWait(browser, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="background"]'))
    )
    action = ActionChains(browser)
    action.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('e').key_up(Keys.CONTROL).key_up(Keys.ALT).perform()
    return jsonify({"status":200,"msg": name+'.svg'})

if __name__ == '__main__':
    path = os.path.abspath(os.getcwd()+'/../../pics')
    chrome_options = webdriver.ChromeOptions()
    prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': path}
    chrome_options.add_experimental_option('prefs', prefs)
    # chrome_options.add_argument('--no-sandbox')#解决DevToolsActivePort文件不存在的报错
    chrome_options.add_argument('window-size=1920x3000') #指定浏览器分辨率
    chrome_options.add_argument('--disable-gpu') #谷歌文档提到需要加上这个属性来规避bug
    chrome_options.add_argument('--hide-scrollbars') #隐藏滚动条, 应对一些特殊页面
    chrome_options.add_argument('--disable-dev-shm-usage')
    # Solve  the problem of cannot run google-chrome in command line and must include headless to run
    # https://stackoverflow.com/questions/60304251/unable-to-open-x-display-when-trying-to-run-google-chrome-on-centos-rhel-7-5
    chrome_options.add_argument('--headless') #浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    chrome_options.binary_location = r"/usr/bin/google-chrome-stable" #手动指定使用的浏览器位置
    browser = webdriver.Chrome('./chromedriver', options=chrome_options)
    app.run('0.0.0.0',8078,True)