# -*- coding: utf-8 -*-
"""Merge aa39df7 base + 44497d9 incremental polish for exclusive W1 files."""
from pathlib import Path

ROOT = Path(r"d:\AgentWorkSpace\MomProductDocument")
TMP = ROOT / "project-docs/90-归档/05-润色回滚备份/_w1-merge-tmp"


def read(name: str) -> str:
    return (TMP / name).read_text(encoding="utf-8")


def write(rel: str, text: str) -> None:
    path = ROOT / rel
    path.write_text(text.rstrip() + "\n", encoding="utf-8", newline="\n")
    print(f"wrote {rel} ({len(text.splitlines())} lines)")


def extract(text: str, start: str, end: str | None = None) -> str:
    i = text.find(start)
    if i < 0:
        raise SystemExit(f"missing start: {start[:80]!r}")
    if end is None:
        return text[i:]
    j = text.find(end, i + len(start))
    if j < 0:
        raise SystemExit(f"missing end after {start[:40]!r}: {end[:80]!r}")
    return text[i:j]


def extract_example_block(text: str, title_substr: str) -> str:
    """Return full !!! example block whose title contains title_substr."""
    needle = "!!! example"
    start = 0
    while True:
        i = text.find(needle, start)
        if i < 0:
            raise SystemExit(f"missing example containing {title_substr!r}")
        line_end = text.find("\n", i)
        header = text[i:line_end]
        if title_substr in header:
            # block continues while indented or blank; stop at next non-indented non-blank
            j = line_end + 1
            while j < len(text):
                nl = text.find("\n", j)
                if nl < 0:
                    nl = len(text)
                line = text[j:nl]
                if line and not line.startswith(" ") and not line.startswith("\t"):
                    break
                j = nl + 1
            return text[i:j].rstrip() + "\n"
        start = i + len(needle)


def merge_bt_ref() -> None:
    aa, w1 = read("dbc-bt-ref.aa39.md"), read("dbc-bt-ref.w1.md")
    w1_head = extract(w1, "# 业务类型-维护与查询参考\n", "## 字段业务语义总表\n")
    aa_sem = extract(aa, "## 字段业务语义\n", "## 配置前检查清单\n")
    w1_check = extract(w1, "## 配置前检查清单\n", "## 查询与变更风险\n")
    w1_risk = extract(w1, "## 查询与变更风险\n")
    merged = (
        w1_head.rstrip()
        + "\n\n"
        + aa_sem.rstrip()
        + "\n\n"
        + w1_check.rstrip()
        + "\n\n"
        + w1_risk.rstrip()
        + "\n"
    )
    assert "行为模式" in merged and "建议回归样例" in merged and "!!! example" in merged
    write("docs/04-DBC-主数据管理/05-策略设置/09-业务类型-维护与查询参考.md", merged)


def merge_ds_ref() -> None:
    aa, w1 = read("dbc-ds-ref.aa39.md"), read("dbc-ds-ref.w1.md")
    w1_head = extract(w1, "# 单据设置-维护与查询参考\n", "## 字段业务语义总表\n")
    aa_sem = extract(aa, "## 字段业务语义\n", "## 新增与编辑约束\n")
    w1_rest = extract(w1, "## 新增与编辑约束\n")
    merged = w1_head.rstrip() + "\n\n" + aa_sem.rstrip() + "\n\n" + w1_rest.rstrip() + "\n"
    assert "行为模式" in merged and "验收清单" in merged and "!!! example" in merged
    write("docs/04-DBC-主数据管理/05-策略设置/10-单据设置-维护与查询参考.md", merged)


