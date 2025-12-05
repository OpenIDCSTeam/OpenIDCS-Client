from HostModule.DataManage import HostDatabase

db = HostDatabase()
conn = db.get_connection()

vm_uuid = "ecs_testvm"

# 先删除状态，再删除配置
conn.execute("DELETE FROM vm_status WHERE vm_uuid = ?", (vm_uuid,))
conn.execute("DELETE FROM vm_saving WHERE vm_uuid = ?", (vm_uuid,))
conn.commit()
conn.close()