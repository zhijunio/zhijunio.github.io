---
title: "CentOS 7 用 yum 安装 GitLab Server 完整指南"
date: 2024-07-15 08:00:00+08:00
slug: install-gitlab-using-yum
tags: [ "gitlab" ]
description: "记录通过 yum 源安装和部署 GitLab Server 的过程，包括环境准备、基础配置和服务启动步骤。"
---

## Gitlab Server 部署

### 1、环境配置

关闭防火墙、SELinux

开启邮件服务

```shell
systemctl start  postfix
systemctl enable postfix
```

### 2、手动安装

#### 1、安装 gitlab 依赖包

centos7:

```shell
yum install -y curl openssh-server openssh-clients postfix cronie policycoreutils-python
```

> gitlab-ce 10.x.x以后的版本需要依赖policycoreutils-python

centos8:

```bash
yum install -y curl openssh-server openssh-clients postfix cronie  policycoreutils-python-utils
```

#### 2、添加官方源

```shell
curl https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.rpm.sh | sudo bash
```

因为官方源太慢，可以使用国内清华yum源，配置如下

```bash
$ vim /etc/yum.repos.d/gitlab-ce.repo
[gitlab-ce]
name=Gitlab CE Repository
baseurl=https://mirrors.tuna.tsinghua.edu.cn/gitlab-ce/yum/el$releasever/
gpgcheck=0
enabled=1
```

#### 3、安装 Gitlab

自动安装最新版

```shell
yum -y install gitlab-ce                    
```

#### 4、配置 Gitlab

##### 1、查看Gitlab版本

```shell
$ head -1 /opt/gitlab/version-manifest.txt
gitlab-ce 10.1.1
```

##### 2、Gitlab 配置登录链接

``` shell
#设置登录链接
$ vim /etc/gitlab/gitlab.rb
***
## GitLab URL
##! URL on which GitLab will be reachable.
##! For more details on configuring external_url see:
##! https://docs.gitlab.com/omnibus/settings/configuration.html#configuring-the-external-url-for-gitlab
# 没有域名，可以设置为本机IP地址
external_url "http://172.17.0.61"
***
$ grep "^external_url" /etc/gitlab/gitlab.rb
external_url "http://172.17.0.61"     #绑定监听的域名或IP
```

##### 3、初始化 Gitlab

**配置语言环境**

gitlab要求语言环境为英文环境，必须切换，切换方法如下：

```bash
echo "export LC_ALL=en_US.UTF-8"  >>  /etc/profile 
```

退出终端重新登陆。

如果上面的方案不可以，再使用下面的方案：  

```bash
$ yum install langpacks-zh_CN langpacks-en langpacks-en_GB -y

$ cat > /etc/profile.d/locale.sh<<-EOF
 export LANG=en_US.UTF-8
 export LANGUAGE=en_US.UTF-8
 export LC_COLLATE=C
 export LC_CTYPE=en_US.UTF-8
EOF

$ source /etc/profile.d/locale.sh
```

第一次使用配置时间较长

``` shell
$ gitlab-ctl reconfigure   
.....
```

##### 4、启动 Gitlab 服务

``` shell
$ gitlab-ctl start
ok: run: gitaly: (pid 22896) 2922s
ok: run: gitlab-monitor: (pid 22914) 2921s
ok: run: gitlab-workhorse: (pid 22882) 2922s
ok: run: logrotate: (pid 22517) 2987s
ok: run: nginx: (pid 22500) 2993s
ok: run: node-exporter: (pid 22584) 2974s
ok: run: postgres-exporter: (pid 22946) 2919s
ok: run: postgresql: (pid 22250) 3047s
ok: run: prometheus: (pid 22931) 2920s
ok: run: redis: (pid 22190) 3053s
ok: run: redis-exporter: (pid 22732) 2962s
ok: run: sidekiq: (pid 22472) 3005s
ok: run: unicorn: (pid 22433) 3011s

$ lsof -i:80
COMMAND   PID       USER   FD   TYPE DEVICE SIZE/OFF NODE NAME
nginx   22500       root    7u  IPv4  50923      0t0  TCP *:http (LISTEN)
nginx   22501 gitlab-www    7u  IPv4  50923      0t0  TCP *:http (LISTEN)
```

##### 5、Gitlab 设置 HTTPS 方式 （缺少配置）

