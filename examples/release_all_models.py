import requests


def release_all_models():
    """
    调用接口释放所有模型
    """
    url = "http://127.0.0.1:8000/v1/models/release_all"
    response = None
    try:
        response = requests.delete(url)
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
    result = release_all_models()
    if result:
        print("释放所有模型结果:", result)
