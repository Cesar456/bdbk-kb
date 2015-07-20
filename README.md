### 准备工作
在开始部署项目前，需要准备的有：

- 数据库：MySQL，需要创建一个新数据库。修改`project/settings.py`中对应的数据库名称，用户名和密码。
- 数据库：MongoDB，用于存储爬取的网页数据，需要修改`project/settings.py`中的数据库主机名和端口。
- python2.7以及相关的包：推荐使用virtualenv。

### 使用的python包
- argparse(1.3.0)
- django(1.8.3)
- xml(3.4.4)
- MySQL-python(1.2.5)
- pymongo(3.0.3)
- pytz(2013.7)
- Scrapy(1.0.1)
- threadpool(1.2.7)


###初始化数据
执行：

```./manage.py syncdb```



###启动爬虫程序
执行下面的命令初始化爬虫：

```./manage.py spider_init```

执行下面的命令启动爬虫：

```./manage.py spider_start```

### 查看数据
可以先启动开发服务器，即可快速看到页面抽取状态：

```./manage.py runserver --insecure```

在本地的 <http://localhost:8000/bdbk/showTuplesForNamedEntity/random/> 即可看到系统运行状态。