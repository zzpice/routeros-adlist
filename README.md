# adlist

将 [anti-AD](https://github.com/privacy-protection-tools/anti-AD) 的纯域名列表自动转换为 MikroTik RouterOS `Adlist` 可直接读取的 hosts 格式。

## 使用

生成文件：[`adlist.txt`](./adlist.txt)

Raw 地址：

```text
https://raw.githubusercontent.com/zzpice/adlist/main/adlist.txt
```

RouterOS：

```routeros
/ip/dns/adlist/add url="https://raw.githubusercontent.com/zzpice/adlist/main/adlist.txt" ssl-verify=no
```

然后检查导入结果：

```routeros
/ip/dns/adlist/print
```

`name-count` 应显示已加载的域名数量。RouterOS 会使用 DNS 缓存保存 Adlist 条目，因此请确保 DNS cache 有足够空间。

> 如果路由器已经正确配置可信 CA，可以将 `ssl-verify` 改为 `yes`。

## 自动更新

GitHub Actions 每 6 小时检查一次 anti-AD：

1. 从 `https://anti-ad.net/domains.txt` 下载最新纯域名列表；
2. 校验响应内容和域名数量；
3. 去重、排序并转换为 `0.0.0.0 domain.example` 格式；
4. 只有内容发生变化时才更新 `adlist.txt`。

RouterOS Adlist 本身也会周期性检查远程列表是否更新。

## 本地生成

只需要 Python 3，无第三方依赖：

```bash
python convert.py
```

可选参数：

```bash
python convert.py --source https://anti-ad.net/domains.txt --output adlist.txt --min-domains 50000
```

脚本采用“失败关闭”策略：如果上游下载失败、返回异常内容、有效域名数量异常偏低或格式大量异常，会直接退出，不覆盖现有可用列表。

## 数据来源

规则来自 [privacy-protection-tools/anti-AD](https://github.com/privacy-protection-tools/anti-AD)。本仓库只负责格式转换与自动发布，不修改 anti-AD 的规则内容。

## License

本仓库的转换脚本与自动化配置使用 [MIT License](./LICENSE)。上游规则的许可与归属以 anti-AD 项目为准。
