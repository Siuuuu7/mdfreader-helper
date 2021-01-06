# mdfreader读取MDF/DAT文件后的常用操作
## 安装与使用
使用pip工具安装：

    pip install mdfreader_helper

从my_lib导入：

    from mdf_helper.my_lib import *
    
使用实例：
    
    filenames = glob.glob('./dat/idc/*.dat')  # 遍历文件夹内所有dat文件
    abbrs = ['n', 'wMCT', 'MCT_', 'ISC']  # 定义在文件中查找所需的信号所对应的关键字缩写。
    df = pd.DataFrame()  # 初始化dataframe
    for file in filenames:
        out = mdf_parser(file, abbrs).keyword_merge_to_pd()  # 在每个文件中依照abbrs中的关键字寻找变量对应的数据列
        #df.columns = ['Speed', 'Torque', 'blabla1', 'blabla2']
        df = pd.concat([df, out], axis=0)  # 将从每个文件中提取出的dataframe拼接成最终的大dataframe
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

