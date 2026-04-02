from app import db
from datetime import datetime


class Comic(db.Model):
    """漫画模型 - 存储漫画基本信息"""
    __tablename__ = 'comics'
    
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)  # 漫画标题
    url = db.Column(db.String(500), nullable=False)    # 源网址
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending/downloading/completed/failed
    folder_path = db.Column(db.String(500), nullable=True)  # 本地存储路径
    total_chapters = db.Column(db.Integer, default=0)   # 总章节数
    downloaded_chapters = db.Column(db.Integer, default=0)  # 已下载章节数
    cover_image = db.Column(db.String(500), nullable=True)  # 封面图路径
    description = db.Column(db.Text, nullable=True)     # 漫画描述
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # 关联章节
    chapters = db.relationship('ComicChapter', backref='comic', lazy=True, cascade='all, delete-orphan')
    
    def __repr__(self):
        return f'<Comic {self.title}>'
    
    def to_dict(self):
        """转换为字典格式（用于API返回）"""
        return {
            'id': self.id,
            'title': self.title,
            'url': self.url,
            'status': self.status,
            'folder_path': self.folder_path,
            'total_chapters': self.total_chapters,
            'downloaded_chapters': self.downloaded_chapters,
            'cover_image': self.cover_image,
            'description': self.description,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S') if self.created_at else None,
            'updated_at': self.updated_at.strftime('%Y-%m-%d %H:%M:%S') if self.updated_at else None,
            'progress': self.get_progress()
        }
    
    def get_progress(self):
        """获取下载进度百分比"""
        if self.total_chapters == 0:
            return 0
        return int((self.downloaded_chapters / self.total_chapters) * 100)


class ComicChapter(db.Model):
    """漫画章节模型 - 存储章节信息"""
    __tablename__ = 'comic_chapters'
    
    id = db.Column(db.Integer, primary_key=True)
    comic_id = db.Column(db.Integer, db.ForeignKey('comics.id'), nullable=False)
    chapter_number = db.Column(db.Integer, nullable=False)  # 章节序号
    title = db.Column(db.String(255), nullable=True)        # 章节标题
    folder_path = db.Column(db.String(500), nullable=True)  # 本地存储路径
    page_count = db.Column(db.Integer, default=0)           # 总页数
    downloaded_pages = db.Column(db.Integer, default=0)     # 已下载页数
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending/downloading/completed/failed
    source_url = db.Column(db.String(500), nullable=True)   # 源章节URL
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def __repr__(self):
        return f'<ComicChapter {self.comic.title} - 第{self.chapter_number}章>'
    
    def to_dict(self):
        """转换为字典格式"""
        return {
            'id': self.id,
            'comic_id': self.comic_id,
            'chapter_number': self.chapter_number,
            'title': self.title,
            'folder_path': self.folder_path,
            'page_count': self.page_count,
            'downloaded_pages': self.downloaded_pages,
            'status': self.status,
            'progress': self.get_progress()
        }
    
    def get_progress(self):
        """获取下载进度百分比"""
        if self.page_count == 0:
            return 0
        return int((self.downloaded_pages / self.page_count) * 100)
