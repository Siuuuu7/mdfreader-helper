# MDF/DAT文件的常用操作
## my_lib.py 
*封装常用函数* </br>
**1. parse_mdf(filename, columns)**
&emsp; *mdfreader常用操作*</br>
- filename : dat/mdf文件名
- columns : 需要读取的通道名/缩写
</br>

    merge_to_pd : 将目标列拼接成带时间戳的DataFrame
    keyword_merge_to_pd : 用变量关键字查询并拼接成带时间戳的DataFrame
</br>

**2. pd_parse(content, label)**
&emsp; *DataFrame常用操作*</br>
- content : DataFrame
- label : 目标标签
</br>

    trace_back : 添加特征前序时间序列
    add_MeanVar ：添加特征前序时间的均值和方差等一系列前序时间内的特征
    resample : 用采样时间内的均值重采样
    initialize : 初始化，为每一行添加上一时刻或上n时刻的标签值
</br>

