"""
漫画管理路由
仅管理员可访问
"""

from flask import render_template, request, jsonify, flash, redirect, url_for, send_from_directory
from app import app, db
from app.models.comic import Comic, ComicChapter
from app.comic_downloader import downloader
from app.decorators import admin_required
import os


@app.route('/comic_management')
@admin_required
def comic_management():
    """漫画管理页面"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 12, type=int)
    status = request.args.get('status', '')
    search = request.args.get('search', '')
    
    # 构建查询
    query = Comic.query
    
    if status:
        query = query.filter_by(status=status)
    
    if search:
        query = query.filter(Comic.title.contains(search))
    
    # 按创建时间倒序排列
    query = query.order_by(Comic.created_at.desc())
    
    # 分页
    comics = query.paginate(page=page, per_page=per_page, error_out=False)
    
    return render_template('comic_management.html', comics=comics)


@app.route('/comic/add', methods=['POST'])
@admin_required
def comic_add():
    """添加漫画下载任务"""
    url = request.form.get('url', '').strip()
    title = request.form.get('title', '').strip()
    
    if not url:
        flash('请输入漫画链接地址', 'danger')
        return redirect(url_for('comic_management'))
    
    # 验证URL格式
    if not url.startswith(('http://', 'https://')):
        flash('请输入有效的网址（以 http:// 或 https:// 开头）', 'danger')
        return redirect(url_for('comic_management'))
    
    try:
        # 添加下载任务
        comic_id = downloader.add_download_task(url, title if title else None)
        flash('漫画下载任务已添加，正在后台下载中...', 'success')
    except Exception as e:
        flash(f'添加下载任务失败: {str(e)}', 'danger')
    
    return redirect(url_for('comic_management'))


@app.route('/comic/<int:comic_id>/delete', methods=['POST'])
@admin_required
def comic_delete(comic_id):
    """删除漫画"""
    try:
        if downloader.delete_comic(comic_id):
            flash('漫画已删除', 'success')
        else:
            flash('删除漫画失败', 'danger')
    except Exception as e:
        flash(f'删除失败: {str(e)}', 'danger')
    
    return redirect(url_for('comic_management'))


@app.route('/comic/<int:comic_id>/progress')
@admin_required
def comic_progress(comic_id):
    """获取漫画下载进度（API）"""
    comic = Comic.query.get_or_404(comic_id)
    return jsonify(comic.to_dict())


@app.route('/comic/progress/all')
@admin_required
def comic_progress_all():
    """获取所有漫画的下载进度（API）"""
    comics = Comic.query.all()
    return jsonify([comic.to_dict() for comic in comics])


@app.route('/comic/<int:comic_id>/view')
@admin_required
def comic_view(comic_id):
    """查看漫画详情"""
    comic = Comic.query.get_or_404(comic_id)
    chapters = ComicChapter.query.filter_by(comic_id=comic_id).order_by(ComicChapter.chapter_number).all()
    return render_template('comic_view.html', comic=comic, chapters=chapters)


@app.route('/comic/<int:comic_id>/chapter/<int:chapter_id>/view')
@admin_required
def comic_chapter_view(comic_id, chapter_id):
    """查看漫画章节"""
    comic = Comic.query.get_or_404(comic_id)
    chapter = ComicChapter.query.get_or_404(chapter_id)
    
    # 确保章节属于该漫画
    if chapter.comic_id != comic_id:
        flash('章节不存在', 'danger')
        return redirect(url_for('comic_view', comic_id=comic_id))
    
    # 获取章节图片列表
    images = []
    if chapter.folder_path:
        chapter_folder = os.path.join('app/static', chapter.folder_path)
        if os.path.exists(chapter_folder):
            # 获取所有图片文件
            image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.webp', '.bmp'}
            files = sorted(os.listdir(chapter_folder))
            for file in files:
                if any(file.lower().endswith(ext) for ext in image_extensions):
                    # 将Windows路径转换为URL路径（使用正斜杠）
                    url_path = chapter.folder_path.replace(chr(92), '/') + '/' + file
                    images.append(url_path)
    
    # 获取上一章和下一章
    prev_chapter = ComicChapter.query.filter(
        ComicChapter.comic_id == comic_id,
        ComicChapter.chapter_number < chapter.chapter_number
    ).order_by(ComicChapter.chapter_number.desc()).first()
    
    next_chapter = ComicChapter.query.filter(
        ComicChapter.comic_id == comic_id,
        ComicChapter.chapter_number > chapter.chapter_number
    ).order_by(ComicChapter.chapter_number.asc()).first()
    
    return render_template('comic_chapter_view.html', 
                         comic=comic, 
                         chapter=chapter, 
                         images=images,
                         prev_chapter=prev_chapter,
                         next_chapter=next_chapter)


@app.route('/comic/<int:comic_id>/retry', methods=['POST'])
@admin_required
def comic_retry(comic_id):
    """重新下载失败的漫画"""
    comic = Comic.query.get_or_404(comic_id)
    
    if comic.status not in ['failed']:
        flash('只能重试失败的下载任务', 'danger')
        return redirect(url_for('comic_management'))
    
    try:
        # 重置状态并重新下载
        comic.status = 'pending'
        db.session.commit()
        
        # 启动新的下载线程
        import threading
        thread = threading.Thread(
            target=downloader._download_comic,
            args=(comic.id, comic.url),
            daemon=True
        )
        thread.start()
        
        flash('已重新开始下载', 'success')
    except Exception as e:
        flash(f'重试失败: {str(e)}', 'danger')
    
    return redirect(url_for('comic_management'))


@app.route('/static/comics/<path:filename>')
def comic_static(filename):
    """提供漫画静态文件访问"""
    return send_from_directory('static/comics', filename)