如果想要以上的 https 方式正常生效使用，则需要把 letsencrypt 自动生成证书的配置打开，这样在执行重新让配置生效命令 (gitlab-ctl reconfigure) 的时候会自动给域名生成免费的证书并自动在 gitlab 自带的 nginx 中加上相关的跳转配置，都是全自动的，非常方便。

```shell
$ vim /etc/gitlab/gitlab.rb
letsencrypt["enable"] = true /如果因为这行报错，改成false即可
letsencrypt["contact_emails"] = ["testqq@qq.com"]     # 添加联系人的电子邮件地址
```

##### 6、Gitlab 添加smtp邮件功能

``` shell
$ vim /etc/gitlab/gitlab.rb
postfix 并非必须的；根据具体情况配置，以 SMTP 的为例配置邮件服务器来实现通知；参考配置如下： 
### Email Settings
gitlab_rails["gitlab_email_enabled"] = true
gitlab_rails["gitlab_email_from"] = "testqq@qq.com"
gitlab_rails["gitlab_email_display_name"] = "gitlab"
gitlab_rails["gitlab_email_reply_to"] = "testqq@qq.com"
gitlab_rails["gitlab_email_subject_suffix"] = "[gitlab]"
gitlab_rails["smtp_enable"] = true
gitlab_rails["smtp_address"] = "smtp.qq.com"
gitlab_rails["smtp_port"] = 465
gitlab_rails["smtp_user_name"] = "testqq@qq.com"
gitlab_rails["smtp_password"] = "kktohrvdryglbjjh" #这是我的qq邮箱授权码
gitlab_rails["smtp_domain"] = "smtp.qq.com"
gitlab_rails["smtp_authentication"] = "login"
gitlab_rails["smtp_enable_starttls_auto"] = true
gitlab_rails["smtp_tls"] = true

#修改配置后需要初始化配置，先关掉服务再重新初始化
$ gitlab-ctl stop
ok: down: gitaly: 0s, normally up
ok: down: gitlab-monitor: 1s, normally up
ok: down: gitlab-workhorse: 0s, normally up
ok: down: logrotate: 1s, normally up
ok: down: nginx: 0s, normally up
ok: down: node-exporter: 1s, normally up
ok: down: postgres-exporter: 0s, normally up
ok: down: postgresql: 0s, normally up
ok: down: prometheus: 0s, normally up
ok: down: redis: 0s, normally up
ok: down: redis-exporter: 1s, normally up
ok: down: sidekiq: 0s, normally up
ok: down: unicorn: 1s, normally up

$ gitlab-ctl reconfigure  
......

$ gitlab-ctl start
ok: run: gitaly: (pid 37603) 0s
ok: run: gitlab-monitor: (pid 37613) 0s
ok: run: gitlab-workhorse: (pid 37625) 0s
ok: run: logrotate: (pid 37631) 0s
ok: run: nginx: (pid 37639) 1s
ok: run: node-exporter: (pid 37644) 0s
ok: run: postgres-exporter: (pid 37648) 1s
ok: run: postgresql: (pid 37652) 0s
ok: run: prometheus: (pid 37660) 1s
ok: run: redis: (pid 37668) 0s
ok: run: redis-exporter: (pid 37746) 0s
ok: run: sidekiq: (pid 37750) 1s
ok: run: unicorn: (pid 37757) 0s
```

##### 7、Gitlab 发送邮件测试

