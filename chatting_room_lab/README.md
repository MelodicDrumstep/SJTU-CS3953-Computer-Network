# 计算机网络课程 lab : Chatting Room

## 环境配置

由于我使用的是 python3 进行开发， 因此需要用 `python3` 命令启动程序， 而非任务书中的 `python` 命令。您可以运行 `source env_start.sh`, 它会做 `alias python=python3`。 此外， `env_start.sh` 还会做 mininet 相关的一些必要配置。

## 启动 mininet

请运行 `sudo python topology.py`

## TCP Server-Client

### 实现概述

#### 多进程 Reactor 模式 + non blocking IO

#### 实现简单应用层协议来解决 TCP 粘包问题

#### 解决 Client 退出的问题

### 运行效果展示

![TCP](images/TCP_chatting_room.png)

### 完整启动流程

虚拟机的命令行输入:

```shell
source env_start.sh
sudo python topology.py
```

然后在 `mininet` 的命令行输入

```
xterm h1
xterm h2
xterm h3
xterm h4
```

然后在 `h1, h2, h3` 的 shell 输入

```shell
source env_start.sh
python user.py
```

在 `h4` 的 shell 输入

```shell
source env_start.sh
python server.py
```

(如果可以把 `python` 命令替换成 `python3` 命令， 那么 xterm 中的 `source env_start.sh` 可以省去)

### 解决

## UDP Broadcast

对于基于 UDP 广播的 chatting room

我最初在本地使用的是 multicast, 相关代码如下:

```python
    # Join the multicast group
    group = socket.inet_aton(self.broadcast_ip_)
    mreq = struct.pack('4sL', group, socket.INADDR_ANY)
    recv_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, mreq)
```

后来在虚拟机上测试的时候发现虚拟机好像不支持 multicast, 或者是我没有正确配置， 因此我在最终的版本中删去了这几行和 multicast 相关的代码，只使用了 broadcast。

### 运行效果展示

![UDPBroadcast](images/UDP_chatting_room.png)

### 完整启动流程

虚拟机的命令行输入:

```shell
source env_start.sh
sudo python topology.py
```

然后在 `mininet` 的命令行输入

```
xterm h1
xterm h2
xterm h3
xterm h4
```

然后在 `h1, h2, h3, h4` 的 shell 输入

```shell
source env_start.sh
python udpclient.py
```

(如果可以把 `python` 命令替换成 `python3` 命令， 那么 xterm 中的 `source env_start.sh` 可以省去)