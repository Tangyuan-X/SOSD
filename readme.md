## How to start
### edit your config.json
目前baseUrl和outputUrl必须一致

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

## TODO

1. 单独构建物体阴影交叉情况的场景。数据中加入关于阴影交叉占比（如交并比）的内容。
2. 关注阴影先后顺序问题，可能需要使用zbuffer数据
3. 考虑自阴影问题
