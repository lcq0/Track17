import tkinter
import mian
from kuaididanhao.spiders import MusicSpider


class Application(object):
    def __init__(self):
        # 创建主窗口Tk()
        self.window = tkinter.Tk()
        # 设置一个标题，参数类型：string
        self.window.title('物流单号爬取')
        # 设置主窗口大小和位置
        # self.window.geometry('800x500+240+120')
        self.center_window(self.window, 1000, 600)  # 窗口居中，宽800，高500
        # 使用frame增加上中下4个框架
        self.fm1 = tkinter.Frame(self.window)  # fm1存放label标签
        self.fm2 = tkinter.Frame(self.window)  # fm2存放url输入框,下载按钮
        self.fm3_0 = tkinter.Frame(self.window)  # fm3_0 存放错误IP显示的文本框
        self.fm3 = tkinter.Frame(self.window)  # fm3 存放下载信息显示的文本框
        self.fm4 = tkinter.Frame(self.window)  # fm4用来存放底下停止和退出按钮
        self.fm1.pack()
        self.fm2.pack()
        self.fm3_0.pack()
        self.fm3.pack()
        self.fm4.pack()

        # 创建一个标签
        self.label = tkinter.Label(self.fm1, text='请输入文件路径和代理IP(多个IP地址用,隔开)，点击开始或者回车！', font=('微软雅黑', 15), width=55)
        # 显示，布局管理器----可以理解为一个弹性容器
        self.label.pack(fill=tkinter.X)

        # 创建一个输入框，用来接收用户输入的歌单的url
        self.entry = tkinter.Entry(self.fm2, width=46, bg='pink', font=('微软雅黑', 12))
        self.entry.grid(row=0, column=0, rowspan=1, columnspan=10, padx=2)
        self.entry.bind("<Key-Return>", self.press_enter)  # 输入歌单url之后直接按回车键，触发press_enter函数
        self.entry.insert(10, 'C:\TrackData\81967003.xlsx')

        self.label = tkinter.Label(self.fm2, text='', font=('微软雅黑', 15), width=3)
        self.label.grid(row=0, column=30, rowspan=1, columnspan=1, padx=5, pady=3)

        # 创建一个文本控件，用于显示多行文本，接收IP
        self.entry_0 = tkinter.Entry(self.fm3_0, width=46, bg='pink', font=('微软雅黑', 12))
        self.entry_0.grid(row=0, column=0, rowspan=1, columnspan=10, padx=2)
        self.entry_0.bind("<Key-Return>", self.press_enter)  # 输入歌单url之后直接按回车键，触发press_enter函数

        # 创建下载按钮
        self.btn_download = tkinter.Button(self.fm3_0, text='开始', command=self.crawl, bg='red', font=('微软雅黑', 12))
        self.btn_download.grid(row=0, column=30, rowspan=1, columnspan=1, padx=5, pady=3)

        # 创建一个文本控件，用于显示多行文本，显示音乐下载信息
        self.text = tkinter.Text(self.fm3, width=110, height=18, font=('微软雅黑', 10))
        self.text.pack(side=tkinter.LEFT, fill=tkinter.Y)

        # 创建一个滚动条
        self.scroll = tkinter.Scrollbar(self.fm3)
        self.scroll.pack(side=tkinter.RIGHT, fill=tkinter.Y)

        # 关联滚动条和文本  config, 相互关联
        self.scroll.config(command=self.text.yview())
        self.text.config(yscrollcomman=self.scroll.set)

        # 创建停止和退出按钮
        btn_stop = tkinter.Button(self.fm4, text='停止', command=self.stop, bg='gray', font=('微软雅黑', 16))
        btn_clean = tkinter.Button(self.fm4, text='清空记录', command=self.clean, bg='gray', font=('微软雅黑', 16))
        btn_quit = tkinter.Button(self.fm4, text='退出', command=self.window.quit, bg='gray', font=('微软雅黑', 16))

        btn_stop.pack(side='left', padx=100, pady=10)
        btn_clean.pack(side='left', padx=80, pady=10)
        btn_quit.pack(side='right', padx=100, pady=10)

    def stop(self):
        MusicSpider.flag = True
        global flag  # 将flag设为全局变量，以便下载过程中能随时获取
        flag = True
        return flag

    def clean(self):
        self.text.delete('1.0', 'end')

    def crawl(self):
        text = self.text
        entry = self.entry
        entry_0 = self.entry_0
        # MusicSpider.MusicSpider.download_songs(self, text, entry)
        mian.action(self, text, entry, entry_0)

    def press_enter(self, even):
        return self.crawl()

    def center_window(self, root, width, height):
        screenwidth = root.winfo_screenwidth()
        screenheight = root.winfo_screenheight()
        size = '%dx%d+%d+%d' % (width, height, (screenwidth - width) / 2, (screenheight - height) / 2)
        # print(size)
        root.geometry(size)

    def run(self):
        # 进入消息循环，显示主窗口
        self.window.mainloop()


if __name__ == '__main__':
    app = Application()
    app.run()