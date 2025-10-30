output "c8kv2_resource_acl_entries" {
  value = iosxe_access_list_extended.qytang_resource_acl.entries
}

output "c8kv2_g2_ip" {
  value = iosxe_interface_ethernet.interface_g2.ipv4_address
}