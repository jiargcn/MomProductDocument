# MOM 制造运营管理系统 · 产品文档

面向离散制造业的 MOM（Manufacturing Operations Management）产品文档仓库。正式文档以 **测试 / 实施 / 运维** 并列读者的「业务行为说明书」书写：功能范围清楚、逻辑可讲、配置可落地、验证可开单。

**在线站点：**

- GitHub Pages：[https://jiargcn.github.io/MomProductDocument/](https://jiargcn.github.io/MomProductDocument/)
- Cloudflare Pages：[https://mom-product-document.pages.dev/](https://mom-product-document.pages.dev/)

## 仓库内容

| 目录 / 文件 | 说明 |
| --- | --- |
| `docs/` | 正式产品文档（MkDocs 源文） |
| `mkdocs.yml` | 站点配置与侧栏导航（以 `nav` 为准） |
| `overrides/` | Material 主题覆盖 |
| `scripts/` | 链接重写、表格修复、离线打包等工具 |
| `project-docs/` | 内部建设工作台（交接、模板、证据），**不发布**到产品站点 |
| `AGENTS.md` | 贡献与 Agent 协作约定 |

侧栏分区：认识系统 · 业务应用（DBC / WMS / MES / QMS / EAM / ANDON / SCP 等）· 平台与集成 · 版本路线图。业务细节从模块首页 → 分组 → **主文档** 进入；`*-维护与查询参考.md` 默认不进侧栏，由主文档内链打开。

## 本地预览

```bash
pip install -r requirements.txt
mkdocs serve
```

浏览器访问 `http://127.0.0.1:8000/`。

```bash
mkdocs build
```

校验导航与 Markdown 渲染，产物输出到 `site/`（已 gitignore，请勿手改）。

## 发布到 Cloudflare Pages

正式地址：[https://mom-product-document.pages.dev/](https://mom-product-document.pages.dev/)（与 GitHub Pages 并存）。

持续部署工作流：[`.github/workflows/deploy-cloudflare-pages.yml`](.github/workflows/deploy-cloudflare-pages.yml)（`main` 推送或手动 Run workflow）。需在仓库 Secrets 中配置：

| Secret | 说明 |
| --- | --- |
| `CLOUDFLARE_ACCOUNT_ID` | 已配置时可忽略 |
| `CLOUDFLARE_API_TOKEN` | [创建 Token](https://dash.cloudflare.com/profile/api-tokens)，模板选 **Edit Cloudflare Workers**（需含 Pages 编辑权限） |

本地也可：`mkdocs build` 后执行  
`npx wrangler pages deploy site --project-name=mom-product-document --branch=main`（需先 `npx wrangler login`）。

## 常用脚本

```bash
# 按 .linkmap.json 重写跨页模块链接（改完后务必 diff 复查）
python scripts/link-interfaces.py

# 扫描 / 修复 Markdown 表头与分隔行列数不一致
python scripts/fix-md-tables.py
python scripts/fix-md-tables.py --fix

# 离线打包：默认同时生成 PDF + HTML + MD 到 dist/
python scripts/pack-offline-site.py
```

离线产物示例：`dist/MOM产品文档-YYYYMMDD.pdf`（含多级书签）、`.html`（自包含）、`.md`（合并正文）。也可追加参数只打子集：`pdf` / `html` / `md`。PDF 构建需要本机 Chrome/Edge，以及全局安装的 `mmdc`（`@mermaid-js/mermaid-cli`）用于渲染 Mermaid。

## 阅读入口建议

1. 产品全景：站点「认识系统」→ [系统概述](docs/01-总体框架/05-系统概述.md) → [系统边界与产品全景](docs/01-总体框架/01-系统边界与产品全景.md)
2. 业务落地：侧栏「业务应用」对应模块首页 → 主文档
3. 内部建设：从 [`project-docs/00-需关注/`](project-docs/00-需关注/README.md) 的交接与问题总账开始

## 贡献要点

- 正式结论写在 `docs/`，并同步更新 `mkdocs.yml` 导航；新模块 CODE 同步 `docs/.linkmap.json`
- 提交前以 `mkdocs build` 作为必跑校验；涉及跨页链接时先跑 `link-interfaces.py`
- 提交信息沿用 `docs:` / `feat:` / `fix:` 等前缀 + 中文摘要
- 更细的页面模板、字段语义与 Agent 约定见 [`AGENTS.md`](AGENTS.md) 与 [`project-docs/00-需关注/实体说明页标准模板.md`](project-docs/00-需关注/实体说明页标准模板.md)
