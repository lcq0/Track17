import xlrd

from collections import deque
from kuaididanhao import settings
class Excel:
    def read_excel(self):
        # 打开文件
        workbook = xlrd.open_workbook(r''+settings.excel_path)
        print(workbook.sheet_names())
        # sheet1_name = workbook.sheet_names()[0]
        # 根据索引或者名称获取sheet内容
        sheet1 = workbook.sheet_by_index(0)
        # sheet的名称，行数，列数
        print(sheet1.name, sheet1.nrows, sheet1.ncols)
        # 获取整行或整列的值（数组）
        cols3 = sheet1.col_values(2)  # 获取第3列内容
        cols11 = sheet1.col_values(10)  # 获取第11列内容
        # 获取整行或整列的值（数组）
        i = 0
        if sheet1.ncols > 18:
            cols18 = sheet1.col_values(17)  # 获取第18列内容
            cols11 = sheet1.col_values(10)  # 获取第11列内容
            i = 0
            queue_col18 = deque(cols18)
            queue_col11 = deque(cols11)
            while len(queue_col18.pop()) < 1:
                i += 1
            row_len = sheet1.nrows - i
            i = 0
            while i < row_len:
                i += 1
                queue_col11.popleft()
        else:
            cols11 = sheet1.col_values(10)  # 获取第11列内容
            queue_col11 = deque(cols11)
            while i < 2:
                i += 1
                queue_col11.popleft()
        # 获取单元格内容
        track_url = sheet1.cell(2, 12)
        queue_col11.appendleft(track_url)
        # print(queue_col11)
        print(len(queue_col11))
        return queue_col11
    # read_excel("main")