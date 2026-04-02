"""
测试漫画网站路由
将测试漫画网站集成到Flask应用中
访问地址: http://localhost:5000/test_comic/
"""

from flask import render_template, send_from_directory, Blueprint
import os

# 创建蓝图
test_comic_bp = Blueprint('test_comic', __name__, url_prefix='/test_comic')

TEST_COMIC_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'test_comic_site')


@test_comic_bp.route('/')
def test_comic_index():
    """测试漫画首页"""
    return send_from_directory(TEST_COMIC_DIR, 'index.html')


@test_comic_bp.route('/chapter.html')
def test_comic_chapter():
    """测试漫画章节页"""
    return send_from_directory(TEST_COMIC_DIR, 'chapter.html')


@test_comic_bp.route('/<path:filename>')
def test_comic_static(filename):
    """提供测试漫画静态文件（图片等）"""
    return send_from_directory(TEST_COMIC_DIR, filename)
