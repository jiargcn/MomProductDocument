# 采购收货

## 概述

采购收货是WMS库房管理中连接供应商送货与内部库存的核心环节，负责将采购订单转化为实际入库库存，支持扫码验收、数量差异处理、拒收退货等业务场景。

## 当前基线取证（代码已证实）

> 适用基线：测试环境对应的 `dev` 分支，2026-07-15。以下是源码已证实的服务调用关系，尚未替代测试环境的端到端回归结果。

| 环节 | 当前实现证据 | 可确认的结论 |
| --- | --- | --- |
| 采购收货申请 | 请求主表以单据号、业务类型、状态和明细为公共结构；采购收货申请额外要求供应商代码。 | 申请用于汇集供应商、到货和物料明细等业务意图，是后续任务的来源。 |
| 采购收货任务 | 创建任务明细后，服务按任务号、业务类型、库位、货主、数量、库存状态、批次写入预计入。 | **任务创建会创建预计入库记录**；预计入与任务号关联，不应只作为独立查询数据理解。 |
| 采购收货记录 | 收货记录服务构建库存事务后调用库存事务服务。 | **记录执行会创建库存事务**；实际库存变化应从记录与事务之间追溯。 |
| 库存事务与余额 | 库存事务服务先合并余额变更请求，调用余额批量更新，再写入库存事务。 | **库存事务服务负责更新库存余额**；余额不是由采购收货页面直接维护。 |
| 外部接口 | 任务创建逻辑含 `ASN_DirectReceipt` 来源的接口信息分支。 | 已发现第三方接口挂接入口；具体接口对象、触发条件与结果回写待专项核对。 |

当前待测试验证项包括：实际状态流转、审批/自动通过策略、PDA 与线边端的具体入口，以及接口调用是否在测试环境成功闭环。相关问题已登记在[产品差距总账](../../15-版本路线图/产品差距总账.md)。

## 当前页面事实卡（代码已证实）

### 1. 采购收货申请

| 维度 | 当前实现 |
| --- | --- |
| 列表字段顺序 | 单据号、状态、供应商代码、供应商名称、发货单号；采购订单号、要求到货日期、订单类型等在页面配置中可查询或详情展示，但默认不在主列表展示。 |
| 查询字段 | 单据号、采购订单号、供应商代码、发货单号、订单类型。 |
| 新增来源 | 可从采购订单选择器带入。选择器限定采购订单为已发布状态（`status=2`）且 ERP 订单类型为 `Z001`。 |
| 已证实必填项 | 后端请求校验要求 `supplierCode` 非空；数据库同时要求单据号、业务类型、供应商代码非空。单据号的生成方式待测试环境确认。 |
| 页面限制 | 业务类型固定为 `PurchaseReceipt`；采购订单带入后的供应商代码、订单类型、ERP 订单类型、汇率和货币码在当前页面配置中禁用编辑。 |
| 可用动作 | 新增、修改、删除、关闭、重新添加、提交、同意、驳回、处理、标签生成、导入导出。动作存在不等于所有状态均可执行，状态前置条件待测试验证。 |
| 导入实现 | 已有固定转换率与非固定转换率两类模板；导入支持更新、追加、覆盖三种模式，错误数据会生成错误文件。模板字段与逐字段校验待在导入专项中补齐。 |

### 2. 采购收货任务

| 维度 | 当前实现 |
| --- | --- |
| 列表字段顺序 | 单据号、申请单号、状态、采购订单号、供应商代码、供应商名称、发货单号。 |
| 查询字段 | 单据号、状态、供应商代码、发货单号。 |
| 上游关联 | 主表保留 `requestNumber`，用于关联采购收货申请；任务创建时会创建以任务号为关联键的预计入库数据。 |
| 可配置执行限制 | 任务结构包含允许修改库位、数量、批次、包装号，允许多收、少收、重复扫码、扫描目标库位等开关。各开关的默认值、界面暴露方式和生效条件待测试验证。 |
| 可用动作 | 新增、修改、删除、关闭、接单、放弃、拒收、撤销、任务配置更新、导入导出。 |

### 3. 采购收货记录

| 维度 | 当前实现 |
| --- | --- |
| 列表字段顺序 | 单据号、状态、申请单号、任务单号、采购订单号、供应商代码、供应商名称、发货单号。 |
| 查询字段 | 单据号、采购订单号、供应商代码、发货单号。 |
| 上游关联 | 主表同时保留 `requestNumber` 与 `jobNumber`，用于追溯申请和任务。 |
| 下游影响 | 记录服务创建库存事务；库存事务服务再更新库存余额。记录页还提供创建上架申请、检验申请、采购退货记录和撤销收货记录的入口。 |
| 状态与接口线索 | 记录表包含状态、ERP 凭证号、ERP 推送标识、接口类型、入/出库事务类型等字段；这些字段的业务口径和接口回写规则待专项确认。 |

