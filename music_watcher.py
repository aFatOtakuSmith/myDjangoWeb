import os
import time
import django
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from django.db.models import Max # 🌟 用于排序计算

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mydearweb.settings')
django.setup()

from django.conf import settings
from music.models import Song

MUSIC_DIR = os.path.join(settings.MEDIA_ROOT, 'music')
AUDIO_EXTS = ('.mp3', '.wav', '.flac')

def wait_until_stable(filepath, timeout=15):
    last_size = -1
    stable_count = 0
    start = time.time()
    while time.time() - start < timeout:
        try:
            size = os.path.getsize(filepath)
        except OSError:
            return False
        if size > 0 and size == last_size:
            stable_count += 1
            if stable_count >= 2:
                return True
        else:
            stable_count = 0
        last_size = size
        time.sleep(0.4)
    return False

class MusicFolderHandler(FileSystemEventHandler):
    def _handle(self, filepath):
        if not os.path.isfile(filepath):
            return
        filename = os.path.basename(filepath)
        if not filename.lower().endswith(AUDIO_EXTS):
            return

        if not wait_until_stable(filepath):
            print(f"⏭️ [跳过] 文件未写完或为空: {filename}")
            return

        title = os.path.splitext(filename)[0]
        relative_path = f'music/{filename}'
        
        if not Song.objects.filter(file=relative_path).exists():
            # 自动计算排序号
            max_order = Song.objects.aggregate(Max('my_order'))['my_order__max']
            next_order = (max_order or 0) + 1
            
            Song.objects.create(
                title=title, 
                file=relative_path,
                my_order=next_order
            )
            print(f"🎵 [新增] {title} (排序号: {next_order})")
        else:
            print(f"⚠️ [跳过] 已存在: {title}")

    def on_created(self, event):
        if not event.is_directory:
            self._handle(event.src_path)

    def on_moved(self, event):
        if not event.is_directory:
            self._handle(event.dest_path)

    def on_deleted(self, event):
        if not event.is_directory:
            filename = os.path.basename(event.src_path)
            if filename.lower().endswith(AUDIO_EXTS):
                relative_path = f'music/{filename}'
                deleted_count, _ = Song.objects.filter(file=relative_path).delete()
                if deleted_count > 0:
                    print(f"🗑️ [删除] {filename}")

# 🌟 新增：启动时的全量扫描函数
def full_scan():
    print("🔄 [全量扫描] 正在比对文件夹与数据库的差异...")
    # 1. 获取文件夹里真实存在的音频文件
    disk_files = set()
    if os.path.exists(MUSIC_DIR):
        for filename in os.listdir(MUSIC_DIR):
            if filename.lower().endswith(AUDIO_EXTS):
                disk_files.add(f'music/{filename}')

    # 2. 获取数据库里现有的歌曲记录
    db_songs = list(Song.objects.all())
    db_files = set(song.file.name for song in db_songs)

    added_count = 0
    deleted_count = 0

    # 3. 找出文件夹里有，但数据库里没有的（漏网之鱼）
    for missing_file in disk_files - db_files:
        title = os.path.splitext(os.path.basename(missing_file))[0]
        max_order = Song.objects.aggregate(Max('my_order'))['my_order__max']
        next_order = (max_order or 0) + 1
        Song.objects.create(title=title, file=missing_file, my_order=next_order)
        print(f"🎵 [扫描新增] {title}")
        added_count += 1

    # 4. 找出数据库里有，但文件夹里已经被删了的（僵尸记录）
    for song in db_songs:
        if song.file.name not in disk_files:
            song.delete()
            print(f"🗑️ [扫描清理] 已删除遗失文件记录: {song.title}")
            deleted_count += 1

    print(f"✅ [全量扫描] 完成！新增 {added_count} 首，清理 {deleted_count} 首。")


if __name__ == "__main__":
    os.makedirs(MUSIC_DIR, exist_ok=True)
    
    # 🌟 启动前，先全量扫描一次
    full_scan()

    print(f"👀 开始实时监听: {MUSIC_DIR}")
    observer = Observer()
    observer.schedule(MusicFolderHandler(), MUSIC_DIR, recursive=False)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\n🛑 已停止")
    observer.join()