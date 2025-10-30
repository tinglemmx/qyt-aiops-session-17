resource "iosxe_system" "c8kv2_system" {
  provider             = iosxe.c8kv2 //引用名字
  hostname             = "C8Kv2"
  ip_domain_lookup     = false
  ip_domain_name       = "netdevops.com"
}