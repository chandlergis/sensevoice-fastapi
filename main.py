from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
from sensevoice_wrapper import run_sensevoice
import os
import tempfile
import shutil

app = FastAPI(title="SenseVoice API")

# 配置
MODEL_PATH = os.getenv("MODEL_PATH", "/models/sense-voice-small-q5_0.gguf")
THREADS = int(os.getenv("THREADS", 4))
ALLOWED_EXTENSIONS = {".wav", ".mp3"}

@app.post("/recognize")
async def recognize(file: UploadFile = File(...), lang: str = "auto"):
    """
    上传音频文件并进行语音识别。
    
    Args:
        file: 上传的音频文件
        lang: 语言（默认 auto）
    
    Returns:
        JSON 响应，包含识别结果
    """
    # 检查文件扩展名
    file_ext = os.path.splitext(file.filename)[1].lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Unsupported file format. Use .wav or .mp3")
    
    # 创建临时文件
    with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as temp_file:
        temp_path = temp_file.name
        # 写入上传的文件
        shutil.copyfileobj(file.file, temp_file)
    
    try:
        # 调用 SenseVoice
        result = run_sensevoice(temp_path, MODEL_PATH, threads=THREADS, lang=lang)
        return JSONResponse(content={"result": result})
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        # 清理临时文件
        if os.path.exists(temp_path):
            os.unlink(temp_path)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=30088)