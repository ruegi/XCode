import ffmpeg
# stream = ffmpeg.hide_banner(True)
stream = ffmpeg.input(r'c:\ts\AATeilFigaro.ts.done', **{'hide_banner': None, 'hwaccel': "auto"})
# stream = ffmpeg.hflip(stream)
stream = ffmpeg.output(stream, 'output1.mkv', **{'c:v': "hevc_nvenc", "preset": "slow", "profile:v": "main10", "pix_fmt": "p010le", "crf": "23", "maxrate": "4M", "bufsize": "8M", "c:a": "copy", "c:s": "dvdsub" } )    # -map 0 -c:v hevc_nvenc -preset slow -profile:v main10 -pix_fmt p010le -crf 23 -maxrate 4M -bufsize 8M -dn -c:a copy -c:s dvdsub -y 
stream = ffmpeg.overwrite_output(stream)
ffmpeg.run(stream)