``` shell
$ gitlab-rails console 
[root@wing ~]# gitlab-rails console
---------------------------------------------------------------------
 GitLab:       12.10.1 (e658772bd63) FOSS
 GitLab Shell: 12.2.0
 PostgreSQL:   11.7
---------------------------------------------------------------------
Loading production environment (Rails 6.0.2)
irb(main):003:0> 
irb(main):004:0> Notify.test_email("testqq@qq.com", "Message Subject", "Message Body").deliver_now  /输入测试命令，回车

Notify#test_email: processed outbound mail in 5.2ms
Delivered mail 5eafceaa250a_1d063fb777add9a08601a@wing.mail (1430.1ms)
Date: Mon, 04 May 2020 16:13:30 +0800
From: gitlab <testqq@qq.com>
Reply-To: gitlab <testqq@qq.com>
To: testqq@qq.com
Message-ID: <5eafceaa250a_1d063fb777add9a08601a@wing.mail>
Subject: Message Subject
Mime-Version: 1.0
Content-Type: text/html;
 charset=UTF-8
Content-Transfer-Encoding: 7bit
Auto-Submitted: auto-generated
X-Auto-Response-Suppress: All

<!DOCTYPE html PUBLIC "-/W3C/DTD HTML 4.0 Transitional/EN" "http://www.w3.org/TR/REC-html40/loose.dtd">
<html><body><p>Message Body</p></body></html>

=> #<Mail::Message:70056859616080, Multipart: false, Headers: <Date: Mon, 04 May 2020 16:13:30 +0800>, <From: gitlab <testqq@qq.com>>, <Reply-To: gitlab <testqq@qq.com>>, <To: testqq@qq.com>, <Message-ID: <5eafceaa250a_1d063fb777add9a08601a@wing.mail>>, <Subject: Message Subject>, <Mime-Version: 1.0>, <Content-Type: text/html; charset=UTF-8>, <Content-Transfer-Encoding: 7bit>, <Auto-Submitted: auto-generated>, <X-Auto-Response-Suppress: All>>
irb(main):005:0> 
```

去qq邮箱web界面查看是否收到邮件。

### 3、一键安装

```bash
curl -s https://packages.gitlab.com/install/repositories/gitlab/gitlab-ce/script.rpm.sh | sudo bash
```

## Gitlab 的使用

**在浏览器中输入 <http://192.168.1.178/> ，然后 change password:  ，并使用root用户登录 即可 (后续动作根据提示操作)**

### 1、Gitlab 命令行修改密码

```shell
$ gitlab-rails console production
irb(main):001:0>user = User.where(id: 1).first      # id为1的是超级管理员
irb(main):002:0>user.password = "yourpassword"      # 密码必须至少8个字符
irb(main):003:0>user.save!                          # 如没有问题 返回true
exit             # 退出
```

### 2、Gitlab服务管理

```shell
gitlab-ctl start                        # 启动所有 gitlab 组件；
gitlab-ctl stop                         # 停止所有 gitlab 组件；
gitlab-ctl restart                      # 重启所有 gitlab 组件；
gitlab-ctl status                       # 查看服务状态；
gitlab-ctl reconfigure                  # 初始化服务；
vim /etc/gitlab/gitlab.rb               # 修改默认的配置文件；
gitlab-ctl tail                         # 查看日志；
```

### 3、登陆 Gitlab

**如果需要手工修改nginx的port ，可以在gitlab.rb中设置 nginx["listen_port"] = 8000 ，然后再次 gitlab-ctl reconfigure即可**

### 4、去掉用户的自动注册功能（安全）

admin are -> settings -> Sign-up Restrictions 去掉钩钩，然后拉到最下面保存，重新登录。

## Gitlab 备份与恢复

### 1、查看系统版本和软件版本

```shell
$ cat /etc/redhat-release 
CentOS Linux release 7.3.1611 (Core) 

$ cat /opt/gitlab/embedded/service/gitlab-rails/VERSION
8.15.4
```

### 2、数据备份

#### 1、查看备份相关的配置项

```shell
$ vim /etc/gitlab/gitlab.rb
gitlab_rails["manage_backup_path"] = true
gitlab_rails["backup_path"] = "/data/gitlab/backups"
```

该项定义了默认备份出文件的路径，可以通过修改该配置，并执行 **gitlab-ctl reconfigure 或者 gitlab-ctl  restart** 重启服务生效。

#### 2、执行备份命令进行备份

```shell
/opt/gitlab/bin/gitlab-rake gitlab:backup:create 
```

#### 3、添加到 crontab 中定时执行

```shell
$ crontab -e
0 2 * * * bash /opt/gitlab/bin/gitlab-rake gitlab:backup:create
```

可以到/data/gitlab/backups找到备份包，解压查看，会发现备份的还是比较全面的，数据库、repositories、build、upload等分类还是比较清晰的。

#### 4、设置备份保留时长

防止每天执行备份，有目录被爆满的风险，打开/etc/gitlab/gitlab.rb配置文件，找到如下配置：

```shell
$ vim /etc/gitlab/gitlab.rb
gitlab_rails["backup_keep_time"] = 604800
```

