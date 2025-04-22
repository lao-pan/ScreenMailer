#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
邮件发送模块
负责将截图通过邮件发送
"""

import os
import smtplib
import logging
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
    
    def send_email(self, subject, message, screenshot_paths=None):
        """
        发送带有截图附件的邮件
        
        Args:
            subject (str): 邮件主题
            message (str): 邮件正文
            screenshot_paths (list): 截图文件路径列表
            
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
            
    def send_monitor_email(self, screenshot_paths):
        """
        发送监控邮件
        
        Args:
            screenshot_paths (list): 截图文件路径列表
            
        Returns:
            bool: 发送成功返回True，失败返回False
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"监控截图 - {timestamp}"
        message = f"""
这是来自ScreenMailer的自动监控邮件。

截图时间: {timestamp}
截图数量: {len(screenshot_paths) if screenshot_paths else 0}

---
此邮件由系统自动发送，请勿回复。
        """
        
        return self.send_email(subject, message, screenshot_paths)
        
    def send_alert_email(self, message, screenshot_paths=None):
        """
        发送告警邮件
        
        Args:
            message (str): 告警信息
            screenshot_paths (list): 截图文件路径列表
            
        Returns:
            bool: 发送成功返回True，失败返回False
        """
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        subject = f"告警通知 - {timestamp}"
        alert_message = f"""
【告警】来自ScreenMailer的告警通知！

时间: {timestamp}
告警信息: {message}

---
此邮件由系统自动发送，请勿回复。
        """
        
        return self.send_email(subject, alert_message, screenshot_paths)