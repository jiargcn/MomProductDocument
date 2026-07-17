# 字段证据：API 参考总览

> 对应正式页：`docs/14-API参考/`。基线：测试环境 / `dev` / 2026-07-15。内部证据。

## 1. 文档发现

| 证据 | 结论 |
| --- | --- |
| 多模块 `application-*.yaml` 含 `springdoc` + `knife4j`，`swagger-ui.path: /swagger-ui.html` | 在线 API 文档以 Knife4j/Swagger 为准 |
| 各 `*-api` 模块依赖 `springdoc-openapi-starter-webmvc-api` | OpenAPI 模型由后端生成 |
| SCP 独立依赖树含 knife4j 4.x | SCP 可能独立文档入口 |

## 2. 已写入正式索引的路径抽样

| 路径 | 来源 |
| --- | --- |
| `GET /system/auth/get-permission-info` | System RBAC 证据 |
| `/mes/basic-processroute-info`、`/mes/work-order`、`/mes/wo-workstation-job`、`/mes/forward-trace`、`/mes/reverse-trace`、`/mes/line-client-info`、`/mes/production-order`、`/mes/production-order-main` | MES 各组字段证据 / 控制器取证 |
| WMS/QMS/EAM/SCP | 以模块业务文档与各自证据为准，本轮未逐条枚举 |

## 3. 明确不做

- 全站 Controller 路径自动导出进 MkDocs（易过期）。  
- 为 PS 编造 API。  
- 在正式页写 DO/DTO/源码路径。

## 4. 待环境固化

- 网关前缀、Token/租户 Header 名。  
- 是否存在聚合 Swagger 网关。  
- 各高频集成接口的请求/响应样例（脱敏）回填。

## 5. 相关 GAP

- `GAP-014` 前后端权限一致性  
- `GAP-071` MES NG→QMS  
- SCP↔DBC 同步、SCP 收货迁移等见 SCP 证据待确认
