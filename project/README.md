### 准备工作
在开始部署项目前，需要准备的有：

- 数据库：MySQL，需要创建一个新数据库。修改`project/settings.py`中对应的数据库名称，用户名和密码。
- python2.7以及相关的包：推荐使用virtualenv。使用到的包：lxml(3.4.4)、django(1.7.1)、mysql-python、threadpool、pymongo（如果使用了mongo DB作为爬虫的存储数据库）。

###初始化数据
执行：

```./manage.py syncdb```



###从百度百科页面源抽取数据
执行抽取的脚本是`extract_tuples_from_infobox.py`。