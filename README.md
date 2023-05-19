# autoamap
[![hacs_badge](https://img.shields.io/badge/HACS-Custom-41BDF5.svg)](https://github.com/hacs/integration)
[![ha-inkwavemap version](https://img.shields.io/badge/autoamap-2023.5.19-blue.svg)](https://github.com/dscao/autoamap)
![visit](https://visitor-badge.glitch.me/badge?page_id=dscao.autoamap&left_text=visit)

 高德地图车机版 for homeassistant
 
New features in version 2023

support Integration UI, Devices

通过集成配置

需要用手机抓包拿到的几个数据，打开高德地图手机版，进行抓包：\
key： /ws/tservice/internal/link/mobile/get?ent=2&in= 网址后面很长很长的字符串，全部复制地来。\
sessionid:  cpuywkud2f0jvhpXXXXXXXXXX  请求头部的sessionid内容\
paramdata： oMYpXXXXXXXXXX  请求主体表单内容\

此版本请使用homeassistant 2022.2以后的版本
