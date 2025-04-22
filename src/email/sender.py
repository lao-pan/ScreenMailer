#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
邮件发送模块
负责将截图通过邮件发送
"""

import os
import smtplib
import logging
import platform
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.image import MIMEImage
from datetime import datetime

logger = logging.getLogger(__name__)

class EmailSender:
    """邮件发送类"""
    
    def __init__(self, config):
        """
        初始化邮件发送模块
        
        Args:
            config (dict): 邮件相关配置
        """
        self.smtp_server = config.get('smtp_server')
        self.smtp_port = config.get('smtp_port', 587)
        self.use_ssl = config.get('use_ssl', False)
        self.username = config.get('username')
        self.password = config.get('password')
        self.sender_email = config.get('sender_email', self.username)
        self.recipients = config.get('recipients', [])
        self.subject_prefix = config.get('subject_prefix', '[ScreenMailer]')
        
        if not self.smtp_server or not self.username or not self.password:
            raise ValueError("邮件服务器配置不完整")
        
        logger.info("邮件发送模块初始化完成")
    
    def send_email(self, subject, message, screenshot_paths=None, log_records=None):
        """
        发送带有截图附件的邮件
        
        Args:
            subject (str): 邮件主题
            message (str): 邮件正文
            screenshot_paths (list): 截图文件路径列表
            log_records (list): 日志记录列表
            
        Returns:
            bool: 发送成功返回True，失败返回False
        """
        if not self.recipients:
            logger.warning("未配置收件人，邮件未发送")
            return False
            
        try:
            # 创建邮件
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = ', '.join(self.recipients)
            msg['Subject'] = f"{self.subject_prefix} {subject}"
            
            # 如果有日志记录，添加到邮件正文
            if log_records:
                message += self._format_logs_for_email(log_records)
            
            # 添加正文
            msg.attach(MIMEText(message, 'plain'))
            
            # 添加截图附件
            if screenshot_paths and isinstance(screenshot_paths, list):
                for i, path in enumerate(screenshot_paths):
                    if os.path.exists(path):
                        with open(path, 'rb') as f:
                            img_data = f.read()
                            image = MIMEImage(img_data)
                            image.add_header('Content-Disposition', 
                                            'attachment', 
                                            filename=os.path.basename(path))
                            msg.attach(image)
                    else:
                        logger.warning(f"截图文件不存在: {path}")
            
            # 连接到SMTP服务器
            if self.use_ssl:
                smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
            else:
                smtp = smtplib.SMTP(self.smtp_server, self.smtp_port)
                smtp.starttls()
            
            # 登录
            smtp.login(self.username, self.password)
            
            # 发送邮件
            smtp.send_message(msg)
            smtp.quit()
            
            logger.info(f"邮件发送成功，收件人: {len(self.recipients)}人")
            return True
            
        except Exception as e:
            logger.error(f"邮件发送失败: {str(e)}")
            return False
    
    def _format_logs_for_email(self, log_records):
        """
        格式化日志记录为邮件正文格式
        
        Args:
            log_records (list): 日志记录列表
            
        Returns:
            str: 格式化后的日志文本
        """
        if not log_records:
            return ""
            
        log_text = "\n\n=====LOGS=====\n"
        for record in log_records:
            log_text += f"{record}\n"
        log_text += "=============\n"
        
        return log_text
            
    def send_monitor_email(self, screenshot_paths, log_records=None):
        """
        发送监控邮件
        
        Args:
            screenshot_paths (list): 截图文件路径列表
            log_records (list): 日志记录列表
            
        Returns:
            bool: 发送成功返回True，失败返回False
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"监控截图 - {timestamp}"
        
        # 获取系统信息
        system_info = platform.system()
        hostname = platform.node()
        
        message = f"""=====基本情况=======
主机名称: {hostname}
操作系统: {system_info}
截图时间: {timestamp}
截图数量: {len(screenshot_paths) if screenshot_paths else 0}
邮件生成时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
---------------------
"""
        
        # 在邮件末尾添加签名
        message += "\n---\n此邮件由ScreenMailer系统自动发送，请勿回复。"
        
        return self.send_email(subject, message, screenshot_paths, log_records)
        
    def send_alert_email(self, message, screenshot_paths=None, log_records=None):
        """
        发送告警邮件
        
        Args:
            message (str): 告警信息
            screenshot_paths (list): 截图文件路径列表
            log_records (list): 日志记录列表
            
        Returns:
            bool: 发送成功返回True，失败返回False
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"告警通知 - {timestamp}"
        
        # 获取系统信息
        system_info = platform.system()
        hostname = platform.node()
        
        alert_message = f"""=====告警信息=======
【告警】来自ScreenMailer的告警通知！

主机名称: {hostname}
操作系统: {system_info}
告警时间: {timestamp}
告警信息: {message}
---------------------
"""
        
        # 在邮件末尾添加签名
        alert_message += "\n---\n此邮件由ScreenMailer系统自动发送，请勿回复。"
        
        return self.send_email(subject, alert_message, screenshot_paths, log_records)