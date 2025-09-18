import requests
import numpy as np
import librosa  # 用于读取本地音频文件并提取波形
import logging
import time


def get_audio_waveform(file_path, target_sample_rate=16000):
    """
    读取本地音频文件，提取符合 Whisper 要求的波形数据
    """
    waveform, sample_rate = librosa.load(file_path,
                                         sr=target_sample_rate,
                                         mono=True,
                                         dtype=np.float32)
    waveform_data = waveform.tolist()

    logging.info(f"读取音频文件成功：{file_path}")
    logging.info(
        f"采样率 {sample_rate}Hz，时长 {len(waveform)/sample_rate:.2f} 秒，点数 {len(waveform)}"
    )

    return sample_rate, waveform_data


if __name__ == "__main__":
    # 你的音频文件路径
    local_audio_path = "./sampleTokyo.wav"
    response = None
    start = time.time()
    try:
        # 1. 读取音频，得到 16kHz 波形
        sample_rate, audio_data = get_audio_waveform(local_audio_path)

        # 2. 构造 payload
        waveform_payload = {"sample_rate": sample_rate, "data": audio_data}

        # 3. 请求接口
        response = requests.post(
            url="http://127.0.0.1:8000/v1/audio/transcriptions/waveform",
            params={
                "model": "Systran/faster-whisper-large-v2",
                "device": "cuda",
                "language": "ja"
            },
            json=waveform_payload  # 直接 JSON
        )

        response.raise_for_status()
        transcription_result = response.json()

        # 4. 打印结果
        print("=" * 50)
        print("本地音频文件转录结果：")
        print(f"文件路径：{local_audio_path}")
        print(f"总时长：{len(audio_data)/sample_rate:.2f} 秒")
        print("=" * 50)
        for idx, seg in enumerate(transcription_result, 1):
            print(
                f"分段 {idx}：[{seg['start']:.2f}-{seg['end']:.2f} 秒] {seg['text']}"
            )

    except Exception as e:
        print(f"处理失败：{str(e)}")
        if 'response' in locals() and response.status_code != 200:
            print(f"接口错误详情：{response.text}")
    print(f'耗时 {time.time() - start:.2f} 秒')
