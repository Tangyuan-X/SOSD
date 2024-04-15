## How to start
### edit your config.json
目前baseUrl和outputUrl必须一致

### run the following command
```shell
blender -b ./locationTest1.blend -P ./main.py
```

其中blend文件已经搬到了[https://drive.google.com/file/d/15UhCaZ8ASu32NMDjwsPAs6aud3bIKrkA/view?usp=drive_link](https://drive.google.com/file/d/15UhCaZ8ASu32NMDjwsPAs6aud3bIKrkA/view?usp=drive_link)

## TODO

1. 在服务器上运行，得到一版数据集
2. 确定数据集的导出数据
3. 引入HDRI环境贴图，重构场景，构造外部环境的场景。
4. 收集HDRI数据集
5. 场景随机HDRI数据集
6. 重新布置场景、重写灯光随机逻辑、物体摆放逻辑（包含防穿模）
7. 单独构建物体阴影交叉情况的场景
8. 阴影mask单独即可，无需合并
9. 关注阴影先后顺序问题，可能需要使用zbuffer数据
10. 考虑自阴影问题
