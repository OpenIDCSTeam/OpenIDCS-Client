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

-- 主机存储配置表 (hs_saving)
CREATE TABLE IF NOT EXISTS hs_saving (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    hs_name TEXT NOT NULL,
    saving_key TEXT NOT NULL,
    saving_value TEXT NOT NULL, -- JSON格式存储数据
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (hs_name) REFERENCES hs_config(hs_name) ON DELETE CASCADE,
    UNIQUE(hs_name, saving_key)
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
CREATE INDEX IF NOT EXISTS idx_hs_saving_name ON hs_saving(hs_name);
CREATE INDEX IF NOT EXISTS idx_vm_saving_name ON vm_saving(hs_name);
CREATE INDEX IF NOT EXISTS idx_vm_saving_uuid ON vm_saving(vm_uuid);
CREATE INDEX IF NOT EXISTS idx_vm_status_name ON vm_status(hs_name);
CREATE INDEX IF NOT EXISTS idx_vm_status_uuid ON vm_status(vm_uuid);
CREATE INDEX IF NOT EXISTS idx_vm_tasker_name ON vm_tasker(hs_name);
CREATE INDEX IF NOT EXISTS idx_hs_logger_name ON hs_logger(hs_name);
CREATE INDEX IF NOT EXISTS idx_hs_logger_created ON hs_logger(created_at);

-- 插入默认的全局配置
INSERT OR IGNORE INTO hs_global (id, bearer, saving) VALUES (1, '', './DataSaving');