# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

MOM 制造运营管理系统产品文档，面向离散制造业的全流程数字化管理平台文档。涵盖 DBC（主数据）、WMS（库房）、MES（生产）、QMS（质量）、EAM（设备）、ANDON（异常）、SCP（供应链）、PS（排程）等业务模块。

## 常用命令

```bash
# 文档预览（热重载）
mkdocs serve

# 构建静态站点
mkdocs build

# 部署到 GitHub Pages
mkdocs gh-deploy
```

## 目录结构

```
docs/                    # 文档源文件（Markdown）
  01-总体框架/           # 系统概述、技术架构、技术栈
  02-业务模型/           # 领域模型、核心流程
  03-基础设施/           # 部署架构、安全体系、监控运维
  04-DBC-主数据管理/
  05-WMS-库房管理/
  06-MES-生产管理/
  07-QMS-质量管理/
  08-EAM-设备管理/
  09-ANDON-异常管理/
  10-SCP-供应链平台/
  11-PS-排程管理/
  12-API参考/
  13-版本路线图/
mkdocs.yml              # MkDocs 站点配置
```

## 技术栈

- 文档框架：MkDocs + Material for MkDocs 主题
- 文档语言：中文（zh）
- Markdown 扩展：admonition、代码高亮、标签页、任务列表等

## 架构说明

本文档采用"系统上下文→技术架构→业务模块"的渐进式结构。业务模块文档按**领域模型→核心流程→接口规范**三段式展开。
