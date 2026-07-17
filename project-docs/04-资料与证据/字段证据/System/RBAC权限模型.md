# System：RBAC 权限模型字段证据

> 对应正式页面：[业务说明](../../../../docs/12-系统管理/03-用户与权限/01-RBAC权限模型.md)、[维护与查询参考](../../../../docs/12-系统管理/03-用户与权限/RBAC权限模型-维护与查询参考.md)。
> 基线：测试环境 / `dev` 分支 / 2026-07-15。内部证据页。

## 1. 对象关系

| 业务对象 | 数据对象 | 服务/控制器 | 证据结论 |
| --- | --- | --- | --- |
| 用户 | `system_users` | `AdminUserService` / `UserController` | 账号主体。 |
| 角色 | `system_role` | `RoleService` / `RoleController` | 功能授权载体。 |
| 菜单 | `system_menu`（含 `permission`） | `MenuService` / `MenuController` | 入口 + 权限标识。 |
| 用户↔角色 | `system_user_role` | `PermissionService.assignUserRole` | 多对多。 |
| 角色↔菜单 | `system_role_menu` | `PermissionService.assignRoleMenu` | 多对多。 |

无独立 `system_permission` 表；权限标识存于菜单字段。

## 2. 授权计算（已证实）

1. 用户启用角色 → 角色菜单（启用）→ 菜单 `permission` 集合。  
2. 登录：`GET /system/auth/get-permission-info` 返回角色、菜单树、permissions。  
3. 菜单树排除 type=BUTTON。  
4. 超管角色码 `super_admin`：`getRoleMenuListByRoleId` 返回全部菜单；`hasAnyPermissions` 对超管放行。

重点实现：`PermissionServiceImpl`、`AuthController`、`SecurityFrameworkServiceImpl`、`RoleCodeEnum`。

## 3. 前后端分层

| 层 | 证据 | 结论 |
| --- | --- | --- |
| 前端 | `v-hasPermi` / `hasPermi` 读登录 permissions | 只证明显示条件。 |
| 后端 | `@PreAuthorize("@ss.hasPermission('...')")` | 启用时强制鉴权；严格模式：权限码无对应菜单则非超管无权限。 |
| 缺口 | `UserController` 等多处注解被注释；`assign-role-menu` 注解亦有注释 | 前端可见 ≠ 后端强制。 |

## 4. 菜单证据

`menu.csv`：`/system` 下 `user` / `role` / `menu` / `dept` / `post`。  
快照中 type=3 按钮菜单极少，与前端大量 `system:*` 按钮码对应关系待核验。

## 5. 本刀不覆盖

- 角色 `data_scope` / `assign-role-data-scope` / `getDeptDataPermission`
- 岗位派工、审批主体
- 全站业务页动作矩阵（GAP-014）

## 问题登记

- `GAP-014`：逐页实测矩阵未建立。  
- 按钮菜单快照与前端权限码对齐、注释掉的 `@PreAuthorize`、前端 `*:*:*`/`admin` 与后端 `super_admin` 等价性：随本页续作跟踪。
