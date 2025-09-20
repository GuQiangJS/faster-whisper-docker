from fastapi import FastAPI, Query, UploadFile, File, HTTPException, Body, Form
from typing import Optional, List, Union, Dict, Iterable
import os
import numpy as np
import aiofiles
import tempfile
from faster_whisper import WhisperModel
import traceback
from pydantic import BaseModel
import logging
import gc
import torch


# 定义音频波形数据的模型
class AudioWaveform(BaseModel):
    sample_rate: int
    data: List[float]  # 音频波形数据


class WhisperModelManager:

    def __init__(self):
        # 模型缓存，避免重复加载
        self.models = {}

    def get_model(self, model_id: str, device: str, compute_type: str):
        """
        https://opennmt.net/CTranslate2/quantization.html
        https://github.com/SYSTRAN/faster-whisper
        """
        key = (model_id, device)
        if key not in self.models:
            if compute_type == "default":
                compute_type = "float16" if device == "cuda" else "int8"
            self.models[key] = WhisperModel(model_id,
                                            device=device,
                                            compute_type=compute_type)
        return self.models[key]

    def transcribe(self, audio, model_id: str, device: str, compute_type: str,
                   **kwargs):
        """
        kwargs 会原样透传给 faster-whisper 的 transcribe()
        """
        model = self.get_model(model_id, device, compute_type)
        segments, info = model.transcribe(audio, **kwargs)
        return list(segments), info

    def release_model(self, model_id: str, device: str):
        """
        释放指定模型，清理内存/显存
        """
        key = (model_id, device)
        if key in self.models:
            del self.models[key]
            gc.collect()
            if device == "cuda" and torch.cuda.is_available():
                torch.cuda.empty_cache()
            return True
        return False

    def release_all(self):
        """
        释放所有已加载的模型，清理缓存
        """
        self.models.clear()
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.empty_cache()
        return True


def process_audio(audio: Union[str, object, np.ndarray]):
    """
    处理音频的核心函数，支持多种输入类型
    
    Args:
        audio: 可以是文件路径、类文件对象或音频波形数组
    """
    # 根据不同类型进行处理
    if isinstance(audio, str):
        # 处理文件路径
        if not os.path.exists(audio):
            raise FileNotFoundError(f"文件不存在: {audio}")
        print(f"处理文件路径: {audio}")
        # 这里添加从文件读取音频的逻辑

    elif hasattr(audio, 'read'):  # 检查是否是类文件对象
        print(f"处理类文件对象: {getattr(audio, 'name', 'unknown')}")
        # 这里添加从类文件对象读取音频的逻辑

    elif isinstance(audio, np.ndarray):
        # 处理音频波形数据
        print(f"处理音频波形: 形状 {audio.shape}, 数据类型 {audio.dtype}")
        # 这里添加处理波形数据的逻辑

    else:
        raise TypeError(f"不支持的音频类型: {type(audio)}")

    # 实际应用中这里会返回语音识别结果
    return "模拟的语音转文字结果"


app = FastAPI(title="Whisper Service", version="1.0.0")

manager = WhisperModelManager()
logging.basicConfig(level=logging.INFO)


@app.delete("/v1/models/release")
async def release_model(model: str = Query("Systran/faster-whisper-large-v2"),
                        device: str = Query(os.environ.get("DEVICE", "auto"))):
    """
    释放指定模型vi
    """
    released = manager.release_model(model, device)
    if not released:
        raise HTTPException(status_code=404,
                            detail=f"模型 {model} (device={device}) 不存在或未加载")
    return {"status": "success", "released_model": model, "device": device}


@app.delete("/v1/models/release_all")
async def release_all_models():
    """
    释放所有缓存的模型
    """
    manager.release_all()
    return {"status": "success", "released": "all models"}


@app.post("/v1/audio/transcriptions/audiofile", response_model=List[Dict])
async def transcribe(
        # 文件上传方式（类文件对象）
        audio: Optional[UploadFile] = File(None, description="音频文件（二进制流）"),
        model: str = Query("Systran/faster-whisper-large-v2"),
        device: str = Query(os.environ.get("DEVICE", "auto")),
        compute_type: str = Query("default"),
        language: Optional[str] = Query(None),
        vad_filter: Optional[bool] = Query(False),
        initial_prompt: Optional[Union[str, Iterable[int]]] = Query(None),
        log_progress: Optional[bool] = Query(False),
        condition_on_previous_text: Optional[bool] = Query(False)):

    if not audio:
        raise HTTPException(status_code=400, detail="请提供音频输入")

    temp_file_path = ''
    try:
        with tempfile.NamedTemporaryFile(delete=False,
                                         suffix=os.path.splitext(
                                             audio.filename)[1]) as temp_file:
            temp_file_path = temp_file.name

        # 异步保存文件到临时目录
        async with aiofiles.open(temp_file_path, 'wb') as out_file:
            content = await audio.read()
            await out_file.write(content)

        # 将类文件对象传递给处理函数
        audio = temp_file_path

        logging.info(f'audio={audio}')

        return run_transcription(
            audio=audio,
            model=model,
            device=device,
            compute_type=compute_type,
            language=language,
            initial_prompt=initial_prompt,
            log_progress=log_progress,
            condition_on_previous_text=condition_on_previous_text,
            vad_filter=vad_filter)

    except Exception as e:
        raise HTTPException(status_code=500,
                            detail=f"处理失败: {str(e)}\n{traceback.format_exc()}")
    finally:
        if temp_file_path and os.path.exists(temp_file_path):
            os.remove(temp_file_path)


@app.post("/v1/audio/transcriptions/waveform", response_model=List[Dict])
async def transcribe_waveform(
        audio: AudioWaveform = Body(...),
        model: str = Query("Systran/faster-whisper-large-v2"),
        device: str = Query(os.environ.get("DEVICE", "auto")),
        compute_type: str = Query("default"),
        language: Optional[str] = Query(None),
        vad_filter: Optional[bool] = Query(False),
        initial_prompt: Optional[Union[str, Iterable[int]]] = Query(None),
        log_progress: Optional[bool] = Query(False),
        condition_on_previous_text: Optional[bool] = Query(False)):
    audio = np.array(audio.data)
    return run_transcription(
        audio=audio,
        model=model,
        device=device,
        compute_type=compute_type,
        language=language,
        initial_prompt=initial_prompt,
        log_progress=log_progress,
        condition_on_previous_text=condition_on_previous_text,
        vad_filter=vad_filter)


def run_transcription(audio, model, device, compute_type, **kwargs):
    logging.info(f'model={model},device={device},compute_type={compute_type}')
    # 注意：此处传入的应为解码后的音频数组
    segments, info = manager.transcribe(audio,
                                        model_id=model,
                                        device=device,
                                        compute_type=compute_type,
                                        **kwargs)
    return [seg._asdict() for seg in segments]
