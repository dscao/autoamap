# autoamap
 高德地图车机版 for homeassistant
 
New features in version 2022

support Integration UI, Devices

通过集成配置

需要用手机抓包拿到的几个数据，打开高德地图手机版，进行抓包：\
key： /ws/tservice/internal/link/mobile/get?ent=2&in= 网址后面很长的字条串，全部复制地来。\
sessionid:  cpuywkud2f0jvhpXXXXXXXXXX  请求头中的sessionid内容\
post主体参数： oMYpXXXXXXXXXX  请求的主体内容\
