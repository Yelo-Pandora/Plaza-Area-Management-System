# docker环境部署说明

该文档用作docker环境的下载安装和项目环境的部署说明

该项目采用本地开调试+docker部署的方式



## 代码拉取

从github上的main分支拉取项目代码，对于本次开发的环境，在vs上需勾选node.js开发和python开发负载。

对于python环境，统一选用3.12版本（如果本地已有3.12环境且已经安装了一系列包，则请创建一个虚拟环境，不然使用VS更新requirement.txt会多出很多多余的包）



## docker及镜像的下载与部署

1. 先去docker官方网站下载docker desktop，注册后可以查看镜像和容器的状态

2. 可以直接在`docker-compose.yml`同级目录下使用下述指令完成docker环境的一键部署：

```

docker compose up --build

```

3. 有时会遇到使用该指令下载镜像时连接超时的情况，此时可以通过docker desktop手动下载镜像，该项目需要的镜像为：

postgis/postgis:latest

python:3.12-slim

node:22.17.1

nginx:stable-perl

4. docker容器部署完成后，容器内数据库的5432端口映射到的是主机的5433端口（防冲突）；后端的8000 Django端口映射到主机的8081端口；前端的80端口映射到主机的8080端口。



## 数据库设置

使用的数据库名称为\*PlazaDB\*，数据库用户名为*DBManager*，数据库密码为*PostgresServer*

`db-init/`为数据库初始化文件夹，容器首次启动时会自动加载并运行该文件夹的SQL脚本，除了初始化表结构之外，还可以用来存放用来初始化的数据。

