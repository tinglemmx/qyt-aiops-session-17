output "c8kv1_data_acl_entries" {
  value = module.c8kv1.c8kv1_data_acl_entries
}

output "c8kv1_interface_g2_ip" {
  value = module.c8kv1.c8kv1_g2_ip
}

output "c8kv2_resource_acl_entries" {
  value = module.c8kv2.c8kv2_resource_acl_entries
}

output "c8kv2_interface_g2_ip" {
  value = module.c8kv2.c8kv2_g2_ip
}
