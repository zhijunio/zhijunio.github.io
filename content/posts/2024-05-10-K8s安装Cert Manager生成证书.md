---
title: "在 Kubernetes 中安装 Cert Manager 并生成证书"
date: 2024-05-10 08:00:00+08:00
slug: install-cert-manager
tags: [ "kubernetes" ]
categories: [ "tech" ]
description: "介绍如何在 Kubernetes 中安装 Cert Manager，并通过它为集群中的服务和 Ingress 自动签发与续订 TLS 证书。"
---

cert-manager 为 Kubernetes 或 OpenShift 集群中的工作负载创建 TLS 证书，并在证书过期之前续订证书。

cert-manager 可以从各种[证书颁发机构](https://cert-manager.io/docs/configuration/issuers/)获取证书，包括： [Let's Encrypt](https://cert-manager.io/docs/configuration/acme/)、[HashiCorp Vault](https://cert-manager.io/docs/configuration/vault/)、 [Venafi](https://cert-manager.io/docs/configuration/venafi/)和[私有 PKI](https://cert-manager.io/docs/configuration/ca/)。

使用 cert-manager 的[证书资源](https://cert-manager.io/docs/usage/certificate/)，私钥和证书存储在 Kubernetes Secret 中，该 Secret 由应用程序 Pod 挂载或由 Ingress 控制器使用。使用[csi-driver](https://cert-manager.io/docs/usage/csi-driver/)、[csi-driver-spiffe](https://cert-manager.io/docs/usage/csi-driver-spiffe/)或[istio-csr](https://cert-manager.io/docs/usage/istio-csr/)，私钥是在应用程序启动之前按需生成的；私钥永远不会离开节点，并且不会存储在 Kubernetes Secret 中。

## 安装

参考官方文档：[https://cert-manager.io/docs/installation/](https://cert-manager.io/docs/installation/)

### 使用kubectl安装

```bash
kubectl apply -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.yaml
```

查看：

```bash
kubectl get pods --namespace cert-manager
```

### 使用helm安装

添加 repo：

```bash
helm repo add jetstack https://charts.jetstack.io --force-update
helm repo update
```

安装 cert-manager：

```bash
helm install cert-manager jetstack/cert-manager \
 --namespace cert-manager   \
 --create-namespace    \
 --version v1.14.5    \
 --set installCRDs=true
```

更多配置参数，参考：[https://artifacthub.io/packages/helm/cert-manager/cert-manager](https://artifacthub.io/packages/helm/cert-manager/cert-manager)

查看状态

```bash
$ kubectl -n cert-manager rollout status deploy/cert-manager
deployment "cert-manager" successfully rolled out

$ kubectl get pods -n cert-manager
NAME                                           READY   STATUS              RESTARTS   AGE
pod/cert-manager-5c47f46f57-k78l6              1/1     Running             0          91s
pod/cert-manager-cainjector-6659d6844d-tr8rf   1/1     Running             0          91s
pod/cert-manager-webhook-547567b88f-8lthd      1/1     Running         0          91s
```

使用helm3查看：

```bash
$ helm list -n cert-manager
NAME         NAMESPACE    REVISION UPDATED                                 STATUS   CHART               cert-manager cert-manager 1        2024-05-09 17:35:59.976722226 +0800 CST deployed cert-manager-v1.14.5 v1.14.5
```

### 验证

创建自签名证书进行验证：

```bash
$ cat <<EOF > test-resources.yaml
apiVersion: v1
kind: Namespace
metadata:
  name: cert-manager-test
---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: test-selfsigned
  namespace: cert-manager-test
spec:
  selfSigned: {}
---
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: selfsigned-cert
  namespace: cert-manager-test
spec:
  dnsNames:
    - example.com
  secretName: selfsigned-cert-tls
  issuerRef:
    name: test-selfsigned
EOF
```

创建 test-resources：

```bash
kubectl apply -f test-resources.yaml
```

查看证书状态：

```bash
$ kubectl describe certificate -n cert-manager-test
Name:         selfsigned-cert
Namespace:    cert-manager-test
Labels:       <none>
Annotations:  <none>
API Version:  cert-manager.io/v1
Kind:         Certificate
Metadata:
  Creation Timestamp:  2024-05-09T23:25:16Z
  Generation:          1
  Resource Version:    302521
  UID:                 4a691ab3-4a7a-476d-9cd6-028285bca5ba
Spec:
  Dns Names:
    example.com
  Issuer Ref:
    Name:       test-selfsigned
  Secret Name:  selfsigned-cert-tls
Status:
  Conditions:
    Last Transition Time:  2024-05-09T23:25:17Z
    Message:               Certificate is up to date and has not expired
    Observed Generation:   1
    Reason:                Ready
    Status:                True
    Type:                  Ready
  Not After:               2024-08-07T23:25:17Z
  Not Before:              2024-05-09T23:25:17Z
  Renewal Time:            2024-07-08T23:25:17Z
  Revision:                1
Events:
  Type    Reason     Age   From                                       Message
  ----    ------     ----  ----                                       -------
  Normal  Issuing    8s    cert-manager-certificates-trigger          Issuing certificate as Secret does not exist
  Normal  Generated  7s    cert-manager-certificates-key-manager      Stored new private key in temporary Secret resource "selfsigned-cert-f66n5"
  Normal  Requested  7s    cert-manager-certificates-request-manager  Created new CertificateRequest resource "selfsigned-cert-1"
  Normal  Issuing    7s    cert-manager-certificates-issuing          The certificate has been successfully issued
```

删除 test-resources：

```bash
kubectl delete -f test-resources.yaml
```

## 卸载

```bash
#通过kubectl删除
kubectl delete -f https://github.com/cert-manager/cert-manager/releases/download/v1.14.5/cert-manager.crds.yaml

#通过helm3删除
helm --namespace cert-manager delete cert-manager
kubectl delete namespace cert-manager
```

## 生成证书

### 概念介绍

#### Issuer

安装 cert-manager 后，您需要配置的第一件事是`Issuer`或`ClusterIssuer`。`Issuers` 和 `ClusterIssuers` 是 Kubernetes 资源，表示能够通过接受证书签名请求来生成签名证书的证书颁发机构 （CA）。所有 cert-manager 证书都需要一个处于就绪状态的引用颁发者来尝试接受请求。

一个简单的 `CA` `Issuer` 如下：

```yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: ca-issuer
  namespace: mesh-system
spec:
  ca:
    secretName: ca-key-pair
```

这是一个基于私钥对证书进行签名的简单 `Issuer` 方法。然后，存储在密钥 `ca-key-pair` 中的证书可用于 `Issuer` 在公钥基础结构 （PKI） 系统中信任新签名的证书。

Issuers 和 ClusterIssuer 区别：

- Issuers 是基于命名空间的
- ClusterIssuer 是基于集群的

#### ACME Orders 和 Challenges

cert-manager 支持使用[ACME Issuer从 ACME 服务器请求证书，包括从](https://cert-manager.io/docs/configuration/acme/)[Let's Encrypt](https://letsencrypt.org/)请求证书。这些证书通常在公共 Internet 上受到大多数计算机的信任。要成功请求证书，证书管理器必须解决已完成的 ACME 挑战，以证明客户端拥有所请求的 DNS 地址。

为了完成这些挑战，cert-manager引入了两种 `CustomResource`类型；`Orders`和`Challenges`。

ACME 支持两种验证方式：

- DNS 验证：通过 DNS01 质询，您可以通过证明您控制域名的 DNS 记录来证明其所有权。这是通过创建具有特定内容的 TXT 记录来完成的，该记录证明您拥有对域 DNS 记录的控制权
- HTTP 验证：通过 HTTP01 质询，您可以通过确保域中存在特定文件来证明域的所有权。

Let's Encrypt 的 ACME 服务器分为两种：

- 暂存环境：`https://acme-staging-v02.api.letsencrypt.org/directory`
- 生产环境：`https://acme-v02.api.letsencrypt.org/directory`

生产环境施加了更严格的速率限制，因此为了减少您达到这些限制的机会，建议测试过程中使用暂存环境。

Let’s Encrypt 利用 ACME 协议来校验域名是否真的属于你，校验成功后就可以自动颁发免费证书，证书有效期只有 90 天，在到期前需要再校验一次来实现续期，幸运的是 cert-manager 可以自动续期，这样就可以使用永久免费的证书了。如何校验这个域名是否属于你呢？主流的两种校验方式是 HTTP-01 和 DNS-01，详细校验原理可参考 [Let's Encrypt 的运作方式](https://letsencrypt.org/zh-cn/how-it-works/)，下面将简单描述下。

### Let’s Encrypt生成证书

#### ACME 颁发证书并使用 HTTP 验证

HTTP-01 的校验原理是给你域名指向的 HTTP 服务增加一个临时 location ，Let’s Encrypt 会发送 http 请求到 `http:///.well-known/acme-challenge/`，`YOUR_DOMAIN` 就是被校验的域名，`TOKEN` 是 ACME 协议的客户端负责放置的文件，在这里 ACME 客户端就是 cert-manager，它通过修改或创建 Ingress 规则来增加这个临时校验路径并指向提供 `TOKEN` 的服务。Let’s Encrypt 会对比 `TOKEN` 是否符合预期，校验成功后就会颁发证书。此方法仅适用于给使用 Ingress 暴露流量的服务颁发证书，并且不支持泛域名证书。

先创建一个颁发者，因为测试，使用暂存环境的 ACME 服务器。

```yaml
cat <<EOF > letsencrypt-staging.yaml
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    # The ACME server URL
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    # Email address used for ACME registration
    email: zhijun.lab@gmail.com
    # Name of a secret used to store the ACME account private key
    privateKeySecretRef:
      name: letsencrypt-staging
    # Enable the HTTP-01 challenge provider
    solvers:
    # An empty "selector" means that this solver matches all domains
    - selector: {}
      http01:
        ingress:
          ingressClassName: nginx
EOF
```

创建颁发者：

```bash
kubectl apply -f letsencrypt-staging.yaml
```

创建证书：

```yaml
cat <<EOF > chensoul-cc-tls.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: chensoul-cc-tls
spec:
  secretName: chensoul-cc-tls
  issuerRef:
    name: letsencrypt-staging
  commonName: test.zhijun.io
  dnsNames:
  - test.zhijun.io
EOF
```

创建证书：

```bash
$ kubectl apply -f chensoul-cc-tls.yaml
certificate.cert-manager.io/chensoul-cc-tls created
```

查看状态：

```bash
kubectl get secret,certificate,Issuer,ClusterIssuer

kubectl describe Issuer letsencrypt-staging
kubectl describe Secret cloudflare-api-token-secret

kubectl describe certificate chensoul-cc-tls
kubectl describe CertificateRequest chensoul-cc-tls
kubectl describe order chensoul-cc-tls
kubectl describe Challenge chensoul-cc-tls
```

等待一段时间，直到证书状态变为True：

```bash
$ kubectl get secret,certificate,Issuer,ClusterIssuer
NAME                                 TYPE                DATA   AGE
secret/chensoul-cc-tls               kubernetes.io/tls   2      47s
secret/cloudflare-api-token-secret   Opaque              1      2m39s
secret/letsencrypt-staging           Opaque              1      5m34s

NAME                                          READY   SECRET            AGE
certificate.cert-manager.io/chensoul-cc-tls   True    chensoul-cc-tls   2m31s

NAME                                         READY   AGE
issuer.cert-manager.io/letsencrypt-staging   True    2m39s
```

还可以查看证书的 TLS Base64 键值对：

```bash
kubectl get secret chensoul-cc-tls -o yaml
```

删除相关资源：

```bash
kubectl delete Secret cloudflare-api-token-secret letsencrypt-staging chensoul-cc-tls
kubectl delete Issuers letsencrypt-staging
kubectl delete certificate chensoul-cc-tls
```

#### ACME 颁发证书并使用 DNS 验证

DNS-01 的校验原理是利用 DNS 提供商的 API Key 拿到你的 DNS 控制权限， 在 Let’s Encrypt 为 ACME 客户端提供令牌后，ACME 客户端 (cert-manager) 将创建从该令牌和您的帐户密钥派生的 TXT 记录，并将该记录放在 `_acme-challenge.`。 然后 Let’s Encrypt 将向 DNS 系统查询该记录，如果找到匹配项，就可以颁发证书。此方法不需要你的服务使用 Ingress，并且支持泛域名证书。

参考：<https://medium.com/@sms-astanley/custom-issuers-with-letsencrypt-and-rancher-ingress-2c89ab1b0a91>

先创建一个颁发者，然后根据域名解析选择 DNS01 提供商，支持的提供商参考：<https://cert-manager.io/docs/configuration/acme/dns01/>

我的 DNS 提供商为 Cloudflare，参考 <https://cert-manager.io/docs/configuration/acme/dns01/cloudflare/> 在 [Cloudflare](https://dash.cloudflare.com/profile/api-tokens) 创建一个 API token 或者 API KEY。

```yaml
cat <<EOF > letsencrypt-staging.yaml
apiVersion: v1
kind: Secret
metadata:
  name: cloudflare-api-token-secret
type: Opaque
stringData:
  api-token: SSQ0XP71lyfFDjIMPuwtti7v-LhOQlpPe5ruK-9Z

---
apiVersion: cert-manager.io/v1
kind: Issuer
metadata:
  name: letsencrypt-staging
spec:
  acme:
    email: zhijun.lab@gmail.com
    server: https://acme-staging-v02.api.letsencrypt.org/directory
    # Name of a secret used to store the ACME account private key
    privateKeySecretRef:
      name: letsencrypt-staging
    solvers:
      - dns01:
          cloudflare:
            email: zhijun.lab@gmail.com
            apiTokenSecretRef:
              name: cloudflare-api-token-secret
              key: api-token
EOF
```

创建颁发者：

```bash
$ kubectl apply -f letsencrypt-staging.yaml
secret/cloudflare-api-token-secret created
issuer.cert-manager.io/letsencrypt-staging created
```

> 如果想将这个 Issuer 设置为默认使用，可以用如下命令升级 cert-manager
>
> ```
> helm upgrade cert-manager jetstack/cert-manager --set "extraArgs={--default-issuer-name=letsencrypt-prod,--default-issuer-kind=ClusterIssuer}" -n cert-manager
> ```

创建一个证书：

```yaml
cat <<EOF > chensoul-cc-tls.yaml
apiVersion: cert-manager.io/v1
kind: Certificate
metadata:
  name: chensoul-cc-tls
spec:
  secretName: chensoul-cc-tls
  issuerRef:
    name: letsencrypt-staging
    kind: Issuer
  commonName: test.zhijun.io
  dnsNames:
    - test.zhijun.io
EOF
```

创建证书：

```bash
$ kubectl apply -f chensoul-cc-tls.yaml
certificate.cert-manager.io/chensoul-cc-tls created
```

查看状态：

```bash
kubectl get secret,certificate,Issuer,ClusterIssuer

kubectl describe Issuer letsencrypt-staging
kubectl describe Secret cloudflare-api-token-secret

kubectl describe certificate chensoul-cc-tls
kubectl describe CertificateRequest chensoul-cc-tls
kubectl describe order chensoul-cc-tls
kubectl describe Challenge chensoul-cc-tls
```

等待一段时间，直到证书状态变为True：

```bash
$ kubectl get secret,certificate,Issuer,ClusterIssuer
NAME                                 TYPE                DATA   AGE
secret/chensoul-cc-tls               kubernetes.io/tls   2      47s
secret/cloudflare-api-token-secret   Opaque              1      2m39s
secret/letsencrypt-staging           Opaque              1      5m34s

NAME                                          READY   SECRET            AGE
certificate.cert-manager.io/chensoul-cc-tls   True    chensoul-cc-tls   2m31s

NAME                                         READY   AGE
issuer.cert-manager.io/letsencrypt-staging   True    2m39s
```

还可以查看证书的 TLS Base64 键值对：

```bash
kubectl get secret chensoul-cc-tls -o yaml
```

删除相关资源：

```bash
kubectl delete Secret cloudflare-api-token-secret letsencrypt-staging chensoul-cc-tls
kubectl delete Issuers letsencrypt-staging
kubectl delete certificate chensoul-cc-tls
```

#### 校验方式对比

HTTP-01 的校验方式的优点是: 配置简单通用，不管使用哪个 DNS 提供商都可以使用相同的配置方法；缺点是：需要依赖 Ingress，如果你的服务不是用 Ingress 暴露流量的就不适用，而且不支持泛域名证书。

DNS-01 的校验方式的优点是没有 HTTP-01 校验方式缺点，不依赖 Ingress，也支持泛域名；缺点就是不同 DNS 提供商的配置方式不一样，而且 DNS 提供商有很多，cert-manager 的 Issuer 不可能每个都去支持，不过有一些可以通过部署实现了 cert-manager 的 [Webhook](https://cert-manager.io/docs/concepts/webhook/) 的服务来扩展 Issuer 进行支持，比如 DNSPod 和 阿里 DNS，详细 Webhook 列表请参考: <https://cert-manager.io/docs/configuration/acme/dns01/#webhook>

选择哪种方式呢？条件允许的话，建议是尽量用 `DNS-01` 的方式，限制更少，功能更全。

## 参考文章

- [Make SSL certs easy with k3s](https://opensource.com/article/20/3/ssl-letsencrypt-k3s)
- <https://www.thebookofjoel.com/k3s-cert-manager-letsencrypt>
- [使用 LetsEncrypt配置kubernetes ingress-nginx免费HTTPS证书]()
- [cert-manager管理k8s集群证书]()
- <https://blog.csdn.net/xichenguan/article/details/100709830>
- <https://medium.com/@sms-astanley/custom-issuers-with-letsencrypt-and-rancher-ingress-2c89ab1b0a91>