### 4. 字段类型与长度（主表关键字段）

| 对象 | 字段 | 数据库类型/长度 | 非空约束 | 说明 |
| --- | --- | --- | --- | --- |
| 申请 | `number` | `varchar(64)` | 是 | 单据号。 |
| 申请 | `business_type` | `varchar(64)` | 是 | 当前页面固定为 `PurchaseReceipt`。 |
| 申请 | `supplier_code` | `varchar(64)` | 是 | 当前后端也有非空校验。 |
| 申请 | `po_number`、`asn_number`、`pp_number` | `varchar(64)` | 否 | 分别为采购订单、发货单、要货计划关联信息。 |
| 申请 | `exchange_rate` | `numeric(24,6)` | 否 | 页面中只读。 |
| 任务 | `number`、`request_number` | `varchar(64)` | 单据号否、申请单号否 | 任务单号与申请单号的关联字段。 |
| 任务 | `supplier_code` | `varchar(64)` | 是 | 供应商代码。 |
| 记录 | `number` | `varchar(64)` | 是 | 收货记录单号。 |
| 记录 | `request_number`、`job_number` | `varchar(64)` | 否 | 上游申请、任务追溯键。 |
| 记录 | `status` | `varchar(20)` | 是 | 默认值为 `1`；实际字典含义待测试验证。 |
| 记录 | `erp_voucher_number` | `varchar(64)` | 否 | ERP 凭证号。 |

## 领域模型

```mermaid
erDiagram
    PURCHASE_RECEIPT_REQUEST {
        string request_id PK "采购收货申请单ID"
        string po_id FK "采购订单ID"
        string supplier_id FK "供应商ID"
        string warehouse_id FK "仓库ID"
        date expected_date "预计到货日期"
        string status "申请单状态"
        string creator "创建人"
        datetime create_time "创建时间"
    }

    PURCHASE_RECEIPT_TASK {
        string task_id PK "采购收货任务ID"
        string request_id FK "申请单ID"
        string material_id FK "物料ID"
        decimal expected_qty "期望数量"
        decimal received_qty "实收数量"
        decimal diff_qty "差异数量"
        string scan_status "扫码状态"
        string task_status "任务状态"
        string receiver "接收人"
        datetime receive_time "接收时间"
    }

    PURCHASE_RECEIPT_RECORD {
        string record_id PK "采购收货记录ID"
        string task_id FK "任务ID"
        string receipt_no "收货单号"
        string po_no "采购订单号"
        string supplier_id FK "供应商ID"
        string warehouse_id FK "仓库ID"
        string material_id FK "物料ID"
        decimal quantity "收货数量"
        decimal diff_qty "差异数量"
        string status "单据状态"
        datetime receipt_time "收货时间"
        string receipt_by "收货人"
    }

    PURCHASE_REJECTION_RECORD {
        string rejection_id PK "采购拒收记录ID"
        string task_id FK "任务ID"
        string rejection_no "拒收单号"
        string reason "拒收原因"
        string material_id FK "物料ID"
        decimal quantity "拒收数量"
        string status "单据状态"
        datetime rejection_time "拒收时间"
        string rejection_by "拒收人"
    }

    PURCHASE_ORDER {
        string po_id PK "采购订单ID"
        string po_no "采购订单号"
        string supplier_id FK "供应商ID"
        date order_date "下单日期"
        string status "订单状态"
    }

    MATERIAL {
        string material_id PK "物料ID"
        string material_code "物料编码"
        string material_name "物料名称"
        string unit "单位"
    }

    SUPPLIER {
        string supplier_id PK "供应商ID"
        string supplier_code "供应商编码"
        string supplier_name "供应商名称"
    }

    WAREHOUSE {
        string warehouse_id PK "仓库ID"
        string warehouse_code "仓库编码"
        string warehouse_name "仓库名称"
    }

    INVENTORY {
        string inventory_id PK "库存ID"
        string material_id FK "物料ID"
        string warehouse_id FK "仓库ID"
        decimal quantity "库存数量"
        string lot_no "批次号"
    }

    PURCHASE_RECEIPT_REQUEST ||--o{ PURCHASE_RECEIPT_TASK : "生成"
    PURCHASE_RECEIPT_TASK ||--o| PURCHASE_RECEIPT_RECORD : "确认入库"
    PURCHASE_RECEIPT_TASK ||--o| PURCHASE_REJECTION_RECORD : "拒收"
    PURCHASE_ORDER ||--o{ PURCHASE_RECEIPT_REQUEST : "触发"
    PURCHASE_RECEIPT_RECORD }o--|| INVENTORY : "更新"
    PURCHASE_RECEIPT_REQUEST }o--|| SUPPLIER : "关联"
    PURCHASE_RECEIPT_REQUEST }o--|| WAREHOUSE : "关联"
    PURCHASE_RECEIPT_TASK }o--|| MATERIAL : "关联"
```

