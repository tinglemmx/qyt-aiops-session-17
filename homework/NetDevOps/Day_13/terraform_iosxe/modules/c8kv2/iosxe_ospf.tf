resource "iosxe_ospf" "c8kv2_ospf" {
  provider     = iosxe.c8kv2 //引用名字
  process_id   = var.ospf_process_id
  networks = var.ospf_networks
  router_id = var.ospf_router_id
}