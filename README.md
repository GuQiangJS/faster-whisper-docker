# faster-whisper-docker

faster-whisper-docker 是一个基于 Docker 的语音识别服务部署项目，使用 Faster-Whisper 模型实现高效的 speech-to-text 转录。项目提供 HTTP 接口，支持：

- 上传整个音频文件方式进行识别；

- 流 (streaming / segment) 音频识别；

- 指定模型（比如 Systran/faster-whisper-large-v2）、语言、设备（CPU / GPU）等参数；

- 简单易用，只需用 docker-compose 构建或拉取镜像即可运行。

## 版本说明

本项目提供两个版本的镜像：

- CPU 版本：适用于没有 GPU 或不需要 GPU 加速的环境
- GPU 版本：适用于支持 CUDA 的 NVIDIA GPU，提供更快的转录速度

> 其实这个项目是为了挽救我上古时代的 750Ti 显卡才开始弄的。也怪我自己没有仔细看各个项目的说明。
> faster-whisper 从一开始就需要 ctranslate2 3.5 以上的版本，而 ctranslate2 从 3 版本开始就抛弃了 CUDA 10
> 但是上古的 750Ti 显卡最多也就支持到了 CUDA 11。结果我安装的是 CUDA12 的版本。
> 基于`pytorch/pytorch:2.6.0-cuda12.4-cudnn9-devel`来运行（Dockerfile.cuda.12)，也依旧提示
>
> ```
> INFO:faster_whisper:Processing audio with duration 01:13.003 Unable to load any of {libcudnn_ops.so.9.1.0, libcudnn_ops.so.9.1, libcudnn_ops.so.9, libcudnn_ops.so} Invalid handle. Cannot load symbol cudnnCreateTensorDescriptor
> ```
>
> 哎，穷人变异失败，也没那么多时间折腾了。等换了显卡或者有时间再折腾了。
> **CPU 版本的镜像是可以用的，CUDA 版本暂时只是基于 cuda 12.8.1 使用 github actions 构建的镜像，如果需要构建其他版本可以参考 [docker-image.yml](.github/workflows/docker-image.yml) 中的 `build-cuda` 部分自行构建**

## 构建方式

### 自行构建

```bash
git clone https://github.com/GuQiangJS/faster-whisper-docker.git
cd faster-whisper-docker
```

构建并运行 CPU 版本：

```bash
docker-compose up -d --build whisper-service-cpu
```

构建并运行 GPU 版本：

```bash
docker-compose up -d --build whisper-service-cuda
```

### 拉取镜像方式

拉取 CPU 版本：

```bash
docker pull ghcr.io/guqiangjs/faster-whisper-docker:cpu-latest
```

拉取 GPU 版本：

```bash
docker pull ghcr.io/guqiangjs/faster-whisper-docker:torch2.7.1-12.8.1-cudnn-runtime-ubuntu22.04-latest
```

## 直接使用 docker-compose

```yaml
services:
  whisper-service:
    image: ghcr.io/guqiangjs/faster-whisper-docker/whisper-service:torch2.7.1-12.8.1-cudnn-runtime-ubuntu22.04-latest
    container_name: whisper-service
    restart: unless-stopped
    ports:
      - "8993:8000"
    volumes:
      - ./hf-hub-cache:/root/.cache/huggingface/hub
    environment:
      - HF_ENDPOINT=https://hf-mirror.com
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: all
              capabilities: [gpu]
```

## 调用方式

### 上传文件方式调用

CPU 版本调用示例：

```bash
curl -X POST "http://127.0.0.1:8000/v1/audio/transcriptions?model=Systran/faster-whisper-large-v2&device=cpu&language=ja" -F "audio=@sampleTokyo.wav"
```

GPU 版本调用示例：

```bash
curl -X POST "http://127.0.0.1:8001/v1/audio/transcriptions?model=Systran/faster-whisper-large-v2&device=cuda&language=ja" -F "audio=@sampleTokyo.wav"
```

模型默认为`Systran/faster-whisper-large-v2`。使用默认模型参数，调用示例：

```bash
curl -X POST "http://127.0.0.1:8000/v1/audio/transcriptions?language=ja" -F "audio=@sampleTokyo.wav"
```

参考 [test_file.py](examples/post_file.py) 。

输出结果：

```txt
转录结果:
[0.00-7.28]: 浅野ともみです 今日の東京株式市場で日経平均株価は小幅促進となっています
[7.28-20.28]: 終わり値は昨日に比べ22円72銭高の11,088円58銭でした 当初一部の値上がり銘柄数は1146
[20.28-27.44]: 対して値下がりは368 変わらずは104銘柄となっています
[27.44-36.28]: ここでプレゼントのお知らせです この番組では毎月発行のマンスリーレポート4月号を抽選で10名様にプレゼントいたします
[36.28-46.04]: お申し込みはお電話で東京0301078373 0301078373まで
[46.04-50.00]: 以上番組からのお知らせでした
耗时 7.02 秒
```

### 上传音频流方式调用

参考 [test_wave.py](examples/post_wave.py) 。

输出结果：

```txt
==================================================
本地音频文件转录结果：
文件路径：./sampleTokyo.wav
总时长：48.19 秒
==================================================
分段 1：[0.00-2.00 秒] 朝野智美です
分段 2：[2.00-7.00 秒] 今日の東京株式市場で日経平均株価は小幅促進となっています
分段 3：[7.00-16.00 秒] 終わり値は昨日に比べ22円72銭高の11,088円58銭でした
分段 4：[16.00-20.00 秒] 当初一部の値上がり銘柄数は1146
分段 5：[20.00-23.00 秒] 対して値下がりは368
分段 6：[23.00-27.00 秒] 変わらずは104銘柄となっています
分段 7：[27.00-29.00 秒] ここでプレゼントのお知らせです
分段 8：[29.00-36.00 秒] この番組では毎月発行のマンスリーレポート4月号を抽選で10名様にプレゼントいたします。
分段 9：[36.00-45.00 秒] お申し込みはお電話で、東京03-0107-8373、03-0107-8373まで。
分段 10：[45.00-48.00 秒] 以上、番組からのお知らせでした。
耗时 10.07 秒
```

### 释放单个模型

```bash
curl -X DELETE "http://127.0.0.1:8000/v1/models/release?model=medium&device=cuda"
```

参考 [release_model.py](examples/release_model.py) 。

### 释放全部模型

```bash
curl -X DELETE "http://127.0.0.1:8000/v1/models/release_all"
```

参考 [release_all_models.py](examples/release_all_models.py) 。

## 端口说明

- CPU 版本默认运行在端口 8000
- GPU 版本默认运行在端口 8001

## 环境变量

- `WHISPER_MODEL`：默认使用的模型名称，默认值为`Systran/faster-whisper-large-v2`
- `DEVICE`：默认设备类型，CPU 版本默认为`cpu`，GPU 版本默认为`cuda`
- 如果环境无法访问 huggingface，可以在 `docker-compose.yml` 中添加代理环境变量
  ```yaml
  environment:
    - http_proxy=http://代理服务器IP:端口
    - https_proxy=http://代理服务器IP:端口
    # 如果代理需要认证
    # - http_proxy=http://用户名:密码@代理服务器IP:端口
    # - https_proxy=http://用户名:密码@代理服务器IP:端口
    # 可选：设置不需要代理的地址（如内部服务）
    - no_proxy=localhost,127.0.0.1,.example.com
  ```