设置备份保留7天（7*3600*24=604800），秒为单位，如果想增大或减小，可以直接在该处配置，并通过gitlab-ctl restart 重启服务生效。

备份完成，会在备份目录中生成一个当天日期的tar包。

### 3、数据恢复

#### 1、安装部署 gitlab server

 具体步骤参见上面：gitlab server 搭建过程

#### 2、恢复 gitlab

##### 1、查看备份相关的配置项

```shell
$ vim /etc/gitlab/gitlab.rb
gitlab_rails["backup_path"] = "/data/gitlab/backups"
```

修改该配置，定义了默认备份出文件的路径，并执行 **gitlab-ctl reconfigure 或者 gitlab-ctl  restart** 重启服务生效。

##### 2、恢复前需要先停掉数据连接服务

```shell
gitlab-ctl stop unicorn
gitlab-ctl stop sidekiq
```

- 如果是台新搭建的主机，不需要操作，理论上不停这两个服务也可以。停这两个服务是为了保证数据一致性。

##### 3、同步备份文件到新服务器

将老服务器/data/gitlab/backups目录下的备份文件拷贝到新服务器上的/data/gitlab/backups

```shell
rsync -avz 1530773117_2019_03_05_gitlab_backup.tar 192.168.95.135://data/gitlab/backups/ 
```

- 注意权限：600权限是无权恢复的。 实验环境可改成了777，生产环境建议修改属主属组

```shell
$ pwd
/data/gitlab/backups
$ chown -R git.git 1530773117_2019_03_05_gitlab_backup.tar 
$ ll
total 17328900
-rwxrwxrwx 1 git git 17744793600 Jul  5 14:47 1530773117_2018_07_05_gitlab_backup.tar
```

##### 4、执行命令进行恢复

后面再输入两次 yes 就完成恢复了。

```shell
$ gitlab-rake gitlab:backup:restore BACKUP=1530773117_2018_07_05_gitlab_backup.tar
注意：backups 目录下保留一个备份文件可直接执行
```

##### 5、恢复完成启动服务

恢复完成后，启动刚刚的两个服务，或者重启所有服务，再打开浏览器进行访问，发现数据和之前的一致：

```shell
$ gitlab-ctl start unicorn
$ gitlab-ctl start sidekiq
或
$ gitlab-ctl restart
```

**注意：通过备份文件恢复gitlab必须保证两台主机的gitlab版本一致，否则会提示版本不匹配**

## 利用Gitlab管理k8s集群

### 1、权限设置

用户设置 -> 网络，白名单以允许来自钩子和服务的对本地网络的请求，填入 K8S 集群 api-server 的地址。

### 2、获取k8s集群API地址

```yaml
$ kubectl cluster-info | grep "Kubernetes master" | awk "/http/ {print $NF}"
https://192.168.19.200:6443
```

### 3、获取k8s集群默认CA证书

```bash
$ kubectl get secrets
NAME                  TYPE                                  DATA   AGE
default-token-cvfqx   kubernetes.io/service-account-token   3      3d21h
```

default-token-cvfqx 为上面获取到的secrets的名称，用以下命令查看证书

