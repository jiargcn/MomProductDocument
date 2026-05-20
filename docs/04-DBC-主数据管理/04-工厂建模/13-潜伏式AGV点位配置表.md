# 潜伏式AGV点位配置表

## 概述

潜伏式AGV点位配置定义AGV专用车位的物理位置和属性，用于AGV调度系统。

## 字段说明

| 字段名 | 中文名 | 类型 | 约束 | 影响业务 | 备注 |
|--------|--------|------|------|----------|------|
| agvPointCode | AGV点位代码 | VARCHAR(50) | 必填 | AGV调度（车位标识） | AGV车位的唯一标识 |
| agvPointName | AGV点位名称 | VARCHAR(200) | 必填 | AGV显示 | 车位显示名称 |
| pointType | 点位类型 | VARCHAR(50) | 非必填 | AGV任务类型 | 类型（如：停靠站、充电站、装卸站） |
| locationCode | 库位代码 | VARCHAR(50) | 非必填 | 关联库位 | 对应的库位 |
| xCoord | X坐标 | DECIMAL(18,4) | 非必填 | AGV导航 | 地理X坐标 |
| yCoord | Y坐标 | DECIMAL(18,4) | 非必填 | AGV导航 | 地理Y坐标 |
| orientation | 朝向角度 | DECIMAL(5,2) | 非必填 | AGV停靠（停车方向） | 停车朝向角度 |
| isAvailable | 是否可用 | BOOLEAN | 默认是 | AGV调度 | 是否可用 |
| priority | 优先级 | INT | 非必填 | AGV调度优先级 | 优先级 |
| effectiveDate | 生效时间 | DATE | 非必填 | 点位启用时间 | 生效时间 |
| invalidDate | 失效时间 | DATE | 非必填 | 点位停用时间 | 失效时间 |
| remark | 备注 | VARCHAR(500) | 非必填 | | 补充说明 |

## 关联关系

```
库位（1）←→（N）AGV点位配置
AGV点位 → AGV任务（目的地）
```

## 字段约束说明

| 约束类型 | 说明 |
|----------|------|
| 唯一约束 | agvPointCode 唯一 |