## 核心流程

```mermaid
flowchart TD
    A["供应商送货"] --> B["创建采购收货申请单"]
    B --> C{"审批通过?"}
    C -->|否| D["调整/取消申请"]
    C -->|是| E["生成采购收货任务"]
    E --> F["仓管员接单"]
    F --> G["扫码验收/数量录入"]
    G --> H{"数量匹配?"}
    H -->|是| I["确认收货"]
    H -->|否| J["填写差异数量"]
    J --> K{"差异可接受?"}
    K -->|是| I
    K -->|否| L["生成采购拒收记录"]
    L --> M["退货处理"]
    I --> N["生成采购收货记录"]
    N --> O["过账到库存"]
    O --> P["完成"]
    M --> P

    subgraph 申请阶段
        B
        C
        D
    end

    subgraph 执行阶段
        E
        F
        G
        H
        J
        K
        L
    end

    subgraph 记录阶段
        I
        N
        O
        P
    end
```

## 功能说明（历史草稿，待逐项核验）

> 下列内容保留为业务说明草稿，不作为当前字段、状态、扫码、离线或库存规则的唯一依据。当前实现以“当前基线取证”和“当前页面事实卡”为准；未证实内容将按试点任务逐项修订或移入产品差距总账。

### 1. 采购收货申请

管理采购收货申请单的创建、编辑、审批流程。

**功能入口**: 采购收货管理 → 采购收货申请

| 字段名 | 中文名 | 类型 | 约束 | 影响业务 | 备注 |
|--------|--------|------|------|----------|------|
| request_no | 申请单号 | VARCHAR(50) | 系统自动生成 | 用于唯一标识本次收货申请 | 格式: PR-YYYYMMDD-XXXX |
| po_no | 采购订单号 | VARCHAR(50) | 必填, FK | 关联[采购订单](../../10-SCP-供应链平台/02-采购订单/index.md)，获取供应商/物料信息 | 来源采购模块 |
| supplier_code | 供应商代码 | VARCHAR(50) | 必填 | 确定送货方，影响后续[供应商对账](../../10-SCP-供应链平台/07-发票结算/index.md) | 来自供应商主数据 |
| order_type | 订单类型 | ENUM | 字典项 | 区分离散/标准采购等 | 离散/标准采购 |
| material_code | 物料编码 | VARCHAR(50) | 必填 | 关联物料主数据 | |
| material_name | 物料名称 | VARCHAR(200) | 显示 | 展示物料信息 | |
| unit | 计量单位 | VARCHAR(20) | 显示 | 物料计量单位 | |
| order_qty | 订单数量 | DECIMAL(12,3) | 必填 | [采购订单](../../10-SCP-供应链平台/02-采购订单/index.md)中的订购数量 | |
| expected_date | 预计到货日期 | DATE | 必填 | 用于提前备货和任务调度 | |
| status | 申请单状态 | ENUM | 系统定义 | 控制流程走向: 待审批/已审批/已取消 | |
| tax_rate | 税率 | DECIMAL(5,2) | 显示 | 税率百分比 | |
| creator | 创建人 | VARCHAR(50) | 系统自动 | 记录操作人员 | |
| create_time | 创建时间 | DATETIME | 系统自动 | 记录创建时间戳 | |

### 2. 采购收货任务

执行层面的扫码验收和数量确认页面。

**功能入口**: 采购收货管理 → 采购收货任务