def merge_mat_main() -> None:
    """aa39 structure + W1 opening/config/verify/realistic example; keep placeholders & FAQ."""
    aa, w1 = read("dbc-mat-main.aa39.md"), read("dbc-mat-main.w1.md")

    opening = (
        "# 物料基本信息\n\n"
        "> 适用基线：测试环境目标 / `dev` 分支 / 2026-07-15。\n"
        "> 阅读对象：测试、实施与主数据维护人员（主）；采购、仓储、生产等业务人员（顺带）。\n\n"
        "物料基本信息是系统识别和使用实物、半成品、成品及其它物料的统一入口。"
        "采购收货、库存作业、生产用料、销售交付等业务都会引用同一份物料信息。"
        "读完本页应能说清：维护范围与边界、一条物料如何从建档到被业务引用、"
        "本页配置（用途开关 / 类型单位 / 启停）如何改变下游可选范围，以及用哪些点做验证。\n\n"
        "本页说明如何维护一项物料、物料在业务中如何被使用，以及如何查询它的上下游信息。"
        "它不替代 BOM、供应商物料、客户物料或库存页面的具体维护说明。\n\n"
    )

    how = extract(w1, "## 如何使用本组文档\n", "## 一笔典型业务：从建档到被引用\n")
    # keep aa 使用前准备 + screenshot
    prep = extract(aa, "## 使用前准备\n", "## 一项物料如何进入业务\n")
    enter = extract(aa, "## 一项物料如何进入业务\n", "## 维护时的关键判断\n")
    # insert 写实示例 after 📝 placeholder, keep placeholder
    realistic = extract_example_block(w1, "写实示例")
    enter = enter.rstrip() + "\n\n" + realistic.rstrip() + "\n\n"

    judge = extract(aa, "## 维护时的关键判断\n", "## 新增与修改\n")
    add = extract(aa, "## 新增与修改\n", "## 批量维护\n")
    batch = extract(aa, "## 批量维护\n", "## 查询、详情与联查\n")
    query = extract(aa, "## 查询、详情与联查\n", "## 标签与打印\n")
    label = extract(aa, "## 标签与打印\n", "## 常见问题与处理\n")
    faq = extract(aa, "## 常见问题与处理\n", "## 当前限制与待确认事项\n")
    limits = extract(aa, "## 当前限制与待确认事项\n", "## 待补充的图示与示例\n")
    todo = extract(aa, "## 待补充的图示与示例\n")

    config = extract(w1, "## 配置如何起作用\n", "## 建议验证点\n")
    verify = extract(w1, "## 建议验证点\n", "## 关键字段业务角色\n")

    # Insert config+verify after 关键判断 (before 新增与修改)
    merged = (
        opening
        + how.rstrip()
        + "\n\n"
        + prep.rstrip()
        + "\n\n"
        + enter.rstrip()
        + "\n\n"
        + judge.rstrip()
        + "\n\n"
        + config.rstrip()
        + "\n\n"
        + verify.rstrip()
        + "\n\n"
        + add.rstrip()
        + "\n\n"
        + batch.rstrip()
        + "\n\n"
        + query.rstrip()
        + "\n\n"
        + label.rstrip()
        + "\n\n"
        + faq.rstrip()
        + "\n\n"
        + limits.rstrip()
        + "\n\n"
        + todo.rstrip()
        + "\n"
    )
    for must in [
        "配置如何起作用",
        "建议验证点",
        "写实示例",
        "📷 截图占位",
        "📝 示例数据占位",
        "常见问题与处理",
        "待补充的图示与示例",
        "### 新增物料",
        "### 关键字段业务角色",
    ]:
        assert must in merged, must
    write("docs/04-DBC-主数据管理/01-物料管理/01-物料基本信息.md", merged)


def merge_mat_ref() -> None:
    aa, w1 = read("dbc-mat-ref.aa39.md"), read("dbc-mat-ref.w1.md")
    # Keep aa39 full body; strengthen header + 快速定位 from W1; add 操作前快速核对 if missing
    aa_body_from_sem = extract(aa, "## 字段业务语义\n")
    w1_head = extract(w1, "# 物料基本信息-维护与查询参考\n", "## 字段业务语义\n")
    # If W1 has 操作前快速核对 near end, keep aa 仍待业务确认 and add 操作前 if useful
    extra = ""
    if "## 操作前快速核对\n" in w1 and "## 操作前快速核对\n" not in aa:
        extra = "\n\n" + extract(w1, "## 操作前快速核对\n", "## 仍待业务确认\n").rstrip()
        # insert before 仍待业务确认
        if "## 仍待业务确认\n" in aa_body_from_sem:
            pre, post = aa_body_from_sem.split("## 仍待业务确认\n", 1)
            aa_body_from_sem = pre.rstrip() + extra + "\n\n## 仍待业务确认\n" + post
    merged = w1_head.rstrip() + "\n\n" + aa_body_from_sem.rstrip() + "\n"
    assert "行为模式" in merged or "字段业务语义总表" in merged
    assert "!!! example" in merged
    write("docs/04-DBC-主数据管理/01-物料管理/02-物料基本信息-维护与查询参考.md", merged)


