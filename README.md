# faster-whisper-docker

faster-whisper-docker 是一个基于 Docker 的语音识别服务部署项目，使用 Faster-Whisper 模型实现高效的 speech-to-text 转录。项目提供 HTTP 接口，支持：

- 上传整个音频文件方式进行识别；

- 流 (streaming / segment) 音频识别；

- 指定模型（比如 Systran/faster-whisper-large-v2）、语言、设备（CPU / GPU）等参数；

- 简单易用，只需用 docker-compose 构建或拉取镜像即可运行。

# 构建方式

## 自行构建

```bash
git clone https://github.com/GuQiangJS/faster-whisper-docker.git
docker-compose up -d --build
```

## 拉取镜像方式

```bash
docker pull ghcr.io/guqiangjs/faster-whisper-docker:latest
```

# 调用方式

## 上传文件方式调用

```bash
curl -X POST "http://127.0.0.1:8000/v1/audio/transcriptions?model=Systran/faster-whisper-large-v2&device=cuda&language=ja" -F "audio=@sampleTokyo.wav"
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

## 上传音频流方式调用

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

## 释放单个模型

```http
DELETE /v1/models/release/?model=medium&device=cuda
```

参考 [release_model.py](examples/release_model.py) 。

## 释放全部模型

```http
DELETE /v1/models/release_all
```

参考 [release_all_models.py](examples/release_all_models.py) 。
