# 报表统计

## 1. 概述

报表统计模块面向离散制造车间，提供五类核心业务记录的查询与统计功能，支撑生产追溯、绩效核算与合规审计。

| 报表类型 | 业务含义 | 典型使用场景 |
|---------|---------|-------------|
| 点检记录 | 设备点检 / 工序点检的执行记录 | 设备保养计划执行追踪 |
| 报工记录 | 工人提交的实际完工数量 | 计件工资核算 |
| 完工记录 | 工单完成的汇总数据 | 工单结案与成本归集 |
| 打印记录 | 工序流转卡 / 条码的打印历史 | 追溯查询、标签补打 |
| 上下工记录 | 工人进出产线的时间 | 考勤关联、班组工时统计 |

---

## 2. 领域模型

### 2.1 ER 实体关系

```mermaid
erDiagram
    PointCheckRecord {
        uuid id "(待截图确认)"
        string checkType "(待截图确认)"
        string bizObjId "(待截图确认)"
        string bizObjType "(待截图确认)"
        datetime checkTime "(待截图确认)"
        string inspectorId "(待截图确认)"
        string result "(待截图确认)"
        string remark "(待截图确认)"
    }

    ReportRecord {
        uuid id "(待截图确认)"
        string workOrderId "(待截图确认)"
        string processId "(待截图确认)"
        string workerId "(待截图确认)"
        datetime reportTime "(待截图确认)"
        decimal quantity "(待截图确认)"
        string unit "(待截图确认)"
        string status "(待截图确认)"
    }

    WorkOrderCompleteRecord {
        uuid id "(待截图确认)"
        string workOrderId "(待截图确认)"
        string productId "(待截图确认)"
        decimal plannedQty "(待截图确认)"
        decimal completedQty "(待截图确认)"
        datetime completeTime "(待截图确认)"
        string completeType "(待截图确认)"
        string operatorId "(待截图确认)"
    }

    PrintRecord {
        uuid id "(待截图确认)"
        string printType "(待截图确认)"
        string bizObjId "(待截图确认)"
        string templateId "(待截图确认)"
        string printerId "(待截图确认)"
        datetime printTime "(待截图确认)"
        string operatorId "(待截图确认)"
    }

    AttendanceRecord {
        uuid id "(待截图确认)"
        string workerId "(待截图确认)"
        string worklineId "(待截图确认)"
        datetime onDutyTime "(待截图确认)"
        datetime offDutyTime "(待截图确认)"
        string shiftId "(待截图确认)"
        string status "(待截图确认)"
    }

    WorkOrder ||--o{ ReportRecord : "报工"
    WorkOrder ||--o{ WorkOrderCompleteRecord : "完工"
    Worker ||--o{ ReportRecord : "提交"
    Worker ||--o{ AttendanceRecord : "上下工"
```

### 2.2 实体说明

| 实体 | 说明 |
|-----|------|
| PointCheckRecord | 点检记录，关联设备(Equipment)或工序(Process) |
| ReportRecord | 报工记录，关联工单(WorkOrder)和工序(Process) |
| WorkOrderCompleteRecord | 完工记录，关联工单(WorkOrder) |
| PrintRecord | 打印记录，关联流转卡、工单等业务对象 |
| AttendanceRecord | 上下工记录，关联工人(Worker)和产线(Workline) |

---

## 3. 核心流程

### 3.1 点检记录流程

```mermaid
flowchart TD
    A[计划点检任务生成] --> B[点检执行]
    B --> C{合格?}
    C -->|是| D[记录合格]
    C -->|否| E[记录异常并触发预警]
    D --> F[更新点检计划下次时间]
    E --> F
    F --> G[归档点检记录]
```

### 3.2 报工记录流程

```mermaid
flowchart TD
    A[工人到达工位] --> B[扫描工序流转卡]
    B --> C[工序完成后填报数量]
    C --> D{报工校验}
    D -->|通过| E[写入报工记录]
    D -->|异常| F[拒绝并提示]
    E --> G[更新工单进度]
```

### 3.3 完工记录流程

