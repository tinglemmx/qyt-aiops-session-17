resource "iosxe_interface_ethernet" "interface_g2" {
  provider                       = iosxe.c8kv1 //引用名字
  type                           = "GigabitEthernet"
  name                           = "2"
  description                    = "Terraform Configure Interface G2"
  shutdown                       = false
  ipv4_address                   = "172.16.12.1"
  ipv4_address_mask              = "255.255.255.0"
  ip_access_group_in             = data.iosxe_access_list_extended.qytang_data_acl.name  # 一定要有这个ACL, 否则就会出错
  ip_access_group_in_enable      = true

}

# -----------------------------这个注释掉配置可以被删除-------------------------------
# resource "iosxe_interface_ethernet" "interface_g3" {
#  provider                       = iosxe.c8kv1 //引用名字
#  type                           = "GigabitEthernet"
#  name                           = "3"
#  description                    = "Terraform Configure Interface G3"
#  shutdown                       = false
#  ipv4_address                   = "172.16.21.1"
#  ipv4_address_mask              = "255.255.255.0"
#  ip_access_group_in             = data.iosxe_access_list_extended.qytang_data_acl.name  # 一定要有这个ACL, 否则就会出错
#  ip_access_group_in_enable      = true
# }

resource "iosxe_interface_loopback" "interface_loop0" {
  provider                   = iosxe.c8kv1 //引用名字
  name                       = 0
  description                = "Terraform Configure Interface Lo0"
  shutdown                   = false
  ipv4_address               = "1.1.1.1"
  ipv4_address_mask          = "255.255.255.0"
}

# -----------------------------这个注释掉配置可以被删除-------------------------------
# resource "iosxe_interface_loopback" "interface_loop1" {
#  provider                   = iosxe.c8kv1 //引用名字
#  name                       = 1
#  description                = "Terraform Configure Interface Lo0"
#  shutdown                   = false
#  ipv4_address               = "11.1.1.1"
#  ipv4_address_mask          = "255.255.255.0"
# }