def merge_recv_index() -> None:
    aa, w1 = read("wms-recv-index.aa39.md"), read("wms-recv-index.w1.md")

    opening = (
        "# 采购收货\n\n"
        "> 适用基线：测试环境目标 / `dev` 分支 / 2026-07-15。\n"
        "> 阅读对象：测试、实施（主）；采购协同、仓库收货、质量协同等现场角色（顺带）。\n\n"
        "## 业务目的与适用范围\n\n"
        "采购收货把「供应商送达的物料」转化为可追溯的内部收货结果。"
        "它连接采购订单或送货通知、仓库现场执行、库存变化，以及后续的上架、检验、退货和外部系统回写。"
        "读完本页应能说清：功能范围、申请→任务→记录主线、任务配置如何改变现场行为，以及如何开验证场景。\n\n"
        "本页说明从到货到收货完成的一条业务链。"
        "通用的申请、任务和记录概念见[申请、任务与记录模型](../../02-业务模型/01-申请任务记录模型.md)；"
        "本页只说明采购收货的来源、现场执行、库存影响和异常处理。\n\n"
    )

    how = (
        "## 如何使用本组文档\n\n"
        "| 你的目的 | 建议阅读 |\n"
        "| --- | --- |\n"
        "| 设计验证场景、讲解配置影响、讲清一笔收货主线 | **本页**（功能范围、逻辑、配置、验证点） |\n"
        "| 想理解采购到货如何变成可追溯的收货和库存结果 | 本页。按一笔收货、角色、关键决策和异常处理理解主线。 |\n"
        "| 发起/承接/执行/撤销、查选择器范围与字段细节 | [采购收货-维护与查询参考](01-采购收货-维护与查询参考.md) |\n"
        "| 对照共享模型（申请/任务/记录、库存挂接、粒度） | "
        "[申请、任务与记录模型](../../02-业务模型/01-申请任务记录模型.md)、"
        "[库存数据挂接模型](../../02-业务模型/02-库存数据挂接模型.md)、"
        "[库存管理精度与唯一粒度](../../02-业务模型/08-库存管理精度与唯一粒度.md) |\n\n"
        "售前/对外介绍请停在模块「解决什么问题」层，**不要**默认进入本页维护参考与字段长表。\n\n"
    )

    prep = extract(aa, "## 使用前准备\n", "## 一笔采购收货如何完成\n")
    flow = extract(aa, "## 一笔采购收货如何完成\n", "### 收货过程中要作出的关键判断\n")
    realistic = extract_example_block(w1, "写实示例：给定配置")
    # keep aa placeholders; add realistic after 📝 placeholder block
    flow = flow.rstrip() + "\n\n" + realistic.rstrip() + "\n\n"

    judge = extract(aa, "### 收货过程中要作出的关键判断\n", "## 三类业务对象分别做什么\n")
    objs = extract(aa, "## 三类业务对象分别做什么\n", "## 角色与操作分工\n")
    roles = extract(aa, "## 角色与操作分工\n", "## 状态与关键动作\n")
    status = extract(aa, "## 状态与关键动作\n", "## 现场执行：Web 与 PDA\n")
    field = extract(aa, "## 现场执行：Web 与 PDA\n", "## 对库存和相关业务的影响\n")
    inv = extract(aa, "## 对库存和相关业务的影响\n", "## 数量差异、拒收与撤销\n")
    qty = extract(aa, "## 数量差异、拒收与撤销\n", "## 查询、详情与追溯\n")
    query = extract(aa, "## 查询、详情与追溯\n", "## 常见问题与处理\n")
    faq = extract(aa, "## 常见问题与处理\n", "## 当前限制与待确认事项\n")
    limits = extract(aa, "## 当前限制与待确认事项\n", "## 待补充的图示与示例\n")
    todo = extract(aa, "## 待补充的图示与示例\n")

    config = extract(w1, "## 配置如何起作用\n", "## 建议验证点\n")
    verify = extract(w1, "## 建议验证点\n", "## 做完影响什么\n")

    # Place config+verify after 现场执行, before 对库存
    merged = (
        opening
        + how
        + prep.rstrip()
        + "\n\n"
        + flow.rstrip()
        + "\n\n"
        + judge.rstrip()
        + "\n\n"
        + objs.rstrip()
        + "\n\n"
        + roles.rstrip()
        + "\n\n"
        + status.rstrip()
        + "\n\n"
        + field.rstrip()
        + "\n\n"
        + config.rstrip()
        + "\n\n"
        + verify.rstrip()
        + "\n\n"
        + inv.rstrip()
        + "\n\n"
        + qty.rstrip()
        + "\n\n"
        + query.rstrip()
        + "\n\n"
        + faq.rstrip()
        + "\n\n"
        + limits.rstrip()
        + "\n\n"
        + todo.rstrip()
        + "\n"
    )
    for must in [
        "配置如何起作用",
        "建议验证点",
        "写实示例",
        "📷 截图占位",
        "📝 示例数据占位",
        "常见问题与处理",
        "待补充的图示与示例",
        "数量差异、拒收与撤销",
        "关键字段业务角色",
        "GAP-010",
        "note right of 任务进行中",
    ]:
        assert must in merged, must
    write("docs/05-WMS-库房管理/03-采购收货/index.md", merged)


