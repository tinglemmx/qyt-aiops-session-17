resource "iosxe_system" "c8kv1_system" {
  provider             = iosxe.c8kv1 //引用名字
  hostname             = "C8Kv1"
  ip_domain_lookup     = false
  ip_domain_name       = "netdevops.com"
}

