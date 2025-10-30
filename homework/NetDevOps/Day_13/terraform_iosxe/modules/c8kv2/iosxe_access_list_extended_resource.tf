# ----------------------Resource是新建配置----------------
resource "iosxe_access_list_extended" "qytang_resource_acl" {
  provider                        = iosxe.c8kv2 //引用名字
  name = "qytang-resource-acl"
  entries = [
    {
      sequence                    = 10
      remark                      = "permit tcp 0 to 1"
      ace_rule_action             = "permit"
      ace_rule_protocol           = "tcp"
      source_prefix               = "10.0.0.0"
      source_prefix_mask          = "0.0.0.255"
      source_port_equal           = "1000"
      destination_host            = "10.1.1.1"
      destination_port_range_from = "1000"
      destination_port_range_to   = "2000"
      ack                         = true
      fin                         = true
      psh                         = true
      rst                         = true
      syn                         = true
      urg                         = true
      dscp                        = "46"
      log                         = true
    },
    {
      sequence                    = 20
      remark                      = "permit ospf any any"
      ace_rule_action             = "permit"
      ace_rule_protocol           = "ospf"
      source_any                  = true
      destination_any             = true
      log                         = true
    },
  ]
}