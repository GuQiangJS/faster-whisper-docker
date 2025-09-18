import requests


def release_model(model, device="auto"):
    """
    调用接口释放指定模型
    """
    url = f"http://127.0.0.1:8000/v1/models/release/"
    params = {"model": model, "device": device}

    response = None
    try:
        response = requests.delete(url, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"请求失败: {str(e)}")
        if response is not None:
            try:
                print(f"错误详情: {response.json()}")
            except:
                print(f"错误响应: {response.text}")
        return None


if __name__ == "__main__":
    model_id = "Systran/faster-whisper-large-v2"
    device = "cuda"
    result = release_model(model_id, device)
    if result:
        print("释放结果:", result)
