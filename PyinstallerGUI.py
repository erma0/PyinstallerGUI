# -*- encoding: utf-8 -*-
'''
@File    :   PyinstallerGUI.py
@Time    :   2025年04月29日 19:41:13 星期二
@Author  :   erma0
@Version :   1.0
@Link    :   https://github.com/erma0
@Desc    :   仿auto-py-to-exe，使用AI制作的PyinstallerGUI
'''
import logging
import shlex
from urllib.parse import quote

import PyInstaller.__main__
import webview
from PyInstaller.log import logger
# from win32ctypes.pywin32 import pywintypes  # from win32ctypes.pywin32


class API(object):

    def min(self):
        webview.windows[0].minimize()

    def close(self):
        webview.windows[0].destroy()

    def save_content(self, content):
        filename = webview.windows[0].create_file_dialog(webview.SAVE_DIALOG)
        if not filename:
            return

        with open(filename, 'w') as f:
            f.write(content)

    def open_file(self, type, allow_multiple=False):
        if type == 'additional':
            file_types = ("All Files (*.*)",)
        elif type == 'script':
            file_types = ("Python Files (*.py)", "All Files (*.*)")
        elif type == 'icon':
            file_types = ("Icon Files (*.ico)", "All Files (*.*)")
        result = webview.windows[0].create_file_dialog(
            webview.OPEN_DIALOG, directory='/', allow_multiple=allow_multiple, file_types=file_types)
        print('py 打开文件', result)
        return result

    def open_folder(self, allow_multiple=False):
        result = webview.windows[0].create_file_dialog(
            webview.FOLDER_DIALOG, directory='/', allow_multiple=allow_multiple
        )
        print('py 打开文件夹', result)
        return result

    def start_build(self, command_str):
        if command_str is None or command_str == "":
            webview.windows[0].evaluate_js("appendLog('错误：命令字符串为空')")
            return

        try:
            args = shlex.split(command_str)[1:]  # 跳过第一个元素，即 'pyinstaller'

            # 设置 PyInstaller 日志级别
            logger.setLevel(logging.INFO)

            # 添加自定义日志处理函数
            class WebviewLogHandler(logging.Handler):
                def emit(self, record):
                    log_entry = self.format(record)
                    webview.windows[0].evaluate_js(
                        f"appendLog('{quote(log_entry.strip())}')")

            webview_handler = WebviewLogHandler()
            webview_handler.setFormatter(
                logging.Formatter('%(levelname)s: %(message)s'))
            logger.addHandler(webview_handler)

            # 使用 PyInstaller 进行打包
            PyInstaller.__main__.run(args)

            webview.windows[0].evaluate_js("appendLog('打包成功')")
        except Exception as e:
            webview.windows[0].evaluate_js(
                f"appendLog('错误：打包失败 - {quote(str(e))}')")
            raise
        finally:
            # 移除自定义日志处理函数
            if 'webview_handler' in locals():
                logger.removeHandler(webview_handler)


if __name__ == '__main__':
    api = API()
    window = webview.create_window(
        title='PyinstallerGUI',
        url='web/index.html',
        js_api=api,
        resizable=True,
        frameless=False,
        width=650,
        height=750
    )
    webview.start(debug=False)
    print('Window is destroyed')

