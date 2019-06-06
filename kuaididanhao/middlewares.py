# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals

import random
from scrapy.conf import settings
from scrapy.http import HtmlResponse
import time
from kuaididanhao.util.globalLog import ta_log
from kuaididanhao import settings
import requests
import tkinter


class KuaididanhaoSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)
# ip
from selenium import webdriver


class ProxyMiddleware(object):
    ip_list = settings.IP_LIST
    USER_AGENT_LIST = settings.USER_AGENT_LIST

    def process_request(self, request, spider):
        ip = random.choice(self.ip_list)
        print('requestIP', ip)
        request.meta['proxy'] = ip
        agent = random.choice(self.USER_AGENT_LIST)

        chromeOptions = webdriver.ChromeOptions()
        # 设置代理
        chromeOptions.add_argument("--user-agent=" + agent)
        chromeOptions.add_argument("--proxy-server=" + ip)
        chromeOptions.add_argument('--disable-gpu')
        chromeOptions.add_argument("-headless")
        # 一定要注意，=两边不能有空格，不能是这样--proxy-server = http://202.20.16.82:10152
        spider.browser = webdriver.Chrome(executable_path="D:/ProgramData/chromedriver.exe",
                                        chrome_options=chromeOptions)


class my_useragent(object):
    USER_AGENT_LIST = settings.USER_AGENT_LIST

    def process_request(self, request, spider):

        agent = random.choice(self.USER_AGENT_LIST)
        print('requestAgent:', agent)
        request.headers['User_Agent'] = agent


class JSPageMiddleware(object):

    i = 0
    j = 0

    def IPcheck(self, ip):
        try:
            url = 'http://ip.tool.chinaz.com/'
            proxies = {
                'http': ip,
            }
            p = requests.get(url=url, proxies=proxies)
            temp = p.text
            settings.text.insert(tkinter.END, temp)  # 在前端文本框中显示下载完毕
            settings.text.see(tkinter.END)
            settings.text.update()
            return True
        except BaseException:
            ta_log.info('无效IP地址:'+ip)
            settings.text.insert(tkinter.END, '无效IP地址:'+ip)  # 在前端文本框中显示下载完毕
            settings.text.see(tkinter.END)
            settings.text.update()
        return False

    def getip(self, ip_list, delete_errorip):
        if delete_errorip == 1:
            ta_log.error("删除代理IP="+ip_list.pop(self.j-1))
            self.j = self.j-1
        if len(ip_list) <= 0:
            ta_log.error("已经没有可用的IP地址了，请更换IP并重启程序！")
            exit(0)
        if len(ip_list) - 1 > self.j:
            temp_ip = ip_list[self.j]
        else:
            self.j = 0
            temp_ip = ip_list[self.j]
        self.j = self.j + 1
        if len(temp_ip) < 1:
            ta_log.info('全部IP地址都已无效，请重新开始')
            settings.text.insert(tkinter.END, '全部IP地址都已无效，请重新开始:')
            settings.text.see(tkinter.END)
            settings.text.update()
        else:
            if JSPageMiddleware.IPcheck(temp_ip):
                return temp_ip
            else:
                JSPageMiddleware.getip(self, ip_list, delete_errorip)
        return temp_ip

    # 通过chrome 动态访问
    def process_request(self, request, spider):
        if spider.name == "kuaidi":
            try:
                return JSPageMiddleware.requesting(self, request, spider, 0)
            except TimeoutError:
                ta_log.info("请求失败，代理IP失效TimeoutError")
                return HtmlResponse(url=request.url, status=500, request=request)
            except(BaseException):
                ta_log.info("请求失败，代理IP失效TimeoutError")
                return JSPageMiddleware.requesting(self, request, spider, 1)

    def requesting(self, request, spider, delete_errorip):
        ip_list = settings.IP_LIST
        temp_ip = JSPageMiddleware.getip(ip_list, delete_errorip)
        if len(temp_ip) < 1:
            spider.browser.quit()
        ip = temp_ip.split(':')[0]
        port = temp_ip.split(':')[1]
        USER_AGENT_LIST = settings.USER_AGENT_LIST
        user_agent = random.choice(USER_AGENT_LIST)
        ta_log.info(ip+' '+port+' '+user_agent)
        spider.browser.get("about:config")
        # spider.browser.maximize_window()
        # spider.browser.set_window_size(100, 50)
        script = '''
            var prefs = Components.classes["@mozilla.org/preferences-service;1"].getService(Components.interfaces.nsIPrefBranch);
            prefs.setIntPref("network.proxy.type", 1);
            prefs.setCharPref("network.proxy.http", "{ip}");
            prefs.setIntPref("network.proxy.http_port", "{port}");
            prefs.setCharPref("network.proxy.ssl", "{ip}");
            prefs.setIntPref("network.proxy.ssl_port", "{port}");
            prefs.setCharPref("network.proxy.ftp", "{ip}");
            prefs.setIntPref("network.proxy.ftp_port", "{port}");
            prefs.setBoolPref("general.useragent.site_specific_overrides",true);
            prefs.setBoolPref("general.useragent.updates.enabled",true);
            prefs.setCharPref("general.useragent.override","{user_agent}");
            '''.format(ip=ip, port=port, user_agent=user_agent)
        spider.browser.execute_script(script)
        time.sleep(1)

        spider.browser.get(request.url)
        time.sleep(settings['wait_time'])
        j = 0
        ta_log.info("访问：{0}".format(request.url))
        while self.i < 1 and '17track' in format(request.url):
            self.i += 1
            try:
                spider.browser.find_element_by_xpath('/html/body/div[5]/div/div[5]/a[1]').click()
            except BaseException:
                time.sleep(3)
                j += 1
                if j > 1:
                    break
            else:
                break
        # spider.browser.find_element_by_xpath('//*[@id="jsTrackBox"]/div[1]/div/div[6]/div[1]/div/div/div/div[5]/div/pre/span').send_keys("90747786567")
        return HtmlResponse(url=spider.browser.current_url, body=spider.browser.page_source, encoding="utf-8")

