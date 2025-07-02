import time
import asyncio

async def get_duration(url):
    """
    Retrieve total duration (in seconds) using ffprobe.
    Returns None if duration cannot be determined.
    """
    cmd = [
        'ffprobe',
        '-v', 'error',
        '-select_streams', 'v:0',
        '-show_entries', 'format=duration',
        '-of', 'default=noprint_wrappers=1:nokey=1',
        url
    ]
    try:
        proc = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        output, _ = await proc.communicate()
        return float(output.decode().strip())
    except Exception:
        return None

async def download_with_progress(url, index, total):
    """
    Download a single HLS stream using ffmpeg,
    updating the progress on one single line.
    """
    # Try to get total duration for progress calculations.
    duration = await get_duration(url)
    output_file = f"L{index+10}.mp4"
    cmd = [
        'ffmpeg',
        '-allowed_extensions', 'ALL',
        '-i', url,
        '-c', 'copy',
        output_file,
        '-y',                   # Overwrite existing file
        '-progress', 'pipe:1',  # Write progress info to stdout
        '-nostats',             # Suppress ffmpeg's stats
        '-loglevel', 'quiet'    # Suppress extra logs
    ]
    
    print(f"Video {index}/{total} → {output_file}")
    process = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE
    )
    
    current_time = 0.0
    bar_length = 30
    
    while True:
        line = await process.stdout.readline()
        if not line:
            if process.returncode is not None:
                break
            await asyncio.sleep(0.05)
            continue

        line = line.decode().strip()
        if line.startswith("out_time_ms="):
            # Extract current processed time in seconds
            ms_str = line.split('=')[1]
            current_time = float(ms_str) / 1_000_000.0

            if duration and duration > 0:
                progress = min(current_time / duration, 1.0)
                filled_length = int(bar_length * progress)
                bar = '=' * filled_length + '-' * (bar_length - filled_length)
                percentage = progress * 100
                print(f"\033[{index}A\033[KVideo {index}/{total} [{bar}] {percentage:5.2f}%\033[{index}B", end='', flush=True)
            else:
                print(f"\033[{index}A\033[KVideo {index}/{total} Elapsed: {current_time:5.1f}s\033[{index}B", end='', flush=True)

        elif line.startswith("progress=") and line == "progress=end":
            break

    await process.wait()
    # Finish the progress line and print a completion message.
    if process.returncode == 0:
        print(f"\033[{index}A\033[KVideo {index}/{total} completed successfully!\033[{index}B")
    else:
        print(f"\033[{index}A\033[KVideo {index}/{total} failed with return code {process.returncode}\033[{index}B")

async def main():
    start_time = time.time()
    # List of HLS URLs (m3u8 links)
    urls = [
        "https://txvodkey125.ckjrio.com/ab85ad06vodtranssgp1252433846/8ecd11ce1397757903281341694/v.f100230.m3u8?t=67edb23a&us=ZDtcpfPglJ&sign=9e3b5119724d04afc98b913e5d4ddeea"        
        # Add more URLs as needed...
    ]
    total_videos = len(urls)
    tasks = [download_with_progress(url, i, total_videos) for i, url in enumerate(urls, start=1)]
    await asyncio.gather(*tasks)
    end_time = time.time()
    print(f"\nTotal download time: {end_time - start_time:.2f} seconds")

if __name__ == "__main__":
    asyncio.run(main())
