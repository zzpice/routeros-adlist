# RouterOS Adlist

将 anti-AD 自动转换为 MikroTik RouterOS DNS Adlist 可直接使用的 hosts 规则。

[接入说明](#快速使用) · [下载 adlist.txt](https://raw.githubusercontent.com/zzpice/routeros-adlist/main/adlist.txt) · [ZZP · 所有项目](https://zzp.moe/)

[![检查与更新](https://github.com/zzpice/routeros-adlist/actions/workflows/update.yml/badge.svg)](https://github.com/zzpice/routeros-adlist/actions/workflows/update.yml)

将 [anti-AD](https://github.com/privacy-protection-tools/anti-AD) 的纯域名列表自动转换为 MikroTik RouterOS `Adlist` 可直接读取的 hosts 格式。

## 快速使用

生成文件：[`adlist.txt`](./adlist.txt)

Raw 地址：

```text
https://raw.githubusercontent.com/zzpice/routeros-adlist/main/adlist.txt
```

RouterOS：

使用前请确认设备时间正确，并按当前 RouterOS 版本启用可信 CA 存储或导入所需 CA 证书。

```routeros
/ip/dns/adlist/add url="https://raw.githubusercontent.com/zzpice/routeros-adlist/main/adlist.txt" ssl-verify=yes
```

检查导入状态：

```routeros
/ip/dns/adlist/print
```

`name-count` 应显示已加载的域名数量。RouterOS 会使用 DNS 缓存保存 Adlist 条目，因此请确保 DNS cache 有足够空间。

> 若证书校验失败，请先检查设备时间和 CA 配置。`ssl-verify=no` 会取消对下载来源的身份验证，仅用于临时排障，排障后应恢复为 `yes`。

## 自动更新

GitHub Actions 每 6 小时检查一次 anti-AD：

1. 从 `https://anti-ad.net/domains.txt` 下载最新纯域名列表；
2. 校验响应内容和域名数量；
3. 去重、排序并转换为 `0.0.0.0 domain.example` 格式；
4. 只有内容发生变化时才更新 `adlist.txt`。

`adlist.txt` 是自动生成文件，不建议手动修改。RouterOS Adlist 本身也会周期性检查远程列表是否更新。

## 安全保护

转换脚本采用失败关闭策略：

- 下载失败会直接退出；
- 响应类型异常会拒绝处理；
- 有效域名少于 50,000 条会拒绝覆盖；
- 异常数据行过多会拒绝覆盖；
- 域名会统一规范化、去重并排序。

这样可以避免上游临时故障或错误页面被误发布为规则列表。

## 本地生成

只需要 Python 3.10+，无第三方依赖：

```bash
python convert.py
```

可选参数：

```bash
python convert.py --source https://anti-ad.net/domains.txt --output adlist.txt --min-domains 50000
```

## 数据来源

规则来自 [privacy-protection-tools/anti-AD](https://github.com/privacy-protection-tools/anti-AD)。本仓库只负责格式转换与自动发布，不修改 anti-AD 的规则内容。

## License

本仓库的转换脚本与自动化配置使用 [MIT License](./LICENSE)。上游规则的许可与归属以 anti-AD 项目为准。

## 项目体系

属于 [ZZP 工具与资源](https://zzp.moe/)。共同的[设计与仓库规范](https://github.com/zzpice/zzp-home/blob/main/docs/design.md)由入口仓库维护；使用步骤、生成产物和验证方式仍以本仓库为准。
