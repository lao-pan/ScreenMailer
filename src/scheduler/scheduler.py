#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
任务调度器模块
负责定时执行屏幕截图和邮件发送任务
"""

import time
import logging
import threading
import schedule
from datetime import datetime

logger = logging.getLogger(__name__)

class Scheduler:
    """任务调度器类"""
    
    def __init__(self, screen_capture, email_sender, config):
        """
        初始化调度器
        
        Args:
            screen_capture: ScreenCapture实例
            email_sender: EmailSender实例
            config (dict): 调度器相关配置
        """
        self.screen_capture = screen_capture
        self.email_sender = email_sender
        self.config = config
        self.is_running = False
        self.thread = None
        
        # 截图相关配置
        self.screenshot_interval = config.get('screenshot_interval', 300)  # 默认5分钟
        self.screenshot_count = config.get('screenshot_count', 1)
        self.screenshot_delay = config.get('screenshot_delay', 0.5)
        
        # 邮件相关配置
        self.email_interval = config.get('email_interval', 3600)  # 默认1小时
        self.send_immediate = config.get('send_immediate', True)
        
        # 保存的截图路径
        self.screenshot_paths = []
        
        logger.info("调度器初始化完成")
        
    def _take_screenshots(self):
        """执行截图任务"""
        logger.info(f"执行截图任务，将连续截取{self.screenshot_count}张截图")
        new_screenshots = self.screen_capture.capture_multi(
            count=self.screenshot_count,
            interval=self.screenshot_delay
        )
        
        if new_screenshots:
            self.screenshot_paths.extend(new_screenshots)
            logger.info(f"截图任务完成，新增{len(new_screenshots)}张截图")
        else:
            logger.warning("截图任务失败，未获取任何截图")
            
        return new_screenshots
        
    def _send_email(self):
        """执行邮件发送任务"""
        if not self.screenshot_paths:
            logger.warning("没有可发送的截图")
            return False
            
        logger.info(f"执行邮件发送任务，将发送{len(self.screenshot_paths)}张截图")
        result = self.email_sender.send_monitor_email(self.screenshot_paths)
        
        if result:
            # 发送成功后清空截图列表
            self.screenshot_paths = []
            
        return result
            
    def _schedule_jobs(self):
        """设置定时任务"""
        # 设置截图任务
        schedule.every(self.screenshot_interval).seconds.do(self._take_screenshots)
        logger.info(f"已设置截图任务，每{self.screenshot_interval}秒执行一次")
        
        # 设置邮件发送任务
        schedule.every(self.email_interval).seconds.do(self._send_email)
        logger.info(f"已设置邮件发送任务，每{self.email_interval}秒执行一次")
        
    def _run_scheduler(self):
        """运行调度器循环"""
        self._schedule_jobs()
        
        # 立即执行一次任务
        if self.send_immediate:
            logger.info("立即执行一次截图和邮件发送任务")
            screenshots = self._take_screenshots()
            if screenshots:
                self._send_email()
        
        # 进入调度循环
        logger.info("调度器开始运行")
        while self.is_running:
            schedule.run_pending()
            time.sleep(1)
            
        logger.info("调度器已停止")
            
    def start(self):
        """启动调度器"""
        if self.is_running:
            logger.warning("调度器已经在运行中")
            return
            
        self.is_running = True
        self.thread = threading.Thread(target=self._run_scheduler)
        self.thread.daemon = True
        self.thread.start()
        
        logger.info("调度器已启动")
        
        # 保持主线程运行
        try:
            while self.is_running:
                time.sleep(1)
        except KeyboardInterrupt:
            self.stop()
            
    def stop(self):
        """停止调度器"""
        if not self.is_running:
            logger.warning("调度器未运行")
            return
            
        self.is_running = False
        if self.thread and self.thread.is_alive():
            self.thread.join(timeout=5)
            
        # 清空调度任务
        schedule.clear()
        
        logger.info("调度器已停止")