import os
import tkinter
import requests
from lxml import etree
# 标记是否停止下载，初始值为False，当值为True时，停止下载
flag = False

class MusicSpider(object):


    def __init__(self):
        pass

    def download_songs(self, text, entry):
        self.text = text
        self.entry = entry
        url = self.entry.get()  # 获取输入框中的字符串
        url = url.replace('/#', '').replace('https', 'http')  # 对字符串进行去空格和转协议处理
        # 当没有输入url就点击下载或者回车的时候，在文本框中显示提示
        if url == '':
            self.text.insert(tkinter.END, '请输入您要下载的歌单的url地址！')
            return
        # 网易云音乐外链url接口：http://music.163.com/song/media/outer/url?id=xxxx
        out_link = 'http://music.163.com/song/media/outer/url?id='
        # 请求头
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.170 Safari/537.36',
            'Referer': 'https://music.163.com/',
            'Host': 'music.163.com'
        }
        # 请求页面的源码
        res = requests.get(url=url, headers=headers).text

        tree = etree.HTML(res)
        # 音乐列表
        song_list = tree.xpath('//ul[@class="f-hide"]/li/a')
        # 如果是歌手页面
        artist_name_tree = tree.xpath('//h2[@id="artist-name"]/text()')
        artist_name = str(artist_name_tree[0]) if artist_name_tree else None

        # 如果是歌单页面：
        song_list_name_tree = tree.xpath('//h2[contains(@class,"f-ff2")]/text()')
        song_list_name = str(song_list_name_tree[0]) if song_list_name_tree else None

        # 设置音乐下载的文件夹为歌手名字或歌单名
        folder = './' + artist_name if artist_name else './' + song_list_name

        if not os.path.exists(folder):
            os.mkdir(folder)

        for i,s in enumerate(song_list):
            href = str(s.xpath('./@href')[0])
            id = href.split('=')[-1]
            src = out_link + id  # 拼接获取音乐真实的src资源值
            title = str(s.xpath('./text()')[0])  # 音乐的名字
            filename = title + '.mp3'
            filepath = folder + '/' + filename
            data = requests.get(src).content  # 音乐的二进制数据
            info = '开始下载第%d首音乐：%s\n' % (i+1, filename)

            if flag:  # 当停止下载时，显示信息，跳出循环，代码不再向下执行
                self.text.insert(tkinter.END, '停止下载')
                self.text.see(tkinter.END)
                self.text.update()
                break
            self.text.insert(tkinter.END, info)  # 在文本框中显示下载信息
            self.text.see(tkinter.END)
            self.text.update()

            try:  # 下载音乐
                with open(filepath, 'wb') as f:
                    f.write(data)
            except Exception as e:
                print(e)
                self.text.insert(tkinter.END, e)  # 将错误信息显示在前端文本框中
                self.text.see(tkinter.END)
                self.text.update()

        if not flag:  # 中间没有点击停止下载，程序会走到这里
            self.text.insert(tkinter.END, '下载完成')  # 在前端文本框中显示下载完毕
            self.text.see(tkinter.END)
            self.text.update()