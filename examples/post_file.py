import requests
import time


def transcribe_audio(file_path, model, device, language=None):
    # API接口地址
    url = "http://127.0.0.1:8000/v1/audio/transcriptions/audiofile"

    # URL查询参数（对应curl中的?后面的参数）
    params = {"model": model, "device": device, "language": language}

    # 准备文件上传（对应curl中的-F参数）
    files = {
        "audio": open(file_path, "rb")  # 以二进制模式打开文件
    }
    response = None
    try:
        # 发送POST请求
        response = requests.post(url, params=params, files=files)

        # 检查请求是否成功
        response.raise_for_status()  # 若状态码不是200，会抛出异常

        # 返回解析后的JSON结果
        return response.json()

    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        # 尝试获取错误详情（如果服务器返回了错误信息）
        if response is not None:
            try:
                print(f"错误详情: {response.json()}")
            except:
                print(f"错误响应: {response.text}")
        return None

    finally:
        # 确保文件被关闭
        files["audio"].close()


# 使用示例
if __name__ == "__main__":
    # 替换为你的音频文件路径
    audio_file_path = "./sampleTokyo.wav"

    start = time.time()
    # 调用接口
    result = transcribe_audio(
        file_path=audio_file_path,
        model="Systran/faster-whisper-large-v2",
        device="cuda",
        language="ja"  # 日语
    )

    # 打印结果
    if result:
        print("转录结果:")
        # 根据实际返回格式调整打印方式
        if isinstance(result, list):
            # 如果返回的是分段列表
            for segment in result:
                print(
                    f"[{segment['start']:.2f}-{segment['end']:.2f}]: {segment['text']}"
                )
        else:
            # 如果返回的是包含segments字段的对象
            for segment in result.get("segments", []):
                print(
                    f"[{segment['start']:.2f}-{segment['end']:.2f}]: {segment['text']}"
                )

    print(f'耗时 {time.time() - start:.2f} 秒')