def merge_recv_ref() -> None:
    aa, w1 = read("wms-recv-ref.aa39.md"), read("wms-recv-ref.w1.md")
    # Base aa39 (field tables up front). Strengthen header + 快速定位; add 写实示例 in 任务; keep 待补充.
    w1_purpose = (
        "> 适用基线：测试环境目标 / `dev` 分支 / 2026-07-15。\n"
        "> 用途：配合[采购收货](index.md)使用。本页给测试、实施与日常操作：怎样发起、承接、执行、查询与定位异常。"
        "端到端主线、配置影响与建议验证点以主文档为准。\n"
    )
    quick = (
        "## 快速定位\n\n"
        "| 你要做什么 | 先看哪里 |\n"
        "| --- | --- |\n"
        "| 理解配置如何改变现场行为、开验证场景 | 返回[采购收货主文档](index.md)「配置如何起作用」「建议验证点」 |\n"
        "| 理解选择器范围、联动、回填与门禁 | 「字段业务语义」 |\n"
        "| 从来源单据发起收货 | 「申请：建立待处理到货」 |\n"
        "| 到现场收货或拒收 | 「任务：承接与现场执行」 |\n"
        "| 查实际结果、上架或撤销 | 「记录：实际收货结果」 |\n"
        "| 查库存为什么没有变化 | 「库存影响与追溯」 |\n"
        "| 使用 PDA | 「终端执行参考」 |\n"
        "| 想先理解收货为什么要经过申请、任务和记录 | 返回[采购收货](index.md) |\n"
    )

    # aa from 字段业务语义 through 任务 section; inject realistic example before 任务 screenshot
    sem = extract(aa, "## 字段业务语义\n", "## 业务对象关系\n")
    rel = extract(aa, "## 业务对象关系\n", "## 申请：建立待处理到货\n")
    app = extract(aa, "## 申请：建立待处理到货\n", "## 任务：承接与现场执行\n")
    task = extract(aa, "## 任务：承接与现场执行\n", "## 记录：实际收货结果\n")
    realistic = extract_example_block(w1, "写实示例：任务配置")
    # insert before last 📷 in task section
    if '!!! example "📷 截图占位"' in task:
        pre, post = task.rsplit('!!! example "📷 截图占位"', 1)
        task = pre.rstrip() + "\n\n" + realistic.rstrip() + "\n\n!!! example \"📷 截图占位\"" + post
    rec = extract(aa, "## 记录：实际收货结果\n", "## 库存影响与追溯\n")
    inv = extract(aa, "## 库存影响与追溯\n", "## 终端执行参考\n")
    term = extract(aa, "## 终端执行参考\n", "## 查询与详情参考\n")
    qry = extract(aa, "## 查询与详情参考\n", "## 操作前的快速核对\n")
    chk = extract(aa, "## 操作前的快速核对\n", "## 待补充的状态图与示例\n")
    todo = extract(aa, "## 待补充的状态图与示例\n")

    merged = (
        "# 采购收货-维护与查询参考\n\n"
        + w1_purpose
        + "\n"
        + quick
        + "\n"
        + sem.rstrip()
        + "\n\n"
        + rel.rstrip()
        + "\n\n"
        + app.rstrip()
        + "\n\n"
        + task.rstrip()
        + "\n\n"
        + rec.rstrip()
        + "\n\n"
        + inv.rstrip()
        + "\n\n"
        + term.rstrip()
        + "\n\n"
        + qry.rstrip()
        + "\n\n"
        + chk.rstrip()
        + "\n\n"
        + todo.rstrip()
        + "\n"
    )
    for must in [
        "字段业务语义总表",
        "状态-动作摘要",
        "写实示例",
        "📷 截图占位",
        "待补充的状态图与示例",
        "数量与换算表",
    ]:
        assert must in merged, must
    write("docs/05-WMS-库房管理/03-采购收货/01-采购收货-维护与查询参考.md", merged)