```mermaid
flowchart TD
    A[工单所有工序完工] --> B[触发完工校验]
    B --> C{满足完工条件?}
    C -->|否| D[提示未完工工序]
    C -->|是| E[生成完工记录]
    E --> F[更新工单状态为已完工]
    F --> G[触发入库/交接流程]
```

### 3.4 打印记录流程

```mermaid
flowchart TD
    A[业务操作触发打印请求] --> B[选择打印模板]
    B --> C[渲染打印内容]
    C --> D[提交至打印服务]
    D --> E[记录打印历史]
    E --> F[返回打印结果]
```

### 3.5 上下工记录流程

```mermaid
flowchart TD
    A[工人刷卡进线] --> B[记录进线时间]
    B --> C[登记当前产线/工位]
    C --> D[工人作业中]
    D --> E[工人刷卡出线]
    E --> F[记录出线时间并计算工时]
    F --> G[生成上下工记录]
```

---

## 4. 字段说明

### 4.1 点检记录 (PointCheckRecord)

| 字段名 | 中文名 | 数据类型 | 说明 |
|-------|--------|---------|------|
| id | 主键 | UUID | 点检记录唯一标识 |
| checkType | 点检类型 | String | 枚举：EquipmentCheck/ProcessCheck |
| bizObjId | 业务对象ID | String | 设备ID或工序ID |
| bizObjType | 业务对象类型 | String | Equipment/Process |
| checkTime | 点检时间 | DateTime | 执行时间 |
| inspectorId | 点检员ID | String | 执行人 |
| result | 点检结果 | String | OK/NG |
| remark | 备注 | String | 异常描述等 |

### 4.2 报工记录 (ReportRecord)

| 字段名 | 中文名 | 数据类型 | 说明 |
|-------|--------|---------|------|
| id | 主键 | UUID | 报工记录唯一标识 |
| workOrderId | 工单ID | String | 关联工单 |
| processId | 工序ID | String | 关联工序 |
| workerId | 报工员ID | String | 提交人 |
| reportTime | 报工时间 | DateTime | 提交时间 |
| quantity | 报工数量 | Decimal | 实际完工数量 |
| unit | 单位 | String | 件/个/千克等 |
| status | 状态 | String | Submitted/Approved/Rejected |

### 4.3 完工记录 (WorkOrderCompleteRecord)

| 字段名 | 中文名 | 数据类型 | 说明 |
|-------|--------|---------|------|
| id | 主键 | UUID | 完工记录唯一标识 |
| workOrderId | 工单ID | String | 关联工单 |
| productId | 产品ID | String | 产品物料 |
| plannedQty | 计划数量 | Decimal | 工单计划数量 |
| completedQty | 完工数量 | Decimal | 实际完工数量 |
| completeTime | 完工时间 | DateTime | 完工时刻 |
| completeType | 完工类型 | String | Normal/Early/Overdue |
| operatorId | 操作员ID | String | 执行人 |

### 4.4 打印记录 (PrintRecord)

| 字段名 | 中文名 | 数据类型 | 说明 |
|-------|--------|---------|------|
| id | 主键 | UUID | 打印记录唯一标识 |
| printType | 打印类型 | String | RouterCard/Barcode/Label |
| bizObjId | 业务对象ID | String | 流转卡ID/工单ID等 |
| templateId | 模板ID | String | 打印模板 |
| printerId | 打印机ID | String | 目标设备 |
| printTime | 打印时间 | DateTime | 打印时刻 |
| operatorId | 操作员ID | String | 打印人 |

### 4.5 上下工记录 (AttendanceRecord)

| 字段名 | 中文名 | 数据类型 | 说明 |
|-------|--------|---------|------|
| id | 主键 | UUID | 上下工记录唯一标识 |
| workerId | 工人ID | String | 关联工人 |
| worklineId | 产线ID | String | 所属产线 |
| onDutyTime | 进线时间 | DateTime | 刷卡进线时刻 |
| offDutyTime | 出线时间 | DateTime | 刷卡出线时刻 |
| shiftId | 班次ID | String | 所属班次 |
| status | 状态 | String | OnDuty/OffDuty/Abnormal |