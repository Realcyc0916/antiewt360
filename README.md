This file is modified from "FuckEWT360" by "493505110"

Modifications made by [Realcyc0916] in 2025.


### 2025/07/11 
#### 由于ewt界面更新等原因，本项目已暂停维护。

## antiewt360
升学e网通自动化刷课脚本



### 使用环境

需要提前配置好python运行环境
并已安装selenium插件

需要测试版的chrome浏览器以提供支持

### 使用教程

在代码中找到如下片段
```python
USER = "username"
PASS = "userpassword"
```
将其修改为自己ewt账号的账号和密码

找到
```python
chrome_options.binary_location = "C:/example.exe"
```
将```C:/example.exe```修改为你的Chrome文件地址

运行即可

### 注意事项

如果学校在“我的假期”中有提供多个选项, 请在程序启动后尽快选择需要的那一个

如果学校在网课平台中有提供试卷提交
请先提交完所有的作业再运行此程序

