# mdfreader读取MDF/DAT文件后的常用操作
## my_lib.py 
*封装常用函数，用于机器学习预处理。* </br>
**1. parse_mdf(filename, columns)**
&emsp; *mdfreader常用操作*</br>
- filename : dat/mdf文件名
- columns : 需要读取的通道名/缩写
</br>

    merge_to_pd : 将目标列拼接成带时间戳的DataFrame
    keyword_merge_to_pd : 用变量关键字查询并拼接成带时间戳的DataFrame
    signal_list_merge_to_pd：参考已知信号列表提取出本文件中存在的信号并拼接成带时间戳的DataFrame

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
    add_col : 添加时间序列新特征

</br>

