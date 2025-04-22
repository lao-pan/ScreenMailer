#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
屏幕截图模块
负责获取屏幕截图，并保存到指定位置
"""

import os
import time
import logging
from datetime import datetime
import PIL.ImageGrab
from PIL import Image

logger = logging.getLogger(__name__)

class ScreenCapture:
    """屏幕截图类"""
    
    def __init__(self, screenshot_dir, config):
        """
        初始化截图模块
        
        Args:
            screenshot_dir (str): 截图保存的目录
            config (dict): 截图相关配置
        """
        self.screenshot_dir = screenshot_dir
        self.format = config.get('format', 'png')
        self.quality = config.get('quality', 90)
        self.bbox = config.get('bbox', None)  # 截取区域，默认全屏
        
        # 确保截图目录存在
        os.makedirs(self.screenshot_dir, exist_ok=True)
        logger.info(f"截图模块初始化完成，截图将保存至: {self.screenshot_dir}")
        
    def capture(self):
        """
        捕获屏幕截图并返回保存的文件路径
        
        Returns:
            str: 保存的截图文件路径
        """
        try:
            # 捕获屏幕
            screenshot = PIL.ImageGrab.grab(bbox=self.bbox)
            
            # 生成文件名
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"screenshot_{timestamp}.{self.format}"
            filepath = os.path.join(self.screenshot_dir, filename)
            
            # 保存截图
            screenshot.save(filepath, format=self.format.upper(), quality=self.quality)
            logger.debug(f"截图已保存: {filepath}")
            return filepath
            
        except Exception as e:
            logger.error(f"截图失败: {str(e)}")
            return None
    
    def capture_multi(self, count=3, interval=0.5):
        """
        连续捕获多张屏幕截图
        
        Args:
            count (int): 截图数量
            interval (float): 截图间隔时间(秒)
            
        Returns:
            list: 保存的截图文件路径列表
        """
        filepaths = []
        for i in range(count):
            filepath = self.capture()
            if filepath:
                filepaths.append(filepath)
            if i < count - 1:
                time.sleep(interval)
        
        return filepaths
    
    def cleanup_screenshots(self, screenshot_paths):
        """
        清理已发送的截图文件
        
        Args:
            screenshot_paths (list): 要清理的截图文件路径列表
        """
        if not screenshot_paths:
            return
            
        count = 0
        for path in screenshot_paths:
            try:
                if os.path.exists(path):
                    os.remove(path)
                    count += 1
                    logger.debug(f"已删除截图: {path}")
            except Exception as e:
                logger.error(f"删除截图失败: {path}, 错误: {str(e)}")
                
        logger.info(f"清理完成，共删除{count}张截图")