#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
配置管理模块
负责读取和管理应用配置
"""

import os
import yaml
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class ConfigManager:
    """配置管理类"""
    
    def __init__(self, config_path):
        """
        初始化配置管理器
        
        Args:
            config_path (str): 配置文件路径
        """
        self.config_path = config_path
        self.config = None
        self.default_config = {
            'email': {
                'smtp_server': '',
                'smtp_port': 587,
                'use_ssl': False,
                'username': '',
                'password': '',
                'sender_email': '',
                'recipients': [],
                'subject_prefix': '[ScreenMailer]'
            },
            'screenshot': {
                'format': 'png',
                'quality': 90,
                'bbox': None
            },
            'scheduler': {
                'screenshot_interval': 300,  # 5分钟
                'screenshot_count': 1,
                'screenshot_delay': 0.5,
                'email_interval': 3600,      # 1小时
                'send_immediate': True
            }
        }
        
        # 加载配置文件
        self.load_config()
        
    def load_config(self):
        """
        加载配置文件
        
        Returns:
            dict: 配置内容
        """
        try:
            # 如果配置文件存在，则从文件加载
            if os.path.exists(self.config_path):
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = yaml.safe_load(f)
                logger.info(f"已从{self.config_path}加载配置")
            else:
                # 如果配置文件不存在，则使用默认配置并创建配置文件
                self.config = self.default_config
                self._create_default_config()
                logger.warning(f"配置文件{self.config_path}不存在，已创建默认配置")
                
            # 验证配置完整性
            self._validate_config()
            
            return self.config
            
        except Exception as e:
            logger.error(f"加载配置文件失败: {str(e)}")
            # 出错时使用默认配置
            self.config = self.default_config
            return self.config
            
    def _create_default_config(self):
        """创建默认配置文件"""
        try:
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 创建带注释的配置文件内容
            config_content = """# ScreenMailer 配置文件
# 由系统自动生成于 {}

# 邮件相关配置
email:
  # SMTP服务器地址（例如：smtp.gmail.com, smtp.qq.com）
  smtp_server: ''
  # SMTP服务器端口，常用端口：587(TLS)或465(SSL)
  smtp_port: 587
  # 是否使用SSL连接，如果端口是465，通常需要设置为true
  use_ssl: false
  # SMTP服务器登录用户名（通常是邮箱地址）
  username: ''
  # SMTP服务器登录密码（对于某些邮件服务商，可能需要使用应用专用密码）
  password: ''
  # 发件人邮箱地址
  sender_email: ''
  # 收件人邮箱地址列表
  recipients: []
  # 邮件主题前缀
  subject_prefix: '[ScreenMailer]'

# 截图相关配置
screenshot:
  # 截图格式，支持：png, jpg, jpeg, bmp
  format: 'png'
  # 图片质量，范围1-100，仅对jpg/jpeg格式有效
  quality: 90
  # 截图区域，格式为[x, y, width, height]，如不指定则截取全屏
  bbox: null

# 调度器配置
scheduler:
  # 截图间隔时间（秒）
  screenshot_interval: 300
  # 每次触发拍摄的截图数量
  screenshot_count: 1
  # 连续截图之间的延迟（秒）
  screenshot_delay: 0.5
  # 发送邮件的间隔时间（秒）
  email_interval: 3600
  # 是否立即发送第一封邮件
  send_immediate: true
""".format(datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            
            # 写入默认配置
            with open(self.config_path, 'w', encoding='utf-8') as f:
                f.write(config_content)
                
            logger.info(f"已创建默认配置文件: {self.config_path}")
            
        except Exception as e:
            logger.error(f"创建默认配置文件失败: {str(e)}")
            
    def _validate_config(self):
        """验证配置完整性，如果缺少项目则使用默认值补充"""
        if not self.config:
            self.config = self.default_config
            return
            
        # 确保顶层配置键存在
        for key in self.default_config:
            if key not in self.config:
                self.config[key] = self.default_config[key]
                logger.warning(f"配置缺少{key}部分，已使用默认值")
                
        # 确保email子配置完整
        for key in self.default_config['email']:
            if key not in self.config['email']:
                self.config['email'][key] = self.default_config['email'][key]
                logger.warning(f"email配置缺少{key}，已使用默认值")
                
        # 确保screenshot子配置完整
        for key in self.default_config['screenshot']:
            if key not in self.config['screenshot']:
                self.config['screenshot'][key] = self.default_config['screenshot'][key]
                logger.warning(f"screenshot配置缺少{key}，已使用默认值")
                
        # 确保scheduler子配置完整
        for key in self.default_config['scheduler']:
            if key not in self.config['scheduler']:
                self.config['scheduler'][key] = self.default_config['scheduler'][key]
                logger.warning(f"scheduler配置缺少{key}，已使用默认值")
    
    def get_config(self):
        """
        获取当前配置
        
        Returns:
            dict: 配置内容
        """
        if not self.config:
            self.load_config()
        return self.config
        
    def save_config(self, new_config=None):
        """
        保存配置到文件
        
        Args:
            new_config (dict, optional): 新的配置内容，如不提供则保存当前配置
            
        Returns:
            bool: 保存成功返回True，失败返回False
        """
        try:
            # 如果提供了新配置，则更新当前配置
            if new_config:
                self.config = new_config
                # 验证配置完整性
                self._validate_config()
                
            # 确保目录存在
            os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
            
            # 写入配置文件
            with open(self.config_path, 'w', encoding='utf-8') as f:
                yaml.dump(self.config, f, default_flow_style=False, sort_keys=False)
                
            logger.info(f"配置已保存到: {self.config_path}")
            return True
            
        except Exception as e:
            logger.error(f"保存配置失败: {str(e)}")
            return False