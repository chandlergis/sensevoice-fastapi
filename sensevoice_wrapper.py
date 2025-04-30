import subprocess
import os
import logging
import stat
import tempfile

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def convert_audio(input_path: str) -> str:
    """Convert audio to the required format (16kHz, 16bit, mono WAV)"""
    output_path = tempfile.mktemp(suffix='.wav')
    cmd = [
        'ffmpeg', '-i', input_path,
        '-acodec', 'pcm_s16le',
        '-ar', '16000',
        '-ac', '1',
        '-f', 'wav',
        output_path
    ]
    
    try:
        logger.info(f"Converting audio: {' '.join(cmd)}")
        subprocess.run(cmd, capture_output=True, check=True)
        return output_path
    except subprocess.CalledProcessError as e:
        raise Exception(f"Error converting audio: {e.stderr}")

def run_sensevoice(audio_path: str, model_path: str, threads: int = 4, lang: str = "auto"):
    """
    调用 sense-voice-main 处理音频文件并返回结果。
    """
    # Check binary exists and permissions
    binary_path = "/app/bin/sense-voice-main"
    if not os.path.exists(binary_path):
        raise FileNotFoundError(f"Binary not found at: {binary_path}")
    
    # Check binary permissions
    st = os.stat(binary_path)
    logger.info(f"Binary permissions: {oct(st.st_mode)}")
    if not st.st_mode & stat.S_IXUSR:
        logger.info("Setting execute permission on binary")
        os.chmod(binary_path, st.st_mode | stat.S_IXUSR)

    # Check model exists and size
    if not os.path.exists(model_path):
        raise FileNotFoundError(f"Model not found at: {model_path}")
    model_size = os.path.getsize(model_path)
    logger.info(f"Model size: {model_size} bytes")

    # Check input audio file
    if not os.path.exists(audio_path):
        raise FileNotFoundError(f"Audio file not found at: {audio_path}")
    
    logger.info(f"Using binary: {binary_path}")
    logger.info(f"Using model: {model_path}")
    logger.info(f"Using audio: {audio_path}")
    
    try:
        # Convert audio to required format
        converted_audio = convert_audio(audio_path)
        logger.info(f"Converted audio saved to: {converted_audio}")
        
        cmd = [
            binary_path,
            "-m", model_path,
            "-t", str(threads),
            "-l", lang,
            converted_audio
        ]
        
        logger.info(f"Running command: {' '.join(cmd)}")
        result = subprocess.run(cmd, capture_output=True, text=True, check=True)
        
        # Cleanup temporary file
        os.unlink(converted_audio)
        
        return result.stdout
    except subprocess.CalledProcessError as e:
        error_msg = f"Error running sense-voice-main:\nStderr: {e.stderr}\nStdout: {e.stdout}"
        logger.error(error_msg)
        raise Exception(error_msg)

# 示例用法
if __name__ == "__main__":
    model_path = "/models/gguf-fp16-sense-voice-small.bin"
    audio_path = "/path/to/asr_example_zh.wav"
    result = run_sensevoice(audio_path, model_path)
    print(result)