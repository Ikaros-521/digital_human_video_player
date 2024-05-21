# 导入所需的库
import re, random, requests, json
import time
import os, shutil
import logging
from datetime import datetime
from datetime import timedelta
from datetime import timezone
import traceback

from urllib.parse import urlparse


class Common:
    def __init__(self):  
        self.count = 1

    """
    数字操作
    """

    # 获取北京时间
    def get_bj_time(self, type=0):
        """获取北京时间

        Args:
            type (int, str): 返回时间类型. 默认为 0.
                0 返回数据：年-月-日 时:分:秒
                1 返回数据：年-月-日
                2 返回数据：当前时间的秒
                3 返回数据：自1970年1月1日以来的秒数
                4 返回数据：根据调用次数计数到100循环
                5 返回数据：当前 时点分
                6 返回数据：当前时间的 时, 分
                7 返回数据：年-月-日 时-分-秒 毫秒

        Returns:
            str: 返回指定格式的时间字符串
            int, int
        """
        if type == 0:
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)  # 获取当前 UTC 时间
            SHA_TZ = timezone(
                timedelta(hours=8),
                name='Asia/Shanghai',
            )
            beijing_now = utc_now.astimezone(SHA_TZ)  # 将 UTC 时间转换为北京时间
            fmt = '%Y-%m-%d %H:%M:%S'
            now_fmt = beijing_now.strftime(fmt)
            return now_fmt
        elif type == 1:
            now = datetime.now()  # 获取当前时间
            year = now.year  # 获取当前年份
            month = now.month  # 获取当前月份
            day = now.day  # 获取当前日期

            return str(year) + "-" + str(month) + "-" + str(day)
        elif type == 2:
            now = time.localtime()  # 获取当前时间

            # hour = now.tm_hour   # 获取当前小时
            # minute = now.tm_min  # 获取当前分钟 
            second = now.tm_sec  # 获取当前秒数

            return str(second)
        elif type == 3:
            current_time = time.time()  # 返回自1970年1月1日以来的秒数

            return str(current_time)
        elif type == 4:
            self.count = (self.count % 100) + 1

            return str(self.count)
        elif type == 5:
            now = time.localtime()  # 获取当前时间

            hour = now.tm_hour   # 获取当前小时
            minute = now.tm_min  # 获取当前分钟

            return str(hour) + "点" + str(minute) + "分"
        elif type == 6:
            now = time.localtime()  # 获取当前时间

            hour = now.tm_hour   # 获取当前小时
            minute = now.tm_min  # 获取当前分钟 

            return hour, minute
        elif type == 7:
            utc_now = datetime.utcnow().replace(tzinfo=timezone.utc)  # 获取当前 UTC 时间
            SHA_TZ = timezone(
                timedelta(hours=8),
                name='Asia/Shanghai',
            )
            beijing_now = utc_now.astimezone(SHA_TZ)  # 将 UTC 时间转换为北京时间
            fmt = '%Y-%m-%d %H-%M-%S %f'
            now_fmt = beijing_now.strftime(fmt)
            return now_fmt
    
    def move_and_rename(self, src_file_path, target_dir, new_filename=None, max_attempts=3, move_file=True):
        """
        移动或复制文件到指定目录，可选地重命名文件。
        
        :param src_file_path: 源文件的完整路径
        :param target_dir: 目标目录的路径
        :param new_filename: 可选的新文件名（不包括目录路径）
        :param max_attempts: 最大重试次数（默认为3）
        :param move_file: 如果为True则移动文件，否则复制文件
        """

        # 确保目标目录存在
        if not os.path.exists(target_dir):
            os.makedirs(target_dir)

        # 如果提供了新文件名，则使用它；否则，保持文件的原始名称
        filename = new_filename if new_filename else os.path.basename(src_file_path)
        target_file_path = os.path.join(target_dir, filename)
        logging.debug(f"target_dir={target_dir}, target_file_path={target_file_path}")

        # 尝试移动或复制文件，如果文件被其他程序占用，则进行重试
        attempts = 0
        retry_delay = 0.5

        while attempts < max_attempts:
            try:
                # 如果源文件不存在，则直接返回False
                if not os.path.exists(src_file_path):
                    logging.error(f"文件移动失败: 源文件{src_file_path}不存在")
                    return False
                
                if move_file:
                    shutil.move(src_file_path, target_file_path)
                    logging.info(f"文件:{src_file_path} 已移动到:{target_file_path}")
                else:
                    shutil.copy2(src_file_path, target_file_path)
                    logging.info(f"文件:{src_file_path} 已复制到:{target_file_path}")
                
                return True
            except Exception as e:
                logging.error(f"文件操作失败: {e}")
                logging.info("重试中...")
                attempts += 1
                time.sleep(retry_delay)

        logging.warning(f"达到最大重试次数({max_attempts})，无法操作文件: {src_file_path}")
        return False

        
    
    def get_filename_with_ext(self, filepath):
        """
        获取文件路径中的文件名，包括扩展名

        Args:
            filepath: 文件路径

        Returns:
            文件名，包括扩展名
        """
        import os

        filename = os.path.basename(filepath)
        return filename