| 字段名 | 中文名 | 类型 | 约束 | 影响业务 | 备注 |
|--------|--------|------|------|----------|------|
| task_id | 任务ID | VARCHAR(50) | PK | 唯一标识一个收货任务 | |
| request_no | 申请单号 | VARCHAR(50) | FK | 关联申请单信息 | |
| po_no | 采购订单号 | VARCHAR(50) | 显示 | 关联[采购订单](../../10-SCP-供应链平台/02-采购订单/index.md) | |
| supplier_code | 供应商代码 | VARCHAR(50) | 显示 | 展示供应商信息 | |
| material_code | 物料编码 | VARCHAR(50) | 扫码获取 | 扫码枪扫描获取 | |
| material_name | 物料名称 | VARCHAR(200) | 显示 | 展示物料信息 | |
| unit | 计量单位 | VARCHAR(20) | 显示 | 物料计量单位 | |
| order_qty | 订单数量 | DECIMAL(12,3) | 来自订单 | [采购订单](../../10-SCP-供应链平台/02-采购订单/index.md)中的订购数量 | |
| expected_qty | 期望数量 | DECIMAL(12,3) | 计算 | order_qty - 已收货数量 | |
| received_qty | 实收数量 | DECIMAL(12,3) | 必填 | 仓管员实际清点数量 | |
| diff_qty | 差异数量 | DECIMAL(12,3) | 计算字段 | received_qty - expected_qty | 正值多收，负值少收 |
| scan_status | 扫码状态 | ENUM | 系统定义 | 已扫码/未扫码 | |
| task_status | 任务状态 | ENUM | 系统定义 | 待执行/执行中/已完成 | |
| receiver | 接收人 | VARCHAR(50) | 系统自动 | 记录执行任务的仓管员 | |
| receive_time | 接收时间 | DATETIME | 系统自动 | 记录任务完成时间 | |

### 3. 采购收货记录

已完成收货单据的列表查询和详情查看。

**功能入口**: 采购收货管理 → 采购收货记录

| 字段名 | 中文名 | 类型 | 约束 | 影响业务 | 备注 |
|--------|--------|------|------|----------|------|
| receipt_no | 收货单号 | VARCHAR(50) | PK | 唯一标识本次收货记录 | 格式: PR-YYYYMMDD-XXXX |
| po_no | 采购订单号 | VARCHAR(50) | FK | 关联[采购订单](../../10-SCP-供应链平台/02-采购订单/index.md) | 来自采购模块 |
| supplier_code | 供应商代码 | VARCHAR(50) | 必填 | 确定送货方 | 影响后续供应商对账 |
| supplier_name | 供应商名称 | VARCHAR(200) | 显示 | 展示供应商信息 | (待截图确认) |
| order_type | 订单类型 | ENUM | 字典项 | 区分离散/标准等订单 | 离散/标准等 |
| status | 单据状态 | ENUM | 系统定义 | 控制流程走向 | 待处理/进行中/已完成/已冲销 |
| receipt_date | 收货日期 | DATE | 必填 | 记录实际收货日期 | |
| warehouse_code | 仓库编码 | VARCHAR(50) | FK | 确定收货仓库 | 影响库存归属 |
| material_code | 物料编码 | VARCHAR(50) | 必填 | 关联物料主数据 | |
| material_name | 物料名称 | VARCHAR(200) | 显示 | 展示物料信息 | |
| unit | 计量单位 | VARCHAR(20) | 显示 | 物料计量单位 | |
| quantity | 收货数量 | DECIMAL(12,3) | 必填 | 实际入库数量 | |
| diff_qty | 差异数量 | DECIMAL(12,3) | 显示 | 与期望数量的差异 | 正值多收，负值少收 |
| tax_rate | 税率 | DECIMAL(5,2) | 显示 | 税率百分比 | |
| receipt_time | 收货时间 | DATETIME | 系统自动 | 记录过账时间 | |
| receipt_by | 收货人 | VARCHAR(50) | 系统自动 | 记录执行仓管员 | |

### 4. 采购拒收记录

拒收单据的记录和查询。

**功能入口**: 采购收货管理 → 采购拒收记录

| 字段名 | 中文名 | 类型 | 约束 | 影响业务 | 备注 |
|--------|--------|------|------|----------|------|
| rejection_no | 拒收单号 | string | PK | 唯一标识本次拒收记录 | (待截图确认) |
| request_no | 申请单号 | string | FK | 关联收货申请 | (待截图确认) |
| task_id | 任务ID | string | FK | 关联收货任务 | (待截图确认) |
| material_id | 物料ID | string | FK | 拒收的物料 | (待截图确认) |
| material_code | 物料编码 | string | 显示 | 物料唯一标识 | (待截图确认) |
| material_name | 物料名称 | string | 显示 | 物料描述 | (待截图确认) |
| quantity | 拒收数量 | decimal | 必填 | 拒收的物料数量 | (待截图确认) |
| rejection_reason | 拒收原因 | string | 必填 | 质量问题/数量异常/包装破损等 | (待截图确认) |
| supplier_id | 供应商 | string | FK | 记录拒收供应商 | (待截图确认) |
| supplier_name | 供应商名称 | string | 显示 | 展示供应商信息 | (待截图确认) |
| rejection_date | 拒收日期 | date | 必填 | 记录拒收发生日期 | (待截图确认) |
| rejection_time | 拒收时间 | datetime | 系统自动 | 记录拒收时间戳 | (待截图确认) |
| rejection_by | 拒收人 | string | 系统自动 | 记录执行仓管员 | (待截图确认) |
| status | 单据状态 | enum | 系统定义 | 待处理/已退货 | (待截图确认) |

