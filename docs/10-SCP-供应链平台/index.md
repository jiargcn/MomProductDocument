# SCP 供应链平台

## 模块概述

SCP（供应链平台）连接企业与供应商，构建从采购需求发起、供应商协同、发货预通知、到货签收、IQC 检验到入库对账的全链路数字化协同能力，实现采购端到端可视、风险可控、结算有据。

## 业务分组

| 分组 | 说明 |
|------|------|
| 采购协同 | 采购申请 → 订单下达 → 供应商确认 → 发货变更全流程线上协同 |
| 供应商管理 | 供应商档案、绩效评估、准入评审、名录分类管理 |
| 来料跟踪 | ASN 预到货通知、到货签收、IQC 检验结果同步、投料追溯 |
| 对账结算 | 采购对账、发票管理、付款申请、结算记录 |
| 基础数据 | 供应商、物料分类、采购员等主数据维护 |

## 核心流程

### 采购协同全链路

```
采购申请 → 采购订单 → 供应商确认 → ASN预发货 → 到货签收 → IQC检验 → 采购入库
    ↓           ↓           ↓            ↓           ↓           ↓           ↓
  需求发起    订单下达    确认/驳回     发货通知    实物签收   质量判定    入库完成
                                                              ↓
                                                        对账结算
```

1. **采购申请**：需求部门提交采购申请，明确物料/数量/交期
2. **采购订单**：审批后转为正式采购订单，下达给供应商
3. **供应商确认**：供应商线上确认订单（接受/部分接受/驳回）
4. **ASN 预发货**：供应商发货前发送 Advanced Shipping Notice，含批次/数量/预计到货时间
5. **到货签收**：仓库实物签收，核对 ASN 与实物是否一致
6. **IQC 检验**：质量部门按批次检验，判定合格/不合格
7. **采购入库**：检验合格后完成入库，触发对账流程

### 对账结算流程

```
采购入库 → 生成对账单 → 供应商确认 → 发票校验 → 付款申请 → 财务审批 → 结算完成
    ↓           ↓            ↓           ↓           ↓           ↓           ↓
 入库数据   按入库单汇总   线上确认   发票与入库核销  付款发起   审批放行   付款完成
```

1. **生成对账单**：按供应商/时间段汇总已入库采购单
2. **供应商确认**：供应商线上核对账目，确认或发起争议
3. **发票管理**：供应商开具发票，与入库单核销
4. **付款申请**：按对账结果发起付款流程
5. **财务审批**：财务审核后执行付款
6. **结算完成**：付款完成，更新结算状态

## 字段说明

### 采购协同

| 字段名 | 说明 | 备注 |
|--------|------|------|
| purchaseApplyNo | 采购申请单号 | (待截图确认) |
| applyDept | 申请部门 | (待截图确认) |
| applyUser | 申请人 | (待截图确认) |
| applyDate | 申请日期 | (待截图确认) |
| materialCode | 物料编码 | (待截图确认) |
| materialName | 物料名称 | (待截图确认) |
| applyQty | 申请数量 | (待截图确认) |
| unitPrice | 单价 | (待截图确认) |
| deliveryDate | 交期 | (待截图确认) |
| purchaseOrderNo | 采购订单号 | (待截图确认) |
| supplierCode | 供应商编码 | (待截图确认) |
| supplierName | 供应商名称 | (待截图确认) |
| orderStatus | 订单状态 | (待截图确认) |
| confirmedQty | 确认数量 | (待截图确认) |
| asnNo | ASN预到货通知单号 | (待截图确认) |
| asnStatus | ASN状态 | (待截图确认) |
| expectedArrivalDate | 预计到货日期 | (待截图确认) |
| actualArrivalDate | 实际到货日期 | (待截图确认) |
| receivedQty | 到货签收数量 | (待截图确认) |
| signStatus | 签收状态 | (待截图确认) |

### 供应商管理

| 字段名 | 说明 | 备注 |
|--------|------|------|
| supplierCode | 供应商编码 | (待截图确认) |
| supplierName | 供应商名称 | (待截图确认) |
| supplierType | 供应商类型 | (待截图确认) |
| contactPerson | 联系人 | (待截图确认) |
| contactPhone | 联系电话 | (待截图确认) |
| address | 地址 | (待截图确认) |
| businessScope | 经营范围 | (待截图确认) |
| qualificationLevel | 资质等级 | (待截图确认) |
| performanceScore | 绩效评分 | (待截图确认) |
| onTimeDeliveryRate | 准时交货率 | (待截图确认) |
| qualityPassRate | 来料合格率 | (待截图确认) |
| creditLevel | 信用等级 | (待截图确认) |
| approvalStatus | 准入状态 | (待截图确认) |
| lastReviewDate | 最近评审日期 | (待截图确认) |

