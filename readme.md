## How to start
### edit your config.json
目前baseUrl和outputUrl必须一致

另外blender中合成器的图片输出也必须用同一个路径
### run the following command
```shell
blender -b ./locationTest1.blend -P ./main.py
```


## TODO

1. 考虑阴影交叉问题
2. 随机生成的位置会穿模
3. 考虑自阴影问题
