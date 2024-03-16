(function () {
    var imageInput = document.getElementById("imageInput"); //获取输入按钮
    var numInput =document.getElementById("numInput");
    var myCanvas = document.getElementById("myCanvas"); //获取canvas
    var cxt = myCanvas.getContext('2d'); //获取上下文
    var img = new Image(); //定义图像对象
    var pxData = null; //定义存储像素的数组
    var rNumber = new Array(256).fill(0); //定义每一个像素点中R通道值的出现次数
    var gNumber = new Array(256).fill(0); //定义每一个像素点中R通道值的出现次数
    var bNumber = new Array(256).fill(0); //定义每一个像素点中R通道值的出现次数
 
    var rangeNum = 64;//显示直方图的频段
 
    //读取文件后的回调函数
    imageInput.onchange = function () {
 
        // img = new Image();
        var file = this.files[0];
        if (window.FileReader) {
            var reader = new FileReader();
            reader.readAsDataURL(file);
            //监听文件读取结束后事件
            reader.onloadend = function (e) {
                img.src = e.target.result; //修改图像数据
            };
        }
    };
    numInput.onchange = function(){
        rangeNum = parseInt(numInput.value);
        if(pxData){
            console.log(rNumber);
            display("rchart",rNumber,"红色直方图分布",['#ff0000']);
            display("gchart",gNumber,"绿色直方图分布",['#00ff00']);
            display("bchart",bNumber,"蓝色直方图分布",['#0000ff']);
        }
    }
    //图片读取完毕后，写到canvas里面
    img.onload = function () {
        cxt.drawImage(img, 0, 0, myCanvas.width, myCanvas.height);
        var imgData = cxt.getImageData(0, 0, myCanvas.width, myCanvas.height);
        pxData = imgData.data; //获取每一个像素
        console.log("imgData", pxData);
 
        // 统计每一个像素点的RGB三通道
        rNumber = new Array(256).fill(0);
        gNumber = new Array(256).fill(0);
        bNumber = new Array(256).fill(0);
 
        for (let i = 0; i < pxData.length; i += 4) {
            rNumber[pxData[i]]++;
            gNumber[pxData[i + 1]]++;
            bNumber[pxData[i + 2]]++;
        }
        console.log("rNumber:", rNumber);
        console.log("gNumber:", gNumber);
        console.log("bNumber:", bNumber);
        display("rchart",rNumber,"红色直方图分布",['#ff0000']);
        display("gchart",gNumber,"绿色直方图分布",['#00ff00']);
        display("bchart",bNumber,"蓝色直方图分布",['#0000ff']);
    }
    function display(id,data,title,color) {
        // 基于准备好的dom，初始化echarts实例
        var myChart = echarts.init(document.getElementById(id));
        let ranges = new Array(rangeNum).fill(0),displayData = new Array(rangeNum).fill(0);
        let delt = Math.ceil(256/rangeNum);
        for(let i=0;i<rangeNum;i++){
            ranges[i] = i ;
            for(let j=0;j<delt;j++){
                displayData[i] += data[i*delt+j];
            }
        }
        // console.log(ranges);
        myChart.setOption({
            title: {
                text: title,
            },
            tooltip:{},//悬浮显示
            xAxis: {
                data: ranges
            },
            yAxis: {
                type:"value",//y轴显示区间分量的个数
            },
            series: [{
                name: '个数',
                type: 'bar',
                color:color,
                data: displayData
            }]
        },rangeNum);
    }
})();