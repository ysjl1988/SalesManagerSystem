#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
生成测试漫画图片 - "肉包子打狗一去不回"
16页故事漫画
"""

import os
import sys
import io

# 设置stdout编码为utf-8
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

from PIL import Image, ImageDraw, ImageFont

# 故事内容
STORY_PAGES = [
    ("从前，有个小贩在街边\n卖肉包子...", "小贩推着包子车，热气腾腾"),
    ("这时，一只流浪狗\n走了过来...", "狗狗眼巴巴地看着包子"),
    ("它看起来又饿又可怜", "狗狗摇着尾巴，眼含期待"),
    ("小贩心想：\n这狗挺可怜的...", "小贩看着狗狗，心生怜悯"),
    ("于是，他拿起一个\n热腾腾的肉包子", "小贩拿起一个包子"),
    ('"来，给你吃吧！"\n小贩把包子扔给狗', "包子飞向狗狗"),
    ("狗狗接住包子，\n转身就跑！", "狗狗叼着包子跑开"),
    ('小贩大喊：\n"喂！你怎么跑了？"', "小贩伸出手，一脸惊讶"),
    ("狗狗头也不回，\n消失在街角...", "狗狗跑远的背影"),
    ('旁边的大爷笑了：\n"年轻人..."', "大爷捋着胡子微笑"),
    ('"你这是肉包子打狗啊！"', "大爷指着跑远的狗"),
    ('小贩纳闷：\n"什么意思？"', "小贩挠挠头不解"),
    ('大爷解释：\n"肉包子打狗——一去不回啊！"', "大爷笑着解释"),
    ("这时，狗狗\n又回来了！", "狗狗跑回来的身影"),
    ("还带着一只\n小狗...", "狗妈妈带着小狗"),
    ("原来它带给孩子吃的！\n小贩感动地又给了几个包子", "温馨的结局"),
]

# 背景色列表（暖色调）
BG_COLORS = [
    (255, 245, 230),  # 暖白
    (255, 240, 220),  # 淡黄
    (255, 235, 210),  # 米色
    (255, 230, 200),  # 浅橙
    (255, 225, 190),  # 杏色
    (255, 240, 215),  # 奶油
    (255, 235, 205),  # 浅黄
    (255, 230, 195),  # 淡橙
    (255, 245, 225),  # 象牙
    (255, 240, 210),  # 暖米
    (255, 235, 200),  # 浅杏
    (255, 230, 190),  # 淡黄
    (255, 245, 220),  # 乳白
    (255, 240, 205),  # 暖色
    (255, 235, 195),  # 浅暖
    (255, 248, 230),  # 温馨
]


def get_font(size):
    """获取字体，尝试多种中文字体"""
    font_paths = [
        "C:/Windows/Fonts/simhei.ttf",  # 黑体
        "C:/Windows/Fonts/simsun.ttc",  # 宋体
        "C:/Windows/Fonts/msyh.ttc",    # 微软雅黑
        "C:/Windows/Fonts/simkai.ttf",  # 楷体
    ]
    
    for path in font_paths:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size)
            except:
                continue
    
    # 回退到默认字体
    return ImageFont.load_default()


def draw_simple_scene(draw, page_num, width, height):
    """绘制简单的场景元素"""
    # 根据页面绘制不同元素
    
    if page_num == 0:  # 小贩推车
        # 包子车
        draw.rectangle([150, 400, 350, 600], fill=(139, 90, 43), outline=(100, 60, 30), width=3)
        draw.ellipse([160, 420, 200, 460], fill=(255, 200, 150), outline=(200, 150, 100), width=2)
        draw.ellipse([210, 420, 250, 460], fill=(255, 200, 150), outline=(200, 150, 100), width=2)
        draw.ellipse([260, 420, 300, 460], fill=(255, 200, 150), outline=(200, 150, 100), width=2)
        # 热气
        for i in range(3):
            x = 180 + i * 40
            draw.arc([x, 380, x+30, 420], 0, 180, fill=(200, 200, 200), width=2)
    
    elif page_num == 1:  # 狗狗看着
        # 狗狗简笔画
        draw.ellipse([250, 450, 400, 550], fill=(210, 180, 140), outline=(150, 120, 80), width=3)
        draw.ellipse([280, 470, 310, 500], fill=(255, 255, 255), outline=(150, 120, 80), width=2)  # 眼睛
        draw.ellipse([290, 480, 300, 490], fill=(0, 0, 0))  # 眼珠
        draw.ellipse([340, 470, 370, 500], fill=(255, 255, 255), outline=(150, 120, 80), width=2)
        draw.ellipse([350, 480, 360, 490], fill=(0, 0, 0))
        draw.polygon([(320, 510), (330, 530), (310, 530)], fill=(0, 0, 0))  # 鼻子
    
    elif page_num == 5:  # 扔包子
        draw.ellipse([300, 450, 360, 510], fill=(255, 200, 150), outline=(200, 150, 100), width=2)
        # 运动轨迹
        draw.line([(250, 480), (300, 480)], fill=(255, 180, 120), width=3)
    
    elif page_num == 6:  # 狗狗跑
        draw.ellipse([350, 450, 500, 520], fill=(210, 180, 140), outline=(150, 120, 80), width=3)
        # 速度线
        for i in range(3):
            draw.line([(300+i*20, 460), (330+i*20, 460)], fill=(100, 100, 100), width=2)
    
    elif page_num == 9:  # 大爷
        draw.ellipse([200, 400, 300, 500], fill=(255, 220, 180), outline=(200, 170, 130), width=2)
        draw.arc([220, 440, 280, 470], 0, 180, fill=(100, 50, 50), width=2)  # 微笑
        # 胡子
        draw.arc([210, 450, 290, 480], 20, 160, fill=(150, 150, 150), width=2)
    
    elif page_num == 13:  # 狗狗回来
        draw.ellipse([200, 450, 350, 520], fill=(210, 180, 140), outline=(150, 120, 80), width=3)
        # 返回箭头
        draw.polygon([(280, 400), (300, 420), (260, 420)], fill=(100, 200, 100))
    
    elif page_num == 14:  # 小狗
        draw.ellipse([200, 480, 280, 540], fill=(210, 180, 140), outline=(150, 120, 80), width=2)
        draw.ellipse([300, 480, 380, 540], fill=(180, 150, 110), outline=(130, 100, 70), width=2)
    
    elif page_num == 15:  # 温馨结局 - 多个包子
        for i in range(5):
            x = 150 + i * 60
            draw.ellipse([x, 500, x+50, 550], fill=(255, 200, 150), outline=(200, 150, 100), width=2)
    
    else:
        # 默认装饰 - 简单的边框装饰
        draw.rectangle([50, 350, width-50, height-150], outline=(200, 180, 160), width=2)


def create_comic_page(page_num, text, scene_desc, output_dir):
    """创建单页漫画"""
    width, height = 800, 1200
    
    # 创建背景
    bg_color = BG_COLORS[page_num]
    img = Image.new('RGB', (width, height), bg_color)
    draw = ImageDraw.Draw(img)
    
    # 获取字体
    title_font = get_font(48)
    page_font = get_font(24)
    small_font = get_font(18)
    
    # 绘制页码
    draw.text((width - 80, 30), f"{page_num + 1}/16", fill=(150, 130, 110), font=page_font)
    
    # 绘制主标题（故事文字）
    # 计算文字位置（居中偏上）
    text_y = 80
    lines = text.split('\n')
    for line in lines:
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        draw.text((text_x, text_y), line, fill=(80, 60, 50), font=title_font)
        bbox = draw.textbbox((0, 0), line, font=title_font)
        text_y += bbox[3] - bbox[1] + 10
    
    # 绘制场景插图区域
    draw_simple_scene(draw, page_num, width, height)
    
    # 绘制场景描述（底部）
    desc_y = height - 100
    bbox = draw.textbbox((0, 0), scene_desc, font=small_font)
    desc_width = bbox[2] - bbox[0]
    desc_x = (width - desc_width) // 2
    draw.text((desc_x, desc_y), scene_desc, fill=(150, 130, 110), font=small_font)
    
    # 绘制装饰边框
    draw.rectangle([20, 20, width-20, height-20], outline=(200, 180, 160), width=3)
    
    # 保存
    output_path = os.path.join(output_dir, f"page_{page_num+1:02d}.jpg")
    img.save(output_path, "JPEG", quality=90)
    print(f"✓ 生成: {output_path}")
    return output_path


def generate_comic(output_dir="test_comic"):
    """生成完整漫画"""
    print("=" * 50)
    print('生成测试漫画: "肉包子打狗一去不回"')
    print("=" * 50)
    
    # 创建输出目录
    os.makedirs(output_dir, exist_ok=True)
    
    # 生成16页
    for i, (text, scene) in enumerate(STORY_PAGES):
        create_comic_page(i, text, scene, output_dir)
    
    print("=" * 50)
    print(f"✅ 漫画生成完成！共16页")
    print(f"📁 输出目录: {os.path.abspath(output_dir)}")
    print("=" * 50)
    
    return output_dir


if __name__ == "__main__":
    generate_comic()
