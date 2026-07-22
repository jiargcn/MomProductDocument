# WMS ERP 成本中心 / 项目信息：行为证据

> 内部证据页；适用基线：测试环境 / `dev` 分支 / 2026-07-22 第二轮。不得从正式业务文档直接链接本页。

## 已定位证据

- 成本中心：`QadCostcentreController` / `QadCostcentreServiceImpl`（`/wms/qad-costcentre`）
- 项目：`QadProjectController` / `QadProjectService`（`/wms/qad-project`）

## 已确认事实

| 对象 | 当前事实 |
| --- | --- |
| 成本中心 | 提供 create/update/delete/page/import 等入口；创建校验 `costcentre_id`、`costcentre_code` 不与已有记录重复。 |
| 项目 | 提供 create/update/delete/page/import 等入口。 |
| 权限注解 | 两端 Controller 上多数 `@PreAuthorize` 为注释状态。 |
| 引用保护 | 删除未见科目账户等下游引用拦截。 |
| 同步权威源 | 未见本仓内 ERP 同步作业把“只读镜像”写死；正式页按「本地可维护 + 权威源待确认」表述。 |

## 第二轮结论摘要

正式页纠正了“可能仅查询”的过窄表述，改为：WMS 已具备本地维护能力，是否仍以 ERP 同步为唯一权威源归 `WMS-SA-002`。

## 问题登记

- `WMS-SA-002`：ERP 成本中心、项目来源与维护责任。
