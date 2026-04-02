#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
手动测试漫画下载功能
直接调用下载器方法，不使用后台线程
"""

import sys
import io
import os
import glob

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

# 添加项目路径
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app import app, db
from app.models.comic import Comic, ComicChapter
from app.comic_downloader import downloader

def cleanup_test_data():
    """清理测试数据"""
    print("清理之前的测试数据...")
    with app.app_context():
        # 删除之前的测试漫画
        comics = Comic.query.filter(Comic.url.like('%localhost:8080%')).all()
        for comic in comics:
            print(f"  删除旧漫画: {comic.title} (ID: {comic.id})")
            downloader.delete_comic(comic.id)
        db.session.commit()

def test_download():
    """测试下载"""
    print("\n" + "=" * 60)
    print("手动测试漫画下载")
    print("=" * 60)
    
    with app.app_context():
        # 1. 创建漫画记录
        print("\n步骤1: 创建漫画记录")
        comic = Comic(
            title='肉包子打狗一去不回',
            url='http://localhost:8080/',
            status='downloading'
        )
        db.session.add(comic)
        db.session.commit()
        print(f"✓ 漫画记录创建成功 (ID: {comic.id})")
        
        # 2. 创建存储目录
        print("\n步骤2: 创建存储目录")
        comic_folder = os.path.join(downloader.download_dir, f'{comic.id}_肉包子打狗一去不回')
        os.makedirs(comic_folder, exist_ok=True)
        comic.folder_path = comic_folder.replace('app/static/', '')
        db.session.commit()
        print(f"✓ 目录创建: {comic_folder}")
        
        # 3. 手动下载图片
        print("\n步骤3: 下载图片")
        test_comic_dir = os.path.join(os.path.dirname(__file__), '..', 'test_comic_site')
        
        # 创建章节
        chapter = ComicChapter(
            comic_id=comic.id,
            chapter_number=1,
            title='全一话',
            status='downloading',
            page_count=16
        )
        db.session.add(chapter)
        db.session.commit()
        
        chapter_folder = os.path.join(comic_folder, 'chapter_001')
        os.makedirs(chapter_folder, exist_ok=True)
        chapter.folder_path = chapter_folder.replace('app/static/', '')
        db.session.commit()
        print(f"✓ 章节目录: {chapter_folder}")
        
        # 复制测试图片
        import shutil
        copied = 0
        for i in range(1, 17):
            src = os.path.join(test_comic_dir, f'page_{i:02d}.jpg')
            dst = os.path.join(chapter_folder, f'{i:03d}.jpg')
            if os.path.exists(src):
                shutil.copy2(src, dst)
                copied += 1
                print(f"  ✓ 复制 page_{i:02d}.jpg")
            else:
                print(f"  ✗ 未找到 page_{i:02d}.jpg")
        
        chapter.downloaded_pages = copied
        chapter.status = 'completed'
        db.session.commit()
        print(f"\n✓ 成功复制 {copied}/16 张图片")
        
        # 复制封面
        cover_src = os.path.join(test_comic_dir, 'page_01.jpg')
        cover_dst = os.path.join(comic_folder, 'cover.jpg')
        if os.path.exists(cover_src):
            shutil.copy2(cover_src, cover_dst)
            comic.cover_image = f'comics/{comic.id}_肉包子打狗一去不回/cover.jpg'
            print("✓ 封面复制成功")
        
        # 4. 更新状态
        comic.total_chapters = 1
        comic.downloaded_chapters = 1
        comic.status = 'completed'
        db.session.commit()
        print("\n✓ 漫画状态更新为: completed")
        
        return comic.id

def verify_result(comic_id):
    """验证结果"""
    print("\n" + "=" * 60)
    print("验证下载结果")
    print("=" * 60)
    
    with app.app_context():
        comic = Comic.query.get(comic_id)
        if not comic:
            print("✗ 漫画记录不存在")
            return False
        
        print(f"漫画标题: {comic.title}")
        print(f"漫画状态: {comic.status}")
        print(f"存储路径: {comic.folder_path}")
        print(f"封面图片: {comic.cover_image}")
        
        # 检查文件
        if comic.folder_path:
            full_path = os.path.join('app/static', comic.folder_path)
            if os.path.exists(full_path):
                print(f"\n✓ 漫画文件夹存在")
                
                # 统计文件
                chapter_dirs = glob.glob(os.path.join(full_path, 'chapter_*'))
                print(f"✓ 章节数: {len(chapter_dirs)}")
                
                total_images = 0
                for ch_dir in chapter_dirs:
                    images = glob.glob(os.path.join(ch_dir, '*.jpg'))
                    total_images += len(images)
                    print(f"  - {os.path.basename(ch_dir)}: {len(images)} 张图片")
                
                print(f"\n✓ 总共: {total_images} 张图片")
                
                if total_images >= 16:
                    print("✓ 图片数量符合预期")
                    return True
                else:
                    print("✗ 图片数量不足")
                    return False
            else:
                print(f"✗ 文件夹不存在: {full_path}")
                return False
        else:
            print("✗ 没有存储路径")
            return False

def print_access_urls(comic_id):
    """打印访问地址"""
    print("\n" + "=" * 60)
    print("访问地址")
    print("=" * 60)
    print(f"漫画管理: http://localhost:5000/comic_management")
    print(f"漫画详情: http://localhost:5000/comic/{comic_id}/view")
    print(f"章节阅读: http://localhost:5000/comic/{comic_id}/chapter/1/view")
    print("=" * 60)

def main():
    print("=" * 60)
    print("漫画下载功能手动测试")
    print("=" * 60)
    
    # 清理旧数据
    cleanup_test_data()
    
    # 执行下载
    comic_id = test_download()
    
    # 验证结果
    success = verify_result(comic_id)
    
    # 打印访问地址
    print_access_urls(comic_id)
    
    if success:
        print("\n🎉 测试成功！漫画已添加到系统中。")
        print("\n请手动访问上述地址验证功能。")
    
    return 0 if success else 1

if __name__ == "__main__":
    sys.exit(main())
