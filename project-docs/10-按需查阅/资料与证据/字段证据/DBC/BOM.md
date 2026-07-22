# DBC：BOM 字段证据

> 对应正式页面：[BOM](../../../../docs/04-DBC-主数据管理/01-物料管理/02-BOM.md)、[维护与查询参考](../../../../docs/04-DBC-主数据管理/01-物料管理/08-BOM-维护与查询参考.md)。
> 基线：测试环境 / `dev` 分支。本波字段技术名核对：2026-07-22（`base.sql` / `BomDO` / `BomBaseVO` / `BomImportExcelVo` / `BomExcelVO` / `bom.data.ts`）。

## 1. 对象与证据来源

| 项目 | 当前证据 |
| --- | --- |
| 业务对象 | BOM（物料清单关系，单表）。 |
| 数据对象 | `basic_bom`、`BomDO`。 |
| 页面/导入 | `bom.data.ts`；导入读 `BomImportExcelVo`，保存/导出另用 `BomExcelVO`。 |
| 结构结论 | **不是**表头/表体双表；历史文档若写 `headerId`/`detailId`/`parentItemCode`/`childItemCode` 均为伪技术名。 |

## 2. 关键字段映射（已核实）

| 业务中文名 | 前端/API 属性 | DO 属性 | 数据库列 | 类型/备注 | 结论 |
| --- | --- | --- | --- | --- | --- |
| BOM 编号 | `bomCode` | `bomCode` | `bom_code` | `varchar(255)` | 已确认；禁止写 `bomNumber`/`number`。 |
| 版本 | `version` | `version` | `version` | `varchar(64)` | 已确认。 |
| 父项物料号 | `productItemCode` | `productItemCode` | `product_item_code` | `varchar(64)` 非空 | 已确认；禁止写 `parentItemCode`/`parentCode`。 |
| 子项物料号 | `componentItemCode` | `componentItemCode` | `component_item_code` | `varchar(64)` 非空 | 已确认；禁止写 `childItemCode`/`materialCode`。 |
| 子项单位 | `componentUom` | `componentUom` | `component_uom` | `varchar(64)` 非空 | 已确认；禁止写 `uom`/`unit`（本对象单位专指子项）。 |
| 数量 | `componentQty` | `componentQty` | `component_qty` | `numeric(18,6)` 非空 | 已确认。 |
| 是否可用 | `available` | `available` | `available` | `boolean` 默认 true | 已确认。 |
| 生效/失效时间 | `activeTime` / `expireTime` | 同左 | `active_time` / `expire_time` | timestamp | 已确认。 |
| 发料方式 | `issueType` | `issueType` | `issue_type` | `varchar(64)` | 已确认；导入必填，导出 VO 上 `@ExcelIgnore`。 |
| 是否过期 | `isExpired` | `isExpired` | `is_expired` | `varchar(64)` | 已确认。 |
| 是否关键物料 | `isKeyMaterial` | `isKeyMaterial` | `is_key_material` | `varchar(8)` 默认 `FALSE` | 已确认；导入表头为「是否关键件」。 |
| 备注 | `remark` | `remark` | `remark` | text | 已确认。 |
| 工序 | —（`BomBaseVO` 无） | `processCode` | `process_code` | `varchar(32)` | DO/DDL 有；主 Web VO 未暴露，用途标为接口侧，正式页勿写为可维护字段。 |

## 3. 导入模型分层（GAP-024）

| 层级 | 对象 | 已确认差异 |
| --- | --- | --- |
| 模板读取 | `BomImportExcelVo` | 必填含版本、父/子项、数量、单位、生效、发料方式、是否过期、是否可用、是否关键件。 |
| 保存/导出 | `BomExcelVO` | 含创建者/创建时间/更新者/更新时间等审计列；`issueType`、`remark` 带 `@ExcelIgnore`。 |
| 结论 | — | 不得把导出审计列写成业务导入必填；导入与导出字段集合不可混用。 |

## 4. 页面层证据

| 事项 | 已确认内容 | 待核验项 |
| --- | --- | --- |
| 页面维护 | 前端要求 BOM 编号、版本、父项、子项、子项单位、数量、可用状态和生效时间。 | 后端当前有效创建/更新校验链及重复明细保护。 |
| 选择器 | 父项从成品/半成品范围选择；子项从物料范围选择；页面会带入子项单位。 | 选择器的完整物料类型和可用状态条件。 |
| 列表 | 前端展示父项、子项、数量、单位、有效期、发料方式、关键物料和可用状态。 | 默认排序、详情分组与反查入口。 |
| 下游引用 | 提供按父项、版本、可用状态查询结构的能力。 | 与 MES 计划/工单、WMS 备料/发料的实际自动挂接和版本选择规则。 |

## 5. 字段技术名校正提醒

禁止沿用历史反译/伪模型名：`parentItemCode`、`childItemCode`、`bomNumber`、`headerId`、`detailId`、`materialCode`、`bomHeader`/`bomDetail`。正式业务页以中文业务词为主；技术核对以本页为准。

## 待核验项

| 编号 | 问题 | 影响 |
| --- | --- | --- |
| DBC-BOM-001 | 专用服务中的部分创建、更新和导入校验为注释状态，当前生效规则未完全确定。 | 新增、编辑、导入和重复检查的培训口径。 |
| DBC-BOM-002 | 循环引用、同版本重复子项、版本切换与有效期冲突的拦截规则待测试。 | 工程变更和需求计算风险。 |
| DBC-BOM-003 | BOM 专属详情分组、反查入口和跨模块跳转未实现或未验证。 | 查询效率与培训可读性不足。 |
| DBC-BOM-004 | `process_code` 写入路径与前端是否只读展示待核验。 | 接口联调勿默认 Web 可维护。 |
