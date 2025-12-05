-- OpenIDCS Host Management Database Schema
-- SQLite数据库表结构定义

-- 全局配置表 (hs_global)
CREATE TABLE IF NOT EXISTS hs_global (
    id INTEGER PRIMARY KEY CHECK (id = 1),
    bearer TEXT NOT NULL,
    saving TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 主机配置表 (hs_config)
CREATE TABLE IF NOT EXISTS hs_config (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_name TEXT NOT NULL UNIQUE,
    server_type TEXT NOT NULL,
    server_addr TEXT NOT NULL,
    server_user TEXT NOT NULL,
    server_pass TEXT NOT NULL,
    filter_name TEXT DEFAULT '',
    images_path TEXT,
    system_path TEXT,
    backup_path TEXT,
    extern_path TEXT,
    launch_path TEXT,
    network_nat TEXT,
    network_pub TEXT,
    i_kuai_addr TEXT DEFAULT '', -- 爱快OS地址
    i_kuai_user TEXT DEFAULT '', -- 爱快OS用户
    i_kuai_pass TEXT DEFAULT '', -- 爱快OS密码
    ports_start INTEGER DEFAULT 0, -- TCP端口起始
    ports_close INTEGER DEFAULT 0, -- TCP端口结束
    remote_port INTEGER DEFAULT 0, -- VNC服务端口
    system_maps TEXT DEFAULT '{}', -- JSON格式存储系统映射字典
    public_addr TEXT DEFAULT '[]', -- JSON格式存储公共IPV46列表
    extend_data TEXT DEFAULT '{}', -- JSON格式存储扩展数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 主机状态表 (hs_status)
CREATE TABLE IF NOT EXISTS hs_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_name TEXT NOT NULL,
    status_data TEXT NOT NULL, -- JSON格式存储HWStatus数据
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hs_name) REFERENCES hs_config(hs_name) ON DELETE CASCADE
);



-- 虚拟机存储配置表 (vm_saving)
CREATE TABLE IF NOT EXISTS vm_saving (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_name TEXT NOT NULL,
    vm_uuid TEXT NOT NULL,
    vm_config TEXT NOT NULL, -- JSON格式存储VMConfig数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hs_name) REFERENCES hs_config(hs_name) ON DELETE CASCADE,
    UNIQUE(hs_name, vm_uuid)
);

-- 虚拟机状态表 (vm_status)
CREATE TABLE IF NOT EXISTS vm_status (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_name TEXT NOT NULL,
    vm_uuid TEXT NOT NULL,
    status_data TEXT NOT NULL, -- JSON格式存储HWStatus列表数据
    recorded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hs_name) REFERENCES hs_config(hs_name) ON DELETE CASCADE
    -- 注意: 不再引用 vm_saving(vm_uuid)，因为 vm_uuid 不是单列唯一键
);

-- 虚拟机任务表 (vm_tasker)
CREATE TABLE IF NOT EXISTS vm_tasker (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_name TEXT NOT NULL,
    task_data TEXT NOT NULL, -- JSON格式存储HSTasker数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hs_name) REFERENCES hs_config(hs_name) ON DELETE CASCADE
);

-- 日志记录表 (hs_logger)
CREATE TABLE IF NOT EXISTS hs_logger (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_name TEXT,
    log_data TEXT NOT NULL, -- JSON格式存储ZMessage数据
    log_level TEXT DEFAULT 'INFO',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hs_name) REFERENCES hs_config(hs_name) ON DELETE SET NULL
);

