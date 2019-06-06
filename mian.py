from scrapy.cmdline import execute
import sys
from kuaididanhao import settings
import tkinter
import os


def action(self, text, entry, entry_0):
    settings.text = text
    self.entry = entry
    self.entry_0 = entry_0
    settings.excel_path = self.entry.get()  # 文件路径
    ips = self.entry_0.get()  # IP地址
    if settings.excel_path == '' or ips == '':
        settings.text.insert(tkinter.END, '请先输入您的文件路径和代理IP！')
        return

    if os.access(settings.excel_path, os.F_OK) and os.access(settings.excel_path, os.W_OK):
        settings.text.insert(tkinter.END, "文件存在可用")  # 在文本框中显示下载信息
        settings.text.see(tkinter.END)
        settings.text.update()
    else:
        settings.text.insert(tkinter.END, "文件不存在或者文件被占用")  # 在文本框中显示下载信息
        settings.text.see(tkinter.END)
        settings.text.update()
        return
    if ips.find(',') > 0:
        settings.IP_LIST = ips.split(',')
    else:
        settings.IP_LIST = [ips]

    sys.path.append(os.path.dirname(os.path.abspath(__file__)))
    execute(["scrapy", "crawl", "kuaidi"])