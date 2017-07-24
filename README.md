ZJU jwb to iCalendar
====================

将浙江大学教务网课程导出为 iCalendar 文件（可用于 iCal、Google Calendar 等）。

## 需要维护的配置

见[data.py](data.py)，需要配置 `exam_year`, `exam_semester`(考试学期), `week_start`(秋冬/春夏学期的第一周星期一)

## 文件说明

由于后端部署为[阿里云函数计算](https://help.aliyun.com/document_detail/54788.html)，所以需要将所有的依赖包均放入项目中

本项目中`bs4`, `dateutil`, `icalendar`, `pytz`, `requests` 文件夹以及 `six.py` 均为依赖包，使用类似于`pip install requests==2.11.1 -t .`命令得到；特别地 pytz中删除了无关的大量时区文件

本项目中的`EasyLogin.py`为@zjuchenyuan开发的一个爬虫单文件库，[项目地址](https://github.com/zjuchenyuan/EasyLogin)

本项目的主要文件为[grabber.py](grabber.py)，入口文件为[index.py](index.py)，前端文件为[jwbtools.html](https://api.py3.io/jwbtools.html)

## 本地使用

[下载本项目](https://codeload.github.com/zjuchenyuan/zju-jwb-to-icalendar/zip/master)后，运行以下命令，将把`output.ics`文件生成在当前目录

```
python2 grabber.py 你的学号 你的教务网密码
```


## 部署方法

### 1.前期准备工作

* 注册[阿里云](https://promotion.aliyun.com/ntms/act/ambassador/sharetouser.html?userCode=x20mh6hn&productCode=vm)、[又拍云](https://console.upyun.com/register/?invite=Sku7XUArZ), 并完成相关实名认证等操作
* 一个已经备案的域名(这里我用api.py3.io)
* 准备好相应https证书，如果使用又拍云可以CNAME后在线免费申请Let's encrypt证书，也可以使用阿里云证书服务申请到免费1年的Symantec证书，还可以自行申请Let's encrypt证书：参见[教程-获得Let's encrypt免费https证书](https://py3.io/Nginx.html#lets-encrypthttps)
* Linux 64位 环境，可以用Bash on Win10

### 2.配置阿里云函数计算

建议阅读[官方文档](https://help.aliyun.com/product/50980.html)中[产品定价](https://help.aliyun.com/document_detail/54301.html), [快速入门-hello world](https://help.aliyun.com/document_detail/51783.html), [Python编程指南](https://help.aliyun.com/document_detail/56316.html)

函数计算控制台：[https://fc.console.aliyun.com/](https://fc.console.aliyun.com/)

新建服务，记住你填写的服务名称(我的是apipy3io)和所属区域(华东2)

下载官方工具fcli：[下载地址](https://github.com/aliyun/fcli/releases)，注意其中的**Windows版本不能使用**(针对v0.5版本)

下载后目录结构如下：

```
|-ical #简便起见，git clone后将zju-jwb-to-icalendar重命名为ical
| |-index.py
| |-grabber.py
| |-...
|-fcli
```

bash进入当前目录:

```
$ find . -name \*.pyc | xargs rm #删除pyc文件，以减小代码包体积
$ ./fcli shell
# 第一次启动需要配置账号id, AK 和 SK; 参见：https://help.aliyun.com/document_detail/51783.html
>>> ls #显示当前的服务列表 #此命令应该会输出apipy3io
>>> cd apipy3io #进入该服务
>>> mkf jwbtools -d ical --etag 20170723 -h index.index -t python2.7
# 创建函数，名为jwbtools，代码文件夹为ical，etag可选用于备注本次部署的版本，-h为函数入口 表示index.py中的index函数作为入口，python2.7为代码语言和版本
```

进入函数计算控制台，在函数列表中现在能看到新创建的`jwbtools`函数，点击进入后左侧代码执行

触发自定义事件，输入（其中的用户名xh和密码123456可以改为正确值），输入说明：整个就是event的dict，而在python中接受到的event是string需要用json.loads，body是一个json dict string，注意json中的双引号转义

```
{
    "body": "{\"username\": \"xh\",\"password\": \"123456\"}"
}
```

看到执行结果为：

```
{ "body": "RXJyb3I6IExvZ2luRXJyb3I6IFdyb25nIFN0dWRlbnQgSUQgPGJyPjxhIGhyZWY9J2phdmFzY3JpcHQ6d2luZG93Lmhpc3RvcnkuZ28oLTEpJz7miLPmiJHov5Tlm548L2E+", "headers": { "Content-Type": "text/html; charset=utf-8" }, "isBase64Encoded": true, "statusCode": 500 }
```

表示成功部署，对返回的内容感兴趣的你可以自行用linux的`base64 -d`解码返回的`body`内容

## 3.配置API网关

### 阅读[官方文档](https://help.aliyun.com/document_detail/54788.html), 关于本文档，我有几点要说的：

1. 实现原理的图仔细看，其中API网关向FunctionCompute传入的"body"是json dict string; 函数计算返回可以为302跳转，但返回的headers中的`Content-Type`会被无视；如果函数计算返回的dict不符合API网关的要求，用户会得到空白页面503 Service Unavailable

2. 快速配置API中的创建函数部分不能使用其图中的hello world程序，而应该使用其下方3.3示例的撞墙式程序

3. 其中`2.2配置跨服务授权Role和policy`可以直接跳过，现在可以一键配置 无需手工操作

4. 阅读到`4.多环境`之前即可结束，我们不需要再增加复杂度

读好了文档，我们进入[API网关控制台](https://apigateway.console.aliyun.com/), 在华东2区域(与上述第二步选择的区域一致)，创建分组，分组名称可以与前述的apipy3io重名

### 然后在`API列表`页面创建API:

#### 基本信息

选择分组(apipy3io)，API名称(jwbtools)， 安全认证 必须选择**无认证**(否则调用API需要签名机制，无法作为post后端给用户使用；顺带说一下类型中的阿里云APP不是手机上的阿里云APP而是Application的意思)，类型 私有，描述随意(教务网课表导出为ics)

#### 定义API请求

协议HTTP(因为API网关的https好像挂了，即使选择https也不能用)，自定义域名现在不管，请求Path填/jwbtools(与前端一致即可)，HTTP Method选择post；入参定义添加一条：参数名username，参数位置Body，类型String，必填打钩，编辑更多-最大长度10（学号的长度是10），编辑更多-参数验证填`[0-9]+`表示只接受数字输入；再添加一条：参数名password，参数位置Body，类型String，必填

#### 定义API后端服务

后端服务类型选FunctionCompute，区域选华东2(上海)(与前述一致)，Service填函数计算的服务名称(apipy3io)，Function填函数名称(jwbtools)，RoleArn不要填点击右侧`获取授权`一键填写，后端超时填30000ms表示30s，Content-Type保持默认，Mock不使用Mock；填完后下一步

#### 定义返回结果

返回类型选择HTML（这里选择的其实就是返回给用户的Content-Type，所以函数计算返回的Content-Type会被忽略），返回结果示例和失败返回结果示例随意乱填即可；最后保存

### 发布API，别忘了这一步

回到API列表，点击jwbtools右侧的发布，发布环境线上，变更备注随意填写(第一次部署)

### 测试API

折腾了这么多，总算配置好了API网关和函数计算，现在我们就来验证一下能不能用吧：

在API网关控制台-分组管理中，找到分组的二级域名，如我的`78145f4bd729479cb9369c9f565fba80-cn-shanghai.alicloudapi.com`

编辑本地文件jwbtools.html，修改其中form的action到上述二级域名和配置的Path: `http://78145f4bd729479cb9369c9f565fba80-cn-shanghai.alicloudapi.com/jwbtools`

然后浏览器打开，提交看看

### 注意事项，一定要看这里

如果后续在API控制台修改了上述`配置API网关`的任何一部分，一定要再次发布才会生效！

如果用fcli传了新的代码(在`fcli shell`中用`rm -f`删除函数后重新`mkf`)，则无需修改API网关

## 4. 配置https的自定义域名

由于目前(2017/07/23)阿里云的API网关的https功能无法使用，所以使用又拍云CDN向外提供服务

登录[又拍云控制台](https://console.upyun.com/dashboard/)，服务-创建服务-全网加速服务：服务名称(apipy3io)，源站类型自主源，加速域名(api.py3.io要求备案)，回源Host填API网关提供的二级域名(78145f4bd729479cb9369c9f565fba80-cn-shanghai.alicloudapi.com), 回源协议HTTP，回源地址也填这个二级域名，其他配置保持默认后创建

进入功能配置，看到域名管理给出了CNAME配置 `apipy3io.b0.aicdn.com`，进入域名DNS配置，配置CNAME解析

进入功能配置-云安全，开启WAF保护(反正免费)，可以自己配置IP访问限制和CC防护，以应对攻击

进入云产品-SSL证书服务，申购证书或者上传自定义证书

进入功能配置-HTTPS配置，配置域名证书，开启强制https访问

记得相应地把前端`jwbtools.html`中的action地址修改噢~

## 5.（可选）使用又拍云CDN存储前端html

既然都用api.py3.io域名作为后端域名了，前端也用它也好

又拍云控制台进入服务，功能配置-高级功能-镜像存储 开启，功能配置-基础功能-已授权管理员-创建操作员并授权

使用FlashFXP等FTP工具或UpYunManager官方工具，ftp连接信息：

```
地址：v0.ftp.upyun.com
加密：选择“显式的 FTP over TLS”使用 FTPS
用户名：操作员名/服务名，如 "operator/mybucket"（需要两个同时填写，字符'/'是用户名的一部分）
密码：操作员的密码
```

然后上传前端文件`jwbtools.html`即可

# 在线使用

经过以上部署，得到网址：[https://api.py3.io/jwbtools.html](https://api.py3.io/jwbtools.html)

欢迎使用，更欢迎Star~

Welcome for Star, Issue and PR!

# Credits

[@xhacker](https://github.com/xhacker), @cMc_SARS

# LICENSE

MIT