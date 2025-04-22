#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
ScreenMailer图标生成脚本 - 高分辨率版
创建一个1024x1024分辨率的高质量应用程序图标
"""

import os
from PIL import Image, ImageDraw, ImageFilter, ImageEnhance

def create_icon():
    """创建高分辨率图标"""
    print("正在创建ScreenMailer高分辨率图标...")
    
    # 图标尺寸 - 提高到1024x1024
    size = (1024, 1024)
    
    # 创建空白图像
    image = Image.new('RGBA', size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(image)
    
    # 计算比例
    scale = size[0] / 256  # 相对于原来256x256的缩放比例
    
    # 绘制背景渐变圆形
    center = (size[0] // 2, size[1] // 2)
    radius = int(size[0] * 0.43)  # 设置半径为画布大小的43%
    
    # 创建渐变背景
    for r in range(radius, 0, -1):
        # 从蓝色渐变到深蓝色
        ratio = r / radius
        color = (
            int(0 + (0 - 0) * (1 - ratio)),          # R
            int(120 + (80 - 120) * (1 - ratio)),     # G
            int(212 + (180 - 212) * (1 - ratio)),    # B
            255                                      # A
        )
        circle_bbox = (
            center[0] - r,
            center[1] - r,
            center[0] + r,
            center[1] + r
        )
        draw.ellipse(circle_bbox, fill=color)
    
    # 添加外发光效果
    glow_image = Image.new('RGBA', size, (255, 255, 255, 0))
    glow_draw = ImageDraw.Draw(glow_image)
    
    glow_radius = int(radius * 1.1)
    glow_bbox = (
        center[0] - glow_radius,
        center[1] - glow_radius,
        center[0] + glow_radius,
        center[1] + glow_radius
    )
    glow_draw.ellipse(glow_bbox, fill=(0, 120, 212, 40))
    
    # 应用模糊效果
    glow_image = glow_image.filter(ImageFilter.GaussianBlur(radius=int(20 * scale)))
    
    # 合并图层
    image = Image.alpha_composite(glow_image, image)
    
    # 绘制相机图标 - 更精细的设计
    
    # 相机主体
    camera_width = int(420 * scale)
    camera_height = int(280 * scale)
    camera_top = int((size[1] - camera_height) / 2) - int(20 * scale)
    camera_left = int((size[0] - camera_width) / 2)
    camera_right = camera_left + camera_width
    camera_bottom = camera_top + camera_height
    
    # 相机主体底色 - 深色
    camera_body_dark = (40, 40, 45)
    camera_body_dark_bbox = (
        camera_left,
        camera_top,
        camera_right,
        camera_bottom
    )
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle(camera_body_dark_bbox, radius=int(30 * scale), fill=camera_body_dark)
    
    # 相机主体亮色 - 顶部
    camera_body_light = (60, 60, 65)
    camera_top_section_height = int(70 * scale)
    camera_body_light_bbox = (
        camera_left,
        camera_top,
        camera_right,
        camera_top + camera_top_section_height
    )
    draw.rounded_rectangle(camera_body_light_bbox, radius=int(30 * scale), fill=camera_body_light)
    
    # 相机突出部分（顶部凸起）
    viewfinder_width = int(160 * scale)
    viewfinder_height = int(40 * scale)
    viewfinder_left = int((size[0] - viewfinder_width) / 2)
    viewfinder_top = camera_top - int(viewfinder_height * 0.7)
    viewfinder_right = viewfinder_left + viewfinder_width
    viewfinder_bottom = camera_top + int(viewfinder_height * 0.3)
    
    # 取景器主体
    viewfinder_bbox = (
        viewfinder_left,
        viewfinder_top,
        viewfinder_right,
        viewfinder_bottom
    )
    draw.rounded_rectangle(viewfinder_bbox, radius=int(12 * scale), fill=camera_body_dark)
    
    # 相机镜头
    lens_center_x = size[0] // 2
    lens_center_y = size[1] // 2 + int(10 * scale)
    lens_outer_radius = int(140 * scale)
    lens_middle_radius = int(120 * scale)
    lens_inner_radius = int(100 * scale)
    
    # 镜头外圈
    lens_outer_bbox = (
        lens_center_x - lens_outer_radius,
        lens_center_y - lens_outer_radius,
        lens_center_x + lens_outer_radius,
        lens_center_y + lens_outer_radius
    )
    draw.ellipse(lens_outer_bbox, fill=(25, 25, 28))
    
    # 镜头中圈
    lens_middle_bbox = (
        lens_center_x - lens_middle_radius,
        lens_center_y - lens_middle_radius,
        lens_center_x + lens_middle_radius,
        lens_center_y + lens_middle_radius
    )
    draw.ellipse(lens_middle_bbox, fill=(35, 35, 38))
    
    # 镜头内圈
    lens_inner_bbox = (
        lens_center_x - lens_inner_radius,
        lens_center_y - lens_inner_radius,
        lens_center_x + lens_inner_radius,
        lens_center_y + lens_inner_radius
    )
    draw.ellipse(lens_inner_bbox, fill=(45, 45, 48))
    
    # 镜头玻璃部分
    lens_glass_radius = int(80 * scale)
    lens_glass_bbox = (
        lens_center_x - lens_glass_radius,
        lens_center_y - lens_glass_radius,
        lens_center_x + lens_glass_radius,
        lens_center_y + lens_glass_radius
    )
    
    # 创建镜头渐变效果
    for r in range(lens_glass_radius, 0, -1):
        ratio = r / lens_glass_radius
        blue_value = int(130 + (230 - 130) * (1 - ratio))
        color = (0, 80, blue_value, 255)
        glass_bbox = (
            lens_center_x - r,
            lens_center_y - r,
            lens_center_x + r,
            lens_center_y + r
        )
        draw.ellipse(glass_bbox, fill=color)
    
    # 添加闪光灯
    flash_size = int(40 * scale)
    flash_left = camera_right - int(100 * scale)
    flash_top = camera_top + int(30 * scale)
    flash_bbox = (
        flash_left,
        flash_top,
        flash_left + flash_size,
        flash_top + flash_size
    )
    
    # 闪光灯底色
    draw.ellipse(flash_bbox, fill=(255, 255, 200))
    
    # 闪光灯高光效果
    flash_highlight_size = int(flash_size * 0.6)
    flash_highlight_left = flash_left + int((flash_size - flash_highlight_size) / 2)
    flash_highlight_top = flash_top + int((flash_size - flash_highlight_size) / 2)
    flash_highlight_bbox = (
        flash_highlight_left,
        flash_highlight_top,
        flash_highlight_left + flash_highlight_size,
        flash_highlight_top + flash_highlight_size
    )
    draw.ellipse(flash_highlight_bbox, fill=(255, 255, 230))
    
    # 添加邮件图标
    envelope_width = int(250 * scale)
    envelope_height = int(150 * scale)
    envelope_left = int((size[0] - envelope_width) / 2)
    envelope_top = size[1] - envelope_height - int(120 * scale)  # 位置在画面下部
    
    # 邮件信封底色
    envelope_color = (240, 240, 240)
    draw.rounded_rectangle(
        (envelope_left, envelope_top,
         envelope_left + envelope_width, envelope_top + envelope_height),
        radius=int(20 * scale),
        fill=envelope_color
    )
    
    # 邮件信封上的折叠线
    fold_color = (200, 200, 200)
    # 中间折线
    draw.line(
        (envelope_left, envelope_top + envelope_height // 2,
         envelope_left + envelope_width, envelope_top + envelope_height // 2),
        fill=fold_color,
        width=int(3 * scale)
    )
    
    # 斜折线 - 左上到中间
    draw.line(
        (envelope_left, envelope_top,
         envelope_left + envelope_width // 2, envelope_top + envelope_height // 2),
        fill=fold_color,
        width=int(3 * scale)
    )
    
    # 斜折线 - 右上到中间
    draw.line(
        (envelope_left + envelope_width, envelope_top,
         envelope_left + envelope_width // 2, envelope_top + envelope_height // 2),
        fill=fold_color,
        width=int(3 * scale)
    )
    
    # 添加邮件图标的阴影
    shadow_offset = int(8 * scale)
    envelope_shadow = Image.new('RGBA', size, (0, 0, 0, 0))
    shadow_draw = ImageDraw.Draw(envelope_shadow)
    shadow_draw.rounded_rectangle(
        (envelope_left + shadow_offset, envelope_top + shadow_offset,
         envelope_left + envelope_width + shadow_offset, envelope_top + envelope_height + shadow_offset),
        radius=int(20 * scale),
        fill=(0, 0, 0, 80)
    )
    envelope_shadow = envelope_shadow.filter(ImageFilter.GaussianBlur(radius=int(10 * scale)))
    
    # 合并阴影与原图
    image = Image.alpha_composite(envelope_shadow, image)
    
    # 轻微的整体增强
    enhancer = ImageEnhance.Contrast(image)
    image = enhancer.enhance(1.05)
    
    enhancer = ImageEnhance.Brightness(image)
    image = enhancer.enhance(1.02)
    
    # 保存为高分辨率PNG和ICO文件
    current_dir = os.path.dirname(os.path.abspath(__file__))
    tools_dir = os.path.dirname(current_dir)
    assets_dir = os.path.join(tools_dir, "assets")
    
    # 确保assets目录存在
    if not os.path.exists(assets_dir):
        os.makedirs(assets_dir, exist_ok=True)
    
    # 更新文件保存路径
    png_path = os.path.join(assets_dir, "icon_1024.png")
    icon_path = os.path.join(assets_dir, "icon.ico")
    
    # 保存PNG
    image.save(png_path)
    print(f"高分辨率PNG图标已保存: {png_path}")
    
    # 创建不同尺寸的图标版本
    icon_sizes = [1024, 512, 256, 128, 64, 32, 16]
    icons = []
    
    for s in icon_sizes:
        if s == 1024:
            icons.append(image)
        else:
            icons.append(image.resize((s, s), Image.Resampling.LANCZOS))
    
    # 保存为ICO文件，包含多个尺寸
    icons[0].save(icon_path, format='ICO', 
                 sizes=[(s, s) for s in icon_sizes],
                 append_images=icons[1:])
    
    print(f"ICO图标文件已保存: {icon_path}")
    return icon_path

if __name__ == "__main__":
    create_icon()