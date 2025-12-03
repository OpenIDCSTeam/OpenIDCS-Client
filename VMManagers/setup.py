from cx_Freeze import setup, Executable

# 设置你的程序名称和版本
program_name = "NetworkConfiguratorService"
program_version = "1.0"

# 指定你的主程序文件
main_script = "agent.py"

# 配置 cx_Freeze
setup(
    name=program_name,
    version=program_version,
    description="Network Configurator Service",
    executables=[Executable(main_script)],
    options={
        "build_exe": {
            # 包含的文件和模块
            "include_files": [],
            "includes": [],
            # 排除的文件和模块
            "excludes": [],
            # 目标平台（可选，通常自动检测）
        }
    }
)