```bash
$ kubectl get secret default-token-cvfqx  -o jsonpath="{["data"]["ca\.crt"]}" | base64 --decode
-----BEGIN CERTIFICATE-----
MIICyDCCAbCgAwIBAgIBADANBgkqhkiG9w0BAQsFADAVMRMwEQYDVQQDEwprdWJl
cm5ldGVzMB4XDTIwMDgxNzA5MjAwMFoXDTMwMDgxNTA5MjAwMFowFTETMBEGA1UE
AxMKa3ViZXJuZXRlczCCASIwDQYJKoZIhvcNAQEBBQADggEPADCCAQoCggEBANIM
iOGHeolaxkE+kqZtc8kDbGFhwqGxNxg4orbIjrz/Z6vrgqo2COn2NjKrVM11bmz
VhHPCruc3snfTLIS+/Z6gZqgpw5ruX8OjfH4nhr9npKxdBon3soa10EovPwMz1KW
laqbuLKTbtTm+oCtAKYXUlzqrFGR/GW2D3bjl1QGOPbAR0pggdxSpPo6oUgtEQJ
QAsNOJ40qMjevi3fnrNDrMqmcNKlSlkw8+Gf4TqM1EfAERRHiEcb/W3hOGWV0gdm
vaq7CE/ENeD1O11NE76BMmk5WO0u6ot4OmP35TTlx8K0N/WPyq76RlH7somiIb8S
1NpAzg+9K0vv1QmILScCAwEAAaMjMCEwDgYDVR0PAQH/BAQDAgKkMA8GA1UdEwEB
/wQFMAMBAf8wDQYJKoZIhvcNAQELBQADggEBAEVgIlTFDoFhb3KA0RMVjckgsP3O
OB7vTEws6w9ZDGJsNlbbCa15f8q3VmERSkfjAhfG4I9gb4KI0CM5Xt3JhU76GWsO
ZXHDfK7AzDGpLPUxlygkK7c7XCES/GEJe5agBxQyCo2pAvcj/nb+JIBeSh8JcG05
pzPhL11it9hDqmS5k92+63xGs/SDEzXEbBVMnyZWiv+AOHlO1/IFofUD3VHcSRMY
wH5j6Irc0p0XTnFg+GHBpqjxwMWxP6IxdVrsOWUALM5oOJYn4aJQy5kSpJFkwNW8
xDvVgtOWq5P9fVfnE4Am0LI/DevzYtcr3O9hUmCfEOnF0hC0n4ghYOPqiB4=
-----END CERTIFICATE-----
```

### 4、设置rbac

```bash
$ vim gitlab-admin-service-account.yaml
apiVersion: v1
kind: ServiceAccount
metadata:
  name: gitlab-admin
  namespace: kube-system
---
apiVersion: rbac.authorization.k8s.io/v1beta1
kind: ClusterRoleBinding
metadata:
  name: gitlab-admin
roleRef:
  apiGroup: rbac.authorization.k8s.io
  kind: ClusterRole
  name: cluster-admin
subjects:
- kind: ServiceAccount
  name: gitlab-admin
  namespace: kube-system

$ kubectl apply -f gitlab-admin-service-account.yaml
serviceaccount/gitlab-admin created
clusterrolebinding.rbac.authorization.k8s.io/gitlab-admin created
```

### 5、获取gitlab-admin的token

```yaml
$ kubectl -n kube-system describe secret $(kubectl -n kube-system get secret | grep gitlab-admin | awk "{print $1}")
Name:         gitlab-admin-token-pmb2h
Namespace:    kube-system
Labels:       <none>
Annotations:  kubernetes.io/service-account.name: gitlab-admin
              kubernetes.io/service-account.uid: bc9e1f94-088d-41f4-8e18-f31f1e9a9369

Type:  kubernetes.io/service-account-token

Data
====
ca.crt:     1025 bytes
namespace:  11 bytes
token:      eyJhbGciOiJSUzI1NiIsImtpZCI6InluNWZyY3V5T1BjNmFFQlpmRVBmOGFOenRmVkx1U0dCRDFhT0s5dEtGeXMifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJnaXRsYWItYWRtaW4tdG9rZW4tcG1iMmgiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC5uYW1lIjoiZ2l0bGFiLWFkbWluIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQudWlkIjoiYmM5ZTFmOTQtMDg4ZC00MWY0LThlMTgtZjMxZjFlOWE5MzY5Iiwic3ViIjoic3lzdGVtOnNlcnZpY2VhY2NvdW50Omt1YmUtc3lzdGVtOmdpdGxhYi1hZG1pbiJ9.HGNf2_q_NS7ASk2ID6Y658PMpDIruFLr70VGk9I_dAP-rYt81FarjQhIQPn554SrtmiTp-iQ_j7slX_YRsGHlpo74VrBM2SirDToXobuSpe77v6MFx6Ol2UsUrxY0ulm_DAjOhZ16jlohPWlhkP0083KBfywwdpyF2oVdALQnT4sI1aDxgUHs-Pmg6D0NbdN0Ipb--s-Z59QKGr1XH4Pp0Qb9kze6KCJSWOk8-4pwtpQcT7K2MA1ucyEJB283D5ChQSddo9q7pBkEwq94TLy-ZbAhHgO89OqVIjY-3H-rb5Kd3meGrtGJZJscx7xnn6_DEvbBwp8DmCoM4vfFLUUow
```

### 6、添加k8s集群

管理执行 -> Kubernetes，添加k8s集群
