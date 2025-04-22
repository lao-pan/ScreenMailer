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
        
        # 邮件发送配置
        self.email_mode = config.get('email_mode', 'interval')  # 'interval', 'hourly', 'half_hourly', 'custom'
        self.email_interval = config.get('email_interval', 3600)  # 默认1小时，当email_mode为interval时使用
        self.email_custom_times = config.get('email_custom_times', [])  # 自定义时间列表，格式为["HH:MM", "HH:MM"]
        self.send_immediate = config.get('send_immediate', True)
        
        # 截图与邮件发送模式
        self.send_with_capture = config.get('send_with_capture', False)  # 截图后立即发送邮件
        
        # 保存的截图路径
        self.screenshot_paths = []
        
        # 当前日志记录
        self.current_log_records = []
        
        logger.info("调度器初始化完成")
        
    def _take_screenshots(self):
        """执行截图任务"""
        logger.info(f"执行截图任务，将连续截取{self.screenshot_count}张截图")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_log_records.append(f"[{timestamp}] 开始执行截图任务")
        
        new_screenshots = self.screen_capture.capture_multi(
            count=self.screenshot_count,
            interval=self.screenshot_delay
        )
        
        if new_screenshots:
            self.screenshot_paths.extend(new_screenshots)
            log_msg = f"截图任务完成，新增{len(new_screenshots)}张截图"
            logger.info(log_msg)
            self.current_log_records.append(f"[{timestamp}] {log_msg}")
            
            # 如果设置为截图后立即发送邮件
            if self.send_with_capture:
                self._send_email()
        else:
            log_msg = "截图任务失败，未获取任何截图"
            logger.warning(log_msg)
            self.current_log_records.append(f"[{timestamp}] {log_msg}")
            
        return new_screenshots
        
    def _send_email(self):
        """执行邮件发送任务"""
        if not self.screenshot_paths:
            log_msg = "没有可发送的截图"
            logger.warning(log_msg)
            self.current_log_records.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {log_msg}")
            return False
            
        logger.info(f"执行邮件发送任务，将发送{len(self.screenshot_paths)}张截图")
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.current_log_records.append(f"[{timestamp}] 开始执行邮件发送任务，包含{len(self.screenshot_paths)}张截图")
        
        # 将当前日志记录传递给邮件发送模块
        result = self.email_sender.send_monitor_email(
            self.screenshot_paths, 
            log_records=self.current_log_records
        )
        
        if result:
            log_msg = "邮件发送成功，清空截图和日志"
            logger.info(log_msg)
            self.current_log_records.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {log_msg}")
            
            # 清空截图列表和日志记录
            self._cleanup_screenshots()
            self.current_log_records = []
            
        else:
            log_msg = "邮件发送失败"
            logger.error(log_msg)
            self.current_log_records.append(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {log_msg}")
            
        return result
    
    def _cleanup_screenshots(self):
        """清理已发送的截图文件"""
        self.screen_capture.cleanup_screenshots(self.screenshot_paths)
        self.screenshot_paths = []
            
    def _schedule_jobs(self):
        """设置定时任务"""
        # 设置截图任务
        schedule.every(self.screenshot_interval).seconds.do(self._take_screenshots)
        logger.info(f"已设置截图任务，每{self.screenshot_interval}秒执行一次")
        
        # 根据不同的邮件发送模式设置任务
        if self.email_mode == 'interval':
            # 按间隔时间发送
            schedule.every(self.email_interval).seconds.do(self._send_email)
            logger.info(f"已设置邮件发送任务，每{self.email_interval}秒执行一次")
            
        elif self.email_mode == 'hourly':
            # 每整点发送
            schedule.every().hour.at(":00").do(self._send_email)
            logger.info("已设置邮件发送任务，每小时整点执行")
            
        elif self.email_mode == 'half_hourly':
            # 每半小时发送
            schedule.every().hour.at(":00").do(self._send_email)
            schedule.every().hour.at(":30").do(self._send_email)
            logger.info("已设置邮件发送任务，每小时的:00和:30执行")
            
        elif self.email_mode == 'custom':
            # 自定义时间发送
            if not self.email_custom_times:
                # 如果没有设置自定义时间，默认每小时发送一次
                logger.warning("未设置自定义发送时间，默认使用每小时整点")
                schedule.every().hour.at(":00").do(self._send_email)
            else:
                for time_str in self.email_custom_times:
                    # 检查时间格式是否正确
                    try:
                        hour, minute = time_str.split(":")
                        int(hour)
                        int(minute)
                        schedule.every().day.at(time_str).do(self._send_email)
                        logger.info(f"已设置邮件发送任务，每天{time_str}执行")
                    except Exception as e:
                        logger.error(f"自定义时间格式错误: {time_str}, {str(e)}")
        
        # 如果设置了截图后立即发送，则不需要额外的邮件发送任务
        if self.send_with_capture:
            logger.info("已设置截图后立即发送邮件模式，不创建单独的邮件发送任务")
        
    def _run_scheduler(self):
        """运行调度器循环"""
        self._schedule_jobs()
        
        # 立即执行一次任务
        if self.send_immediate:
            logger.info("立即执行一次截图任务")
            screenshots = self._take_screenshots()
            
            # 如果不是截图后立即发送模式，且要求立即发送邮件
            if not self.send_with_capture and screenshots:
                logger.info("立即执行一次邮件发送任务")
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
        # 移除主线程阻塞循环，避免卡死GUI
        # 保持主线程运行的循环已删除

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