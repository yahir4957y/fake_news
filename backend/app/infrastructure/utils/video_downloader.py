import yt_dlp
import tempfile
import os

def descargar_video(url: str) -> bytes:
    """
    Descarga un video desde una URL (TikTok, YouTube, X) 
    y devuelve sus bytes para inyectarlos en Gemini.
    """
    # usamos la carpeta temp del sistema 
    temp_dir = tempfile.gettempdir()
    opciones = {
        'format': 'best[ext=mp4]/best', 
        'outtmpl': os.path.join(temp_dir, '%(id)s.%(ext)s'),
        'quiet': True,
        'no_warnings': True,
        'max_filesize': 50 * 1024 * 1024, 
    }

    try:
     
        with yt_dlp.YoutubeDL(opciones) as ydl:
            # extraemos la info 
            info = ydl.extract_info(url, download=True)
            archivo_descargado = ydl.prepare_filename(info)
            
            
            with open(archivo_descargado, 'rb') as f:
                video_bytes = f.read()
            
            # borramos el archivo local 
            if os.path.exists(archivo_descargado):
                os.remove(archivo_descargado)
            
            return video_bytes
            
    except yt_dlp.utils.DownloadError as e:
        raise Exception("El video es privado, fue eliminado o la red social bloqueó la descarga.")
    except Exception as e:
        raise Exception(f"No se pudo extraer el video: {str(e)}")