-- 创建索引以提高查询性能
CREATE INDEX IF NOT EXISTS idx_hs_config_name ON hs_config(hs_name);
CREATE INDEX IF NOT EXISTS idx_hs_status_name ON hs_status(hs_name);
CREATE INDEX IF NOT EXISTS idx_vm_saving_name ON vm_saving(hs_name);
CREATE INDEX IF NOT EXISTS idx_vm_saving_uuid ON vm_saving(vm_uuid);
CREATE INDEX IF NOT EXISTS idx_vm_status_name ON vm_status(hs_name);
CREATE INDEX IF NOT EXISTS idx_vm_status_uuid ON vm_status(vm_uuid);
CREATE INDEX IF NOT EXISTS idx_vm_tasker_name ON vm_tasker(hs_name);
CREATE INDEX IF NOT EXISTS idx_hs_logger_name ON hs_logger(hs_name);
CREATE INDEX IF NOT EXISTS idx_hs_logger_created ON hs_logger(created_at);

-- 插入默认的全局配置
INSERT OR IGNORE INTO hs_global (id, bearer, saving) VALUES (1, '', './DataSaving');

-- =================================================================
-- 数据库升级脚本 (用于现有数据库升级)
-- =================================================================

-- 检查并创建升级日志表
CREATE TABLE IF NOT EXISTS hs_migration_log (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    version TEXT NOT NULL,
    description TEXT,
    executed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 升级函数：添加字段（如果不存在）
-- 由于SQLite不支持ALTER TABLE IF NOT EXISTS，我们需要手动检查

-- Version 1.0: 添加爱快OS相关字段
-- ALTER TABLE hs_config ADD COLUMN i_kuai_addr TEXT DEFAULT '';
-- ALTER TABLE hs_config ADD COLUMN i_kuai_user TEXT DEFAULT '';
-- ALTER TABLE hs_config ADD COLUMN i_kuai_pass TEXT DEFAULT '';

-- Version 1.1: 添加端口配置字段
-- ALTER TABLE hs_config ADD COLUMN ports_start INTEGER DEFAULT 0;
-- ALTER TABLE hs_config ADD COLUMN ports_close INTEGER DEFAULT 0;
-- ALTER TABLE hs_config ADD COLUMN remote_port INTEGER DEFAULT 0;

-- Version 1.2: 添加系统和网络配置字段
-- ALTER TABLE hs_config ADD COLUMN system_maps TEXT DEFAULT '{}';
-- ALTER TABLE hs_config ADD COLUMN public_addr TEXT DEFAULT '[]';

-- Version 1.3: 添加扩展数据字段
-- ALTER TABLE hs_config ADD COLUMN extend_data TEXT DEFAULT '{}';

-- =================================================================
-- 临时升级脚本执行（一次性使用）
-- =================================================================

-- 执行以下语句来添加缺失的字段（请根据实际情况取消注释需要的语句）

-- 1. 爱快OS相关字段
-- ALTER TABLE hs_config ADD COLUMN i_kuai_addr TEXT DEFAULT '';
-- ALTER TABLE hs_config ADD COLUMN i_kuai_user TEXT DEFAULT '';
-- ALTER TABLE hs_config ADD COLUMN i_kuai_pass TEXT DEFAULT '';

-- 2. 端口配置字段
-- ALTER TABLE hs_config ADD COLUMN ports_start INTEGER DEFAULT 0;
-- ALTER TABLE hs_config ADD COLUMN ports_close INTEGER DEFAULT 0;
-- ALTER TABLE hs_config ADD COLUMN remote_port INTEGER DEFAULT 0;

-- 3. 系统和网络配置字段
-- ALTER TABLE hs_config ADD COLUMN system_maps TEXT DEFAULT '{}';
-- ALTER TABLE hs_config ADD COLUMN public_addr TEXT DEFAULT '[]';

-- 4. 扩展数据字段
-- ALTER TABLE hs_config ADD COLUMN extend_data TEXT DEFAULT '{}';

-- 清理：删除不再使用的hs_saving表 (如果存在)
DROP TABLE IF EXISTS hs_saving;

-- 注意事项：
-- 1. 以上ALTER TABLE语句如果字段已存在会报错，这是正常的
-- 2. 执行前请备份数据库
-- 3. 执行完成后可以注释掉这些ALTER TABLE语句