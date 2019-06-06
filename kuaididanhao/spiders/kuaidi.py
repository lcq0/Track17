# -*- coding: utf-8 -*-
import scrapy
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from selenium import webdriver
import selenium.webdriver.firefox.webdriver
import selenium.webdriver.firefox.firefox_profile
from selenium.webdriver.support.wait import WebDriverWait

from kuaididanhao import items
from kuaididanhao.util.excelutil import Excel
from scrapy.conf import settings
from kuaididanhao import settings
from kuaididanhao.util.globalLog import ta_log


class KuaidiSpider(scrapy.Spider):
    name = 'kuaidi'
    allowed_domains = ['t.17track.net', 'www.dhl.com']  # 17Track
    start_urls = ['https://t.17track.net/zh-cn']  # 17Track
    queue_col11 = Excel.read_excel(Excel)
    read_len = len(queue_col11)

    def __init__(self, timeout=30):
        # profile = webdriver.FirefoxProfile()
        # profile.set_preference('permissions.default.image', 2)
        profile = webdriver.FirefoxOptions()
        profile.add_argument('-headless')
        self.timeout = timeout
        self.browser = webdriver.Firefox(options=profile)
        # self.browser.set_page_load_timeout(self.timeout)
        self.wait = WebDriverWait(self.browser, self.timeout)
        self.url_track = str(self.queue_col11.popleft())
        if len(self.queue_col11) <= 0:
            ta_log.info("文件："+settings.excel_path+"已经没有需要爬取的物流信息！")
            self.browser.quit()
            return
        if '17track' in self.url_track:
            i = 0
            t = self.queue_col11.popleft()
            if isinstance(t, float):
                str_url0 = '#nums=' + str(int(t))
            else:
                str_url0 = '#nums=' + t
            while i < 39:
                i += 1
                try:
                    t = self.queue_col11.popleft()
                except IndexError:
                    break
                else:
                    t = t.split(',')[0]
                    if isinstance(t, float):
                        str_url0 = str_url0 + ',' + str(int(t))
                    else:
                        str_url0 = str_url0 + ',' + t
                    # #nums=RS912523242CH,UWQ8570207010227,LT346566736CN
            self.start_urls = ['https://t.17track.net/zh-cn/'+str_url0]  # 17Track
        elif 'dhl' in self.url_track:
            i = 0
            str_url0 = 'AWB='+str(int(self.queue_col11.popleft()))
            while (i < 9):
                i += 1
                try:
                    t = str(int(self.queue_col11.popleft()))
                except IndexError:
                    break
                else:
                    t = t.split(',')[0]
                    str_url0 = str_url0 + '%2C' + t
                    # AWB=1914885755%2C1324862055%2C4066879795&brand=DHL
            str_url0 = str_url0+'&brand=DHL'
            self.start_urls = ['http://www.dhl.com/en/express/tracking.html?' + str_url0]  # www.dhl.com
        elif 'usps' in self.url_track:
            i = 0
            str_url0 = 'tRef=fullpage&tLc=3&text28777=&tLabels='+self.queue_col11.popleft()
            while (i < 4):
                i += 1
                try:
                    t = self.queue_col11.popleft()
                except IndexError:
                    break
                else:
                    t = t.split(',')[0]
                    str_url0 = str_url0 + '%2C' + t
            str_url0 = str_url0+'%2C'
            self.start_urls = ['https://zh-tools.usps.com/go/TrackConfirmAction?' + str_url0]
        else:
            i = 0
            t = self.queue_col11.popleft()
            if isinstance(t, float):
                str_url0 = '#nums=' + str(int(t))
            else:
                str_url0 = '#nums=' + t
            while (i < 39):
                i += 1
                try:
                    t = self.queue_col11.popleft()
                except IndexError:
                    break
                else:
                    t = t.split(',')[0]
                    if isinstance(t, float):
                        str_url0 = str_url0 + ',' + str(int(t))
                    else:
                        str_url0 = str_url0 + ',' + t
                    # #nums=RS912523242CH,UWQ8570207010227,LT346566736CN
            self.start_urls = ['https://t.17track.net/zh-cn/' + str_url0]  # 17Track
        super(KuaidiSpider, self).__init__()
        dispatcher.connect(self.spider_closed, signals.spider_closed)
    def spider_closed(self, spider):
        # 当爬虫退出的时候 关闭chrome
        print("spider closed")
        self.browser.quit()
    def parse(self, response):
        # 17Track解析
        if '17track' in self.browser.current_url:
            kuaidi = response.xpath("//div/article/div[2]/div[1]/div/div/div[@class='tracklist-item tracklist-tracking']")
            for kuai in kuaidi:
                trackItem = items.KuaididanhaoItem()
                trackItem['trackNo'] = kuai.xpath(".//p[@class='text-uppercase']/text()").extract_first()
                trackItem['trackStatus'] = kuai.xpath(".//p[@class='text-capitalize']/text()").extract_first()
                trackItem['trackOrigin'] = kuai.xpath(".//div[1]/div[2]/div[1]/div[2]/div/span/text()").extract_first()
                trackItem['trackTarget'] = kuai.xpath(".//div[1]/div[2]/div[3]/div[2]/div/span/text()").extract_first()
                trackItem['trackTime'] = kuai.xpath(".//div[1]/div[3]/p/time/text()").extract_first()
                trackItem['trackEvent'] = kuai.xpath(".//div[1]/div[3]/p/span/text()").extract_first()
                yield trackItem
        # dhl解析
        elif 'dhl' in self.browser.current_url:
            # print(response.text)
            # kuaidi = response.xpath("//div[3]/div[5]/div[2]/div[1]/div[2]/div/div[2]/div[1]"
            #                         "/div[@class='tracking-result express']/table[1]/tbody/tr")
            kuaidi = response.xpath("//div[@class='tracking-result express']")
            for kuai in kuaidi:
                trackItem = items.KuaididanhaoItem()
                t_no = kuai.xpath(".//td[2]/strong/text()").extract_first()
                if 'Waybill' in t_no:
                    trackItem['trackNo'] = t_no.split(': ')[1]
                else:
                    trackItem['trackNo'] = '未找到'
                    continue
                t_status = kuai.xpath(".//td[2]/span/text()").extract_first()
                trackItem['trackStatus'] = "\n".join(t_status)
                trackItem['trackOrigin'] = kuai.xpath(".//td[3]/a[1]/text()").extract_first()
                trackItem['trackTarget'] = kuai.xpath(".//td[3]/a[2]/text()").extract_first()
                trackItem['trackTime'] = kuai.xpath(".//td[3]/span[1]/text()").extract_first()
                trackItem['trackEvent'] = '数据来源DHL'
                yield trackItem
        # usps解析
        elif 'usps' in self.browser.current_url:
            kuaidi = response.xpath("//div[@class='col-sm-10 col-sm-offset-1']/div[1]")
            for kuai in kuaidi:
                trackItem = items.KuaididanhaoItem()
                trackItem['trackNo'] = kuai.xpath(".//h3[@class='tracking_number']/span[1]/text()").extract_first()
                trackItem['trackStatus'] = kuai.xpath(".//div[2]/h2/strong/text()").extract_first()
                trackItem['trackOrigin'] = kuai.xpath(".//div[2]/div/p[3]/text()").extract_first()
                trackItem['trackTarget'] = kuai.xpath(".//div[2]/div/p[3]/text()").extract_first()
                trackItem['trackTime'] = kuai.xpath(".//div[2]/div/p[1]/text()").extract_first()
                trackItem['trackEvent'] = kuai.xpath(".//div[2]/div/p[2]/text()").extract_first()
                yield trackItem
        else:
            kuaidi = response.xpath(
                "//div/article/div[2]/div[1]/div/div/div[@class='tracklist-item tracklist-tracking']")
            for kuai in kuaidi:
                trackItem = items.KuaididanhaoItem()
                trackItem['trackNo'] = kuai.xpath(".//p[@class='text-uppercase']/text()").extract_first()
                trackItem['trackStatus'] = kuai.xpath(".//p[@class='text-capitalize']/text()").extract_first()
                trackItem['trackOrigin'] = kuai.xpath(".//div[1]/div[2]/div[1]/div[2]/div/span/text()").extract_first()
                trackItem['trackTarget'] = kuai.xpath(".//div[1]/div[2]/div[3]/div[2]/div/span/text()").extract_first()
                trackItem['trackTime'] = kuai.xpath(".//div[1]/div[3]/p/time/text()").extract_first()
                trackItem['trackEvent'] = kuai.xpath(".//div[1]/div[3]/p/span/text()").extract_first()
                yield trackItem
        if len(self.queue_col11) > 0:
            if '17track' in self.url_track:
                i = 0
                t = self.queue_col11.popleft()
                if isinstance(t, float):
                    str_url0 = '#nums=' + str(int(t))
                else:
                    str_url0 = '#nums=' + t
                while (i < 39):
                    i += 1
                    try:
                        t = self.queue_col11.popleft()
                    except IndexError:
                        break
                    else:
                        t = t.split(',')[0]
                        if isinstance(t, float):
                            str_url0 = str_url0 + ',' + str(int(t))
                        else:
                            str_url0 = str_url0 + ',' + t
                yield scrapy.Request("https://t.17track.net/zh-cn/"+str_url0, callback=self.parse, dont_filter=True)
            elif 'dhl' in self.url_track:
                i = 0
                str_url0 = 'AWB=' + self.queue_col11.popleft()
                while (i < 9):
                    i += 1
                    try:
                        t = self.queue_col11.popleft()
                    except IndexError:
                        break
                    else:
                        t = t.split(',')[0]
                        str_url0 = str_url0 + '%2C' + t
                        # AWB=1914885755%2C1324862055%2C4066879795&brand=DHL
                str_url0 = str_url0 + '&brand=DHL'
                yield scrapy.Request("http://www.dhl.com/en/express/tracking.html?" + str_url0, callback=self.parse,
                                     dont_filter=True)
            elif 'usps' in self.url_track:
                i = 0
                str_url0 = 'tRef=fullpage&tLc=3&text28777=&tLabels=' + self.queue_col11.popleft()
                while (i < 34):
                    i += 1
                    try:
                        t = self.queue_col11.popleft()
                    except IndexError:
                        break
                    else:
                        t = t.split(',')[0]
                        str_url0 = str_url0 + '%2C' + t
                str_url0 = str_url0 + '%2C'
                yield scrapy.Request("https://zh-tools.usps.com/go/TrackConfirmAction?" + str_url0, callback=self.parse,
                                     dont_filter=True)
            else:
                i = 0
                t = self.queue_col11.popleft()
                if isinstance(t, float):
                    str_url0 = '#nums=' + str(int(t))
                else:
                    str_url0 = '#nums=' + t
                while (i < 39):
                    i += 1
                    try:
                        t = self.queue_col11.popleft()
                    except IndexError:
                        break
                    else:
                        t = t.split(',')[0]
                        if isinstance(t, float):
                            str_url0 = str_url0 + ',' + str(int(t))
                        else:
                            str_url0 = str_url0 + ',' + t
                yield scrapy.Request("https://t.17track.net/zh-cn/" + str_url0, callback=self.parse, dont_filter=True)