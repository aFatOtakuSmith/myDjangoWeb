import re
import base64
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.admin.views.decorators import staff_member_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Song, Playlist  # 🌟 导入 Playlist
from mutagen.id3 import ID3, ID3NoHeaderError
from django.contrib.auth.decorators import login_required
def music_player(request):
    songs = Song.objects.all()
    playlists = Playlist.objects.all()
    return render(request, 'music/music_player.html', {
        'songs': songs,
        'playlists': playlists
    })
@login_required
def music_player(request):
    songs = Song.objects.all()
    playlists = Playlist.objects.all()
    return render(request, 'music/music_player.html', {
        'songs': songs,
        'playlists': playlists
    })
@csrf_exempt
def toggle_like(request, song_id):
    if request.method == 'POST':
        try:
            song = Song.objects.get(id=song_id)
            song.is_liked = not song.is_liked
            song.save()
            return JsonResponse({'status': 'success', 'is_liked': song.is_liked})
        except Song.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': '歌曲不存在'}, status=404)
    return JsonResponse({'status': 'error', 'message': '仅支持 POST'}, status=400)

def get_lyrics(request, song_id):
    try:
        song = Song.objects.get(id=song_id)
        filepath = song.file.path
        
        cover_base64 = None
        
        try:
            audio = ID3(filepath)
            covers = audio.getall('APIC')
            if covers:
                cover_data = covers[0].data
                cover_base64 = f"data:{covers[0].mime};base64,{base64.b64encode(cover_data).decode('utf-8')}"
                
        except ID3NoHeaderError:
            return JsonResponse({'status': 'success', 'type': 'text', 'lyrics': '这首歌没有内嵌歌词 (无ID3标签)', 'cover': cover_base64})
            
        uslt_frames = audio.getall('USLT')
        
        if uslt_frames:
            raw_text = uslt_frames[0].text
            if isinstance(raw_text, bytes):
                try:
                    raw_text = raw_text.decode('utf-8')
                except UnicodeDecodeError:
                    raw_text = raw_text.decode('gbk', errors='ignore')
            
            pattern = re.compile(r'\[(\d{2}):(\d{2})(?:\.(\d+))?\](.*)')
            lines = raw_text.splitlines()
            
            lyrics_data = []
            is_lrc = False
            
            for line in lines:
                match = pattern.match(line.strip())
                if match:
                    is_lrc = True
                    minutes = int(match.group(1))
                    seconds = int(match.group(2))
                    milliseconds = match.group(3)
                    
                    time_in_seconds = minutes * 60 + seconds
                    if milliseconds:
                        time_in_seconds += int(milliseconds.ljust(3, '0')) / 1000.0
                        
                    text = match.group(4).strip()
                    if text:
                        lyrics_data.append({"time": round(time_in_seconds, 2), "text": text})
            
            if is_lrc and lyrics_data:
                return JsonResponse({'status': 'success', 'type': 'lrc', 'lyrics': lyrics_data, 'cover': cover_base64})
            else:
                return JsonResponse({'status': 'success', 'type': 'text', 'lyrics': raw_text, 'cover': cover_base64})
                
        return JsonResponse({'status': 'success', 'type': 'text', 'lyrics': '这首歌没有内嵌歌词', 'cover': cover_base64})
            
    except Exception as e:
        return JsonResponse({'status': 'error', 'lyrics': f'后端异常: {str(e)}', 'cover': None})

@staff_member_required
def batch_upload(request):
    if request.method == 'POST':
        files = request.FILES.getlist('files')
        if not files:
            messages.warning(request, '没有选择任何文件')
            return redirect('music:batch_upload')
            
        created = 0
        for f in files:
            title = f.name.rsplit('.', 1)[0]
            Song.objects.create(title=title, file=f)
            created += 1
            
        messages.success(request, f'成功导入 {created} 首歌曲')
        return redirect('admin:music_song_changelist')

    return render(request, 'music/batch_upload.html')