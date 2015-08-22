## 百度百科数据抽取器
project文件夹内是一个对百度百科页面的（三元组数据、标签数据）进行抽取、处理的应用程序。程序可以自动爬取百度百科页面并动态更新数据库内容。
### 准备工作
在开始部署项目前，需要准备的有：

- 数据库：MySQL(>=5.5)，需要创建一个新数据库。修改`project/settings.py`中对应的数据库名称，用户名和密码。数据库编码使用utf8_unicode_ci。
- 数据库：MongoDB(>=3.0)，用于存储爬取的网页数据，需要修改`project/settings.py`中的数据库主机名和端口。一般来说，由于百度百科页面量大，因此MongoDB需要运行在至少有500GB的目录下。
- python2.7以及相关的包：推荐使用virtualenv。

### 使用的python包
- argparse(1.3.0)
- django(1.8.3)
- lxml(3.4.4)
- MySQL-python(1.2.5)
- pymongo(3.0.3)
- pytz(2013.7)
- Scrapy(1.0.1)
- threadpool(1.2.7)
- jieba(0.36.1)

在Ubuntu上，安装上述python包之前需要执行
```apt-get install python-dev libffi-dev libssl-dev libxml2-dev libxslt1-dev```
确保相关的库已经安装。

在Mac OS X上，使用Homebrew执行
```brew install libxml2 libxslt libffi openssl```


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

在本地的 <http://localhost:8000/> 即可看到系统运行状态。

### 其他命令
- ```./manage.py bdbk_extract```：从页面内抽取数据，如果```--src```选项是```stdin```或者```page```，则直接打印输出而不存入数据库；若```--src```选项是```mongodb```，就从数据库（MongoDB）中抽取页面并存入数据库，用于页面已经爬取好的情况，此时可以指定MongoDB的地址：```--mongod-host```、```--mongod-port```，以及用于多线程处理时，可以指定页面下标的上（闭）下（开）界：```--mongod-from-to```。
- ```./extract_mongodb_dispatcher.py```：批量抽取MongoDB中的页面，可以指定MongoDB的地址：```--mongod-host```、```--mongod-port```，和多线程处理的线程数量```--worker-count```，每个线程处理的页面数量```--worker-job-count```。
- ```./manage.py spider_getproxy```：刷新代理服务器地址列表。输出的代理服务器列表可以直接存为列表文件供```./manage.py spider_start```使用。（但通常代理服务器会使速度更慢）
- ```./manage.py bdbk_discover_links```：分析三元组数据，发现新的实体间的链接。TODO。
- ```./manage.py bdbk_make_corpus```： 整理爬取的页面文本，输出corpus供[word2vec](https://code.google.com/p/word2vec/)计算词向量使用。
