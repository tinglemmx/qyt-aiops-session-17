resource "iosxe_ospf" "c8kv1_ospf" {
  provider     = iosxe.c8kv1 //引用名字
  process_id   = 1
  networks = [
    {
      ip       = "172.16.12.0"
      wildcard = "0.0.0.255"
      area     = "0"
    },
    {
      ip       = "1.1.1.0"
      wildcard = "0.0.0.255"
      area     = "0"
    },
  #  {
  #    ip       = "11.1.1.0"
  #    wildcard = "0.0.0.255"
  #    area     = "0"
  #  }
  ]
  router_id = "1.1.1.1"
}