def merge_bt_main() -> None:
    aa, w1 = read("dbc-bt-main.aa39.md"), read("dbc-bt-main.w1.md")
    aa_table = extract(aa, "## 关键字段业务角色\n", "## 维护与查询重点\n")
    before, after = w1.split("## 关键字段业务角色\n", 1)
    # drop W1's shorter table; keep from 做完影响什么 onward
    after_from = after.split("## 做完影响什么\n", 1)[1]
    # keep aa table trailing links, then continue W1 sections
    merged = (
        before.rstrip()
        + "\n\n"
        + aa_table.rstrip()
        + "\n\n## 做完影响什么\n"
        + after_from.lstrip()
    )
    assert "关键行为要点" in merged
    assert "配置如何起作用" in merged and "建议验证点" in merged
    assert "写实示例" in merged and "📷 截图占位" in merged
    write("docs/04-DBC-主数据管理/05-策略设置/03-业务类型.md", merged)


def merge_ds_main() -> None:
    aa, w1 = read("dbc-ds-main.aa39.md"), read("dbc-ds-main.w1.md")
    aa_table = extract(aa, "## 关键字段业务角色\n", "## 什么时候需要维护\n")
    aa_judge = extract(aa, "## 维护时最重要的判断\n", "## 查询与联查\n")
    aa_todo = extract(aa, "## 待补充的图示与示例\n")

    before, after = w1.split("## 关键字段业务角色\n", 1)
    after_from = after.split("## 什么时候需要维护\n", 1)[1]
    body = "## 什么时候需要维护\n" + after_from
    body = body.replace("## 做完影响什么\n", aa_judge + "## 做完影响什么\n", 1)

    # trim W1 trailing screenshot under 当前边界; append aa 待补充 (screenshot+tip)
    head, tail = body.split("## 当前边界（不打断主线）", 1)
    if "!!! example" in tail:
        tail = tail.split("!!! example")[0].rstrip() + "\n\n"
    body = head + "## 当前边界（不打断主线）" + tail + aa_todo

    merged = before.rstrip() + "\n\n" + aa_table.rstrip() + "\n\n" + body.lstrip()
    assert "关键行为要点" in merged
    assert "维护时最重要的判断" in merged
    assert "待补充的图示与示例" in merged and "!!! tip" in merged
    assert "配置如何起作用" in merged and "建议验证点" in merged
    assert "写实示例" in merged
    write("docs/04-DBC-主数据管理/05-策略设置/04-单据设置.md", merged)


def verify_bt_ds_mains() -> None:
    bt = (ROOT / "docs/04-DBC-主数据管理/05-策略设置/03-业务类型.md").read_text(encoding="utf-8")
    ds = (ROOT / "docs/04-DBC-主数据管理/05-策略设置/04-单据设置.md").read_text(encoding="utf-8")
    assert "配置如何起作用" in bt and "建议验证点" in bt and "写实示例" in bt
    assert "关键行为要点" in bt
    assert "📷 截图占位" in bt
    assert "配置如何起作用" in ds and "建议验证点" in ds and "写实示例" in ds
    assert "维护时最重要的判断" in ds
    assert "待补充的图示与示例" in ds and "!!! tip" in ds
    assert "关键行为要点" in ds
    print("bt/ds mains verify ok")


def main() -> None:
    merge_bt_main()
    merge_ds_main()
    verify_bt_ds_mains()
    merge_bt_ref()
    merge_ds_ref()
    merge_mat_main()
    merge_mat_ref()
    merge_recv_index()
    merge_recv_ref()
    print("all done")


if __name__ == "__main__":
    main()
