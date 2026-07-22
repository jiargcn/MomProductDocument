# Repository Guidelines

## 项目结构与模块组织

本仓库是 MOM 制造运营管理系统产品文档站点，基于 MkDocs + Material 构建。所有手写文档放在 `docs/`，目录编号即导航顺序，必须与 `mkdocs.yml` 的 `nav` 保持一致；新增或重命名目录后必须同步更新导航。

完整模块清单如下：

- `docs/index.md`：站点首页。
- `docs/01-总体框架/`：系统概述、技术架构、技术栈。
- `docs/02-业务模型/`：领域模型、核心流程。
- `docs/03-基础设施/`：部署、安全、监控、报表。
- `docs/04-DBC-主数据管理/`：主数据、工厂建模、策略、物流、设备、工艺建模。
- `docs/05-WMS-库房管理/`：仓储、收货、上架、发料、库存、出库、盘点。
- `docs/06-MES-生产管理/`：基础建模、工艺、计划、追溯、报表。
- `docs/07-QMS-质量管理/`：检验配置、来料、生产、客户检验、质量评审。
- `docs/08-EAM-设备管理/`：设备、备件、工装、巡检保养。
- `docs/09-ANDON-异常管理/`：故障记录、问题响应。
- `docs/10-SCP-供应链平台/`：采购订单、预测、计划、发货、跟踪、结算。
- `docs/11-PS-排程管理/`：基础数据、维护订单、生产排程、结果查询。
- `docs/12-系统管理/`：租户认证、组织、权限、运维、消息、开发平台。
- `docs/13-数采管理/`：采集点、设备管理、NodeRed。
- `docs/14-API参考/`：接口参考。
- `docs/15-版本路线图/`：版本规划。

## 构建、测试与开发命令

```bash
mkdocs serve
```

启动本地热重载预览，默认访问 `http://127.0.0.1:8000/`。

```bash
mkdocs build
```

构建静态站点到 `site/`，用于发现导航、配置、Markdown 渲染等构建问题。

```bash
python scripts/link-interfaces.py
```

根据 `docs/.linkmap.json` 原地重写相关模块接口、业务分组和内联模块引用。新增页面、调整模块 CODE 或修改映射后必须运行，并用 `git diff` 检查脚本改动。

## 文档风格与命名约定

正文使用简体中文，保留英文原文中的 code、API、命令和 error message。业务模块遵循统一页面模型：`<module>/index.md` 写模块定位、业务分组表、核心流程、主数据维护顺序和相关接口；`<module>/<NN-子功能>/index.md` 写业务分组表和叶页概览；`<module>/<NN-子功能>/<叶页>.md` 写功能说明、**字段业务语义（按行为模式 P1–P14，非技术映射）**、相关模块接口表和业务规则。字段语义写法见 `docs/02-业务模型/04-页面数据字典规范.md` 与 `project-docs/00-需关注/实体说明页标准模板.md`。新增页面时先创建 `.md`，再挂入 `mkdocs.yml`，如涉及新 CODE 同步更新 `.linkmap.json`。

## 跨页面链接系统

`docs/.linkmap.json` 维护 `CODE_NAME → { name, path }` 映射。`scripts/link-interfaces.py` 会执行三类重写：Phase 1 将「相关模块接口」表中的中文名链接到目标页；Phase 2 将「业务分组」表中的分组名链接到对应 `index.md`；Phase 3 将「业务规则」段和字段业务语义表「影响业务/备注」列中的模块名改为内联链接。脚本会直接修改 Markdown 文件，运行后必须复查 diff。

## 测试与校验要求

本仓库没有独立自动化测试套件，提交前以 `mkdocs build` 作为必跑校验。涉及跨页面链接时，先运行 `python scripts/link-interfaces.py`，检查脚本修改的 Markdown 文件，再执行 `mkdocs build`。涉及样式、脚本、图表或导航层级变化时，应本地预览确认页面显示正常。

## 数据采集约定

采集 Vue / Element Plus 页面数据时，优先编写 Playwright 脚本拦截 API 响应，并使用精确 path pattern 避免匹配页面自身 URL。不要依赖 `playwright cli snapshot/eval/screenshot` 解析表格；必要时等待 `.el-table tbody tr` 等 DOM 就绪后再提取。登录态文件 `.playwright-cli/auth.json` 不得提交。

## 提交与 Pull Request 规范

历史提交采用 `docs:`、`feat:`、`fix:` 等前缀加中文摘要，例如 `docs: 补全模块页接口表`。每次提交聚焦一个文档或工具变更。PR 说明应包含变更模块、运行过的校验命令、是否更新 `mkdocs.yml` 或 `.linkmap.json`；涉及 `.linkmap.json`、导航结构或视觉变化时说明影响范围，必要时附截图。

## Agent 专用说明

除非用户明确要求其他格式，否则只生成 Markdown 文档。不要直接修改 `site/` 构建产物；应修改 `docs/`、`scripts/`、`mkdocs.yml` 或主题覆盖文件。
