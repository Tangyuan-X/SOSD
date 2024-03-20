## How to start
### edit your config.json
目前baseUrl和outputUrl必须一致

另外blender中合成器的图片输出也必须用同一个路径
### run the following command
```shell
blender -b ./locationTest1.blend -P ./main.py
```


## TODO

1. blender导出的index mask无法完全包围住物体，边缘有问题。以及mask无法为255的纯红色
2. blender导出的indexobj图片中，有各种噪点，导致最终生成的shadow_mask中会有噪点
3. 每次运行后清除obj和材质，防止blend文件越来越大
4. 随机生成的位置会穿模
5. 考虑自阴影问题