## 业务规则（待核验）

### 数量差异处理

- **允许差异范围**: 可配置（如: ±5% 或 固定值），超出范围的差异需要上级审批
- **差异记账**: 差异数量单独记录，支持正向（多收）和负向（少收）两种场景
- **差异追溯**: 所有差异需要填写原因，便于供应商绩效考核

### 扫码验收规则

- 扫码枪扫描物料条码，系统自动匹配物料信息和期望数量
- 扫码匹配成功才允许确认收货
- 支持离线扫码，扫码记录暂存本地，网络恢复后自动同步

### 库存过账时机

- 收货任务确认后，实时生成收货记录
- 收货记录审核通过后，立即更新库存台账
- 库存过账支持事务回滚，异常时自动冲正

### 拒收处理流程

- 拒收记录生成后，触发退货申请流程
- 拒收物料不参与正常库存计算
- 拒收记录与供应商绩效考核挂钩

## 搜索条件说明（待核验）

### 采购收货记录搜索

| 搜索字段 | 中文名 | 搜索类型 | 说明 |
|----------|--------|----------|------|
| supplier | 供应商 | 下拉选择 | 支持模糊搜索供应商名称 |
| warehouse | 仓库 | 下拉选择 | 支持多仓库筛选 |
| receipt_no | 收货单号 | 文本输入 | 支持精确和模糊搜索 |
| status | 单据状态 | 下拉选择 | 待处理/进行中/已完成/已冲销 |
| date_range | 收货日期范围 | 日期区间 | 支持自定义起止日期 |

### 采购拒收记录搜索

| 搜索字段 | 中文名 | 搜索类型 | 说明 |
|----------|--------|----------|------|
| supplier | 供应商 | 下拉选择 | 支持模糊搜索 |
| rejection_no | 拒收单号 | 文本输入 | 支持精确和模糊搜索 |
| material | 物料 | 下拉选择 | 支持按物料筛选 |
| date_range | 拒收日期范围 | 日期区间 | 支持自定义起止日期 |

## 菜单树结构（待菜单与终端映射核验）

```
采购收货管理
  ├─ 采购收货申请（新建/审批）
  ├─ 采购收货任务（执行页面，含扫码/数量录入）
  ├─ 采购收货记录（已完成单据列表）
  └─ 采购拒收记录（拒收单据列表）
```

## 相关模块接口（待接口专项核验）

### 依赖模块

| 模块 | 接口方向 | 说明 |
|------|----------|------|
| PURCHASE_ORDER | 采购订单 | 获取采购订单信息，触发收货申请 |
| DBC_MATERIAL | [物料主数据](../../04-DBC-主数据管理/01-物料管理/01-物料基本信息.md) | 获取物料信息、条码规则 |
| DBC_SUPPLIER | [供应商主数据](../../04-DBC-主数据管理/02-供应商管理/01-供应商.md) | 获取供应商信息 |
| WMS_WAREHOUSE | [仓库主数据](../01-基础数据/index.md) | 获取仓库信息 |
| QMS_INSPECTION | [质量检验](../../07-QMS-质量管理/index.md) | 支持到货质检联动 |

### 被依赖模块

| 模块 | 接口方向 | 说明 |
|------|----------|------|
| WMS_INVENTORY | [库存管理](../09-库存管理/index.md) | 收货过账后更新库存台账 |
| SCP_PURCHASE | [采购供应链](../../10-SCP-供应链平台/index.md) | 收货数据同步至采购对账 |
| FM_PAYABLE | 应付管理 | 收货记录作为付款依据 |

## 版本历史

| 版本 | 日期 | 修改说明 |
|------|------|----------|
| 1.1 | 2026-07-15 | 新增基线取证和申请、任务、记录页面事实卡；原有未证实内容调整为待核验草稿。 |
| 1.0 | 2026-05-19 | 初稿发布 |
