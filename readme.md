## How to start
### run the following command

室内数据集：

```shell
blender -b ./indoor.blend -P ./indoor.py
```

室外数据集：

```shell
blender -b ./outdoor.blend -P ./outdoor.py
```

为了防止在github同步过大的二进制文件，其中blend文件已经搬到了[https://drive.google.com/drive/folders/1TjVv01WxVHClVdCdnm6T4eguckKv27-Z?usp=sharing](https://drive.google.com/drive/folders/1TjVv01WxVHClVdCdnm6T4eguckKv27-Z?usp=sharing)

### requirement

- blender=3.3

以下软件包需要在blender自带的python环境下安装

- Python=3.10.13
- Pillow=10.2.0
- pycocotools=2.0.7
- numpy=1.22.0
- opencv-python=4.5.4.60
