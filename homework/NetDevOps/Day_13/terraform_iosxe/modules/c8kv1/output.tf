output "c8kv1_data_acl_entries" {
  value = data.iosxe_access_list_extended.qytang_data_acl.entries
}

output "c8kv1_g2_ip" {
  value = iosxe_interface_ethernet.interface_g2.ipv4_address
}