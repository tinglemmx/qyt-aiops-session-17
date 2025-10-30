resource "iosxe_interface_ethernet" "interface_g2" {
  provider                       = iosxe.c8kv2 //引用名字
  type                           = "GigabitEthernet"
  name                           = "2"
  description                    = "Terraform Configure Interface G2"
  shutdown                       = false
  ipv4_address                   = "172.16.12.2"
  ipv4_address_mask              = "255.255.255.0"
  ip_access_group_in             = iosxe_access_list_extended.qytang_resource_acl.name
  ip_access_group_in_enable      = true
}

resource "iosxe_interface_loopback" "interface_loop0" {
  provider                   = iosxe.c8kv2 //引用名字
  name                       = 0
  description                = "Terraform Configure Interface Lo0"
  shutdown                   = false
  ipv4_address               = "2.2.2.2"
  ipv4_address_mask          = "255.255.255.0"
}