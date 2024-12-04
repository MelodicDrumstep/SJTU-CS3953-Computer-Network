# 启动 xterm

需要安装 xterm

然后执行命令 `export DISPLAY=:0.0` 与 `xhost +`

启动 mininet 时， 添加 `-E` 和 `-x` 参数: `sudo python3 topology.py -E -x`