### 来料跟踪

| 字段名 | 说明 | 备注 |
|--------|------|------|
| asnNo | ASN单号 | (待截图确认) |
| poNo | 采购订单号 | (待截图确认) |
| supplierCode | 供应商编码 | (待截图确认) |
| expectedArrivalDate | 预计到货日期 | (待截图确认) |
| actualArrivalDate | 实际到货日期 | (待截图确认) |
| materialCode | 物料编码 | (待截图确认) |
| materialName | 物料名称 | (待截图确认) |
| asnQty | ASN通知数量 | (待截图确认) |
| receivedQty | 签收数量 | (待截图确认) |
| signedBy | 签收人 | (待截图确认) |
| signDate | 签收日期 | (待截图确认) |
| iqcStatus | IQC状态 | (待截图确认) |
| iqcResult | IQC检验结果 | (待截图确认) |
| qualifiedQty | 合格数量 | (待截图确认) |
| unqualifiedQty | 不合格数量 | (待截图确认) |
| defectType | 不良类型 | (待截图确认) |
| batchNo | 批次号 | (待截图确认) |
| tracingInfo | 投料追溯信息 | (待截图确认) |

### 对账结算

| 字段名 | 说明 | 备注 |
|--------|------|------|
| statementNo | 对账单号 | (待截图确认) |
| supplierCode | 供应商编码 | (待截图确认) |
| supplierName | 供应商名称 | (待截图确认) |
| statementPeriod | 对账周期 | (待截图确认) |
| warehouseReceiptNos | 入库单号列表 | (待截图确认) |
| totalAmount | 对账总金额 | (待截图确认) |
| confirmedAmount | 供应商确认金额 | (待截图确认) |
| disputeAmount | 争议金额 | (待截图确认) |
| statementStatus | 对账状态 | (待截图确认) |
| invoiceNo | 发票号 | (待截图确认) |
| invoiceAmount | 发票金额 | (待截图确认) |
| invoiceStatus | 发票状态 | (待截图确认) |
| paymentApplicationNo | 付款申请单号 | (待截图确认) |
| paymentAmount | 付款金额 | (待截图确认) |
| paymentStatus | 付款状态 | (待截图确认) |
| paymentMethod | 付款方式 | (待截图确认) |
| settlementNo | 结算单号 | (待截图确认) |
| settlementDate | 结算日期 | (待截图确认) |

### 基础数据

| 字段名 | 说明 | 备注 |
|--------|------|------|
| supplierCode | 供应商编码 | (待截图确认) |
| supplierName | 供应商名称 | (待截图确认) |
| materialCategoryCode | 物料分类编码 | (待截图确认) |
| materialCategoryName | 物料分类名称 | (待截图确认) |
| purchaserCode | 采购员编码 | (待截图确认) |
| purchaserName | 采购员姓名 | (待截图确认) |
| purchaserDept | 采购部门 | (待截图确认) |
| paymentTermCode | 付款条款编码 | (待截图确认) |
| paymentTermName | 付款条款名称 | (待截图确认) |
| minOrderQty | 最小订购量 | (待截图确认) |
| leadTime | 交货周期 | (待截图确认) |

## 关联关系

### SCP → WMS（库房管理）

| 方向 | 接口内容 | 说明 |
|------|----------|------|
| SCP → WMS | 采购订单下发 | SCP 采购订单同步至 WMS，生成待入库采购单 |
| WMS → SCP | 到货签收结果 | WMS 签收数据回传 SCP，更新 ASN 实到数量 |
| WMS → SCP | 入库完成通知 | WMS 入库完成后通知 SCP，触发对账流程 |

### SCP → QMS（质量管理）

| 方向 | 接口内容 | 说明 |
|------|----------|------|
| SCP → QMS | IQC 检验委托 | SCP 将到货检验需求推送 QMS，生成 IQC 工单 |
| QMS → SCP | 检验结果回传 | QMS 检验完成后回传结果（合格/不合格/让步接收） |

### SCP → ERP（财务）

| 方向 | 接口内容 | 说明 |
|------|----------|------|
| SCP → ERP | 对账数据同步 | SCP 对账单据同步至 ERP，生成应付账款 |
| SCP → ERP | 发票核销 | SCP 发票信息同步 ERP，完成三单匹配（订单/入库单/发票） |
| ERP → SCP | 付款结果回传 | ERP 付款完成后回传付款结果，更新 SCP 结算状态 |