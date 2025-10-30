# 提前配置
# ip access-list extended qytang_data_acl
#   10 permit ip host 1.1.1.1 host 2.2.2.2
#   20 permit ip any any

# ------------Data是引用设备上已经存在的配置，Resource是新配置----------------
data "iosxe_access_list_extended" "qytang_data_acl" {
  provider                        = iosxe.c8kv1 //引用名字
  name                            = "qytang_data_acl"
}