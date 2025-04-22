# ScreenMailer

一个用于 Windows 虚拟机监控的自动化工具，通过定时截屏和邮件发送功能实现远程监控。配有图形用户界面，支持生成独立可执行文件。

## 功能特点

-   自动定时截取屏幕画面
-   通过电子邮件发送截图
-   图形用户界面(GUI)，易于配置和操作
-   可自定义截图频率和发送时间
-   支持异常检测和告警通知
-   低资源占用，适合在后台长时间运行
-   可打包为独立可执行文件(.exe)，无需安装 Python

## 项目结构

```
ScreenMailer/
│
├── src/                    # 源代码目录
│   ├── screenshot/         # 截图相关功能
│   ├── email/              # 邮件发送功能
│   ├── scheduler/          # 定时任务管理
│   ├── config/             # 配置文件处理
│   └── utils/              # 工具函数
│
├── gui_builder/            # GUI界面和打包相关文件
│   ├── screenmailer_gui.py # 图形界面主程序
│   ├── build_exe.py        # 可执行文件打包脚本
│   ├── create_icon.py      # 图标生成脚本
│   ├── icon_1024.png       # 高分辨率PNG图标
│   └── icon.ico            # 应用程序图标
│
├── config/                 # 配置文件
├── screenshots/            # 临时存储截图的文件夹
├── release/                # 发布版本目录，包含可执行文件
├── tests/                  # 测试代码
└── README.md               # 项目说明文档
```

## 环境要求

### 开发环境

-   Python 3.8 或更高版本
-   Windows 操作系统
-   依赖库：PyQt5, Pillow, PyYAML, schedule, PyInstaller

### 运行环境

-   Windows 操作系统（用于运行.exe 可执行文件）
-   无需安装 Python 或其他依赖（独立可执行文件）

## 安装说明

### 方法 1：直接使用可执行文件

1. 直接从`release`目录获取`ScreenMailer.exe`可执行文件
2. 双击运行即可，无需安装

### 方法 2：从源代码运行

1. 克隆仓库到本地：

```
git clone <repository-url>
cd ScreenMailer
```

2. 安装依赖：

```
pip install -r requirements.txt
```

3. 运行 GUI 版本：

```
python gui_builder/screenmailer_gui.py
```

## 配置说明

### 通过 GUI 配置（推荐）

启动应用程序后，通过图形界面可以方便地设置：

-   邮件服务器设置 (SMTP 服务器、端口、账户等)
-   邮件发送频率和接收者列表
-   截图设置 (质量、格式、区域等)
-   监控计划 (定时发送、立即启动等)

所有配置会自动保存在用户文档目录下的`ScreenMailer/config/config.yaml`中。

### 手动配置

如需手动编辑配置文件，请修改`Documents/ScreenMailer/config/config.yaml`：

```yaml
email:
    smtp_server: smtp.example.com
    smtp_port: 587
    use_ssl: false
    username: your_username
    password: your_password
    sender_email: sender@example.com
    recipients:
        - recipient1@example.com
        - recipient2@example.com
    subject_prefix: "[ScreenMailer]"

screenshot:
    format: png
    quality: 90
    bbox: null # null表示全屏截图，或者提供[左,上,右,下]坐标

scheduler:
    screenshot_interval: 300 # 单位：秒
    screenshot_count: 1
    screenshot_delay: 1
    email_mode: interval # interval, hourly, half_hourly, custom
    email_interval: 3600 # 单位：秒
    email_custom_times:
        - "08:00"
        - "12:00"
        - "18:00"
    send_immediate: true
    send_with_capture: false
```

## 使用方法

### 基本使用

1. 双击运行`ScreenMailer.exe`
2. 在"邮件设置"选项卡中配置邮件服务器和收件人
3. 在"截图设置"选项卡中配置截图参数
4. 在"调度设置"选项卡中设置截图和发送频率
5. 点击"保存配置"按钮保存设置
6. 点击"启动监控"按钮开始监控
7. 监控状态可以在"仪表盘"选项卡中查看
8. 可随时点击"立即截图并发送"按钮进行测试

### 数据存储位置

所有数据（配置、截图、日志）都存储在用户的"文档"文件夹中：

```
Documents/ScreenMailer/
├── config/       # 配置文件
├── logs/         # 日志文件
└── screenshots/  # 截图文件
```

### 开机自启动设置

可以使用 Windows 任务计划程序设置开机自启动：

1. 按 `Win + R` 键，输入 `taskschd.msc` 打开任务计划程序
2. 点击"创建基本任务"
3. 设置名称为"ScreenMailer 自动启动"
4. 触发器选择"计算机启动时"
5. 操作选择"启动程序"
6. 程序/脚本选择 ScreenMailer.exe 的路径
7. 完成设置

## 开发进度

-   [x] 项目结构设计
-   [x] 截图模块开发
-   [x] 邮件发送模块开发
-   [x] 定时器功能实现
-   [x] 配置文件读写
-   [x] 图形用户界面(GUI)实现
-   [x] 打包为可执行文件
-   [ ] 异常检测实现
-   [ ] 完整测试与文档
-   [x] 高分辨率应用图标设计

## 自定义开发

### 生成新的可执行文件

如果您修改了源代码，可以重新生成可执行文件：

```
python gui_builder/build_exe.py
```

### 创建新的应用图标

如需修改应用图标：

```
python gui_builder/create_icon.py
```

## 许可证

MIT

## 作者

[laopan]

## 最后更新

2025 年 4 月 23 日
