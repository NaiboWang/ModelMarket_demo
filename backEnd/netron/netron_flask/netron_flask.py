import time
from random import random
import threading
from werkzeug.utils import cached_property
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

browsers = []
n = 3  # 浏览器数量，即最多可同时处理的文件数量，用以多并发


path = os.path.abspath(os.getcwd() + '/../../static/pics')
chrome_options = webdriver.ChromeOptions()
prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': path}
chrome_options.add_experimental_option('prefs', prefs)
# chrome_options.add_argument('--no-sandbox')#解决DevToolsActivePort文件不存在的报错
chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
chrome_options.add_argument('--disable-dev-shm-usage')
# Solve  the problem of cannot run google-chrome in command line and must include headless to run
# https://stackoverflow.com/questions/60304251/unable-to-open-x-display-when-trying-to-run-google-chrome-on-centos-rhel-7-5
chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
chrome_options.binary_location = r"chrome/chrome"  # 手动指定使用的浏览器位置
# 设置最多同时处理的任务长度，即浏览器打开的数量
for i in range(n):
    browser = webdriver.Chrome('./chromedriver', options=chrome_options)
    browsers.append({"browser": browser, "status": "waiting"})
app = Flask(__name__)


class Device:
    def __init__(self):
        self.lock = threading.Lock()
        self.sem = threading.Semaphore(value=n)
        # 允许最多三个线程同时访问资源

    def get_model_structure(self, name):
        browser = None
        id = 0
        self.sem.acquire()  # 加锁，锁住相应的资源
        # 找到浏览器状态
        self.lock.acquire()  # 锁住n个浏览器变量
        for i in range(len(browsers)):
            if browsers[i]["status"] == 'waiting':
                browser = browsers[i]["browser"]
                browsers[i]["status"] = 'working'
                id = i
                break
        self.lock.release()  # 解锁
        try:
            browser.get('http://localhost/modelmarket/netron/index.html?model=%s' % name)
            WebDriverWait(browser, 10).until(
                EC.presence_of_element_located((By.XPATH, '//*[@id="background"]'))
            )
            action = ActionChains(browser)
            action.key_down(Keys.CONTROL).key_down(Keys.ALT).send_keys('e').key_up(Keys.CONTROL).key_up(Keys.ALT).perform()
        except:
            self.lock.acquire()  # 锁住n个浏览器变量
            browsers[id]["status"] = 'waiting'
            self.lock.release()  # 解锁
            self.sem.release()  # 解锁，离开该资源
            return 301
        self.lock.acquire()  # 锁住n个浏览器变量
        browsers[id]["status"] = 'waiting'
        self.lock.release()  # 解锁
        self.sem.release()  # 解锁，离开该资源
        return name


device = Device()


class jdThread(threading.Thread):
    def __init__(self,name):
        threading.Thread.__init__(self)
        self.name = name
        self.status = 200

    def run(self):
        self.status = device.get_model_structure(self.name)  # 将num加1，并输出原来的数据和+1之后的数据

    def get_status(self):
        return self.status


@app.route('/modelmarket_netron/<name>')
def get_structure(name):
    t = jdThread(name)
    t.start()
    t.join()  # 等待线程执行完毕
    status = t.get_status()
    print("Done with", name, ", status is:", status)
    return jsonify({"status": status, "msg": name + '.svg'})


@app.route('/modelmarket_netron/test.info')
def test():
    return "test"


if __name__ == '__main__':
    # path = os.path.abspath(os.getcwd() + '/../../static/pics')
    # chrome_options = webdriver.ChromeOptions()
    # prefs = {'profile.default_content_settings.popups': 0, 'download.default_directory': path}
    # chrome_options.add_experimental_option('prefs', prefs)
    # # chrome_options.add_argument('--no-sandbox')#解决DevToolsActivePort文件不存在的报错
    # chrome_options.add_argument('window-size=1920x3000')  # 指定浏览器分辨率
    # chrome_options.add_argument('--disable-gpu')  # 谷歌文档提到需要加上这个属性来规避bug
    # chrome_options.add_argument('--hide-scrollbars')  # 隐藏滚动条, 应对一些特殊页面
    # chrome_options.add_argument('--disable-dev-shm-usage')
    # # Solve  the problem of cannot run google-chrome in command line and must include headless to run
    # # https://stackoverflow.com/questions/60304251/unable-to-open-x-display-when-trying-to-run-google-chrome-on-centos-rhel-7-5
    # chrome_options.add_argument('--headless')  # 浏览器不提供可视化页面. linux下如果系统不支持可视化不加这条会启动失败
    # chrome_options.binary_location = r"chrome/chrome"  # 手动指定使用的浏览器位置
    # # 设置最多同时处理的任务长度，即浏览器打开的数量
    # for i in range(n):
    #     browser = webdriver.Chrome('./chromedriver', options=chrome_options)
    #     browsers.append({"browser": browser, "status": "waiting"})
    # 注意，在uwsgi配置的生产环境中，前面这堆代码是不会执行的，所以要配置到外面公共区域
    app.run('0.0.0.0', 8078, True, processes=True)
