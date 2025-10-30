variable ospf_process_id {
  type = number
  default = 1
}

variable ospf_router_id {
  type = string
  default = "2.2.2.2"
}

variable "ospf_networks" {
  description = "A list of network configurations for OSPF"
  type = list(object({
    ip       = string
    wildcard = string
    area     = string
  }))
  default = [
    {
      ip       = "172.16.12.0"
      wildcard = "0.0.0.255"
      area     = "0"
    },
    {
      ip       = "2.2.2.0"
      wildcard = "0.0.0.255"
      area     = "0"
    }
  ]
}

# 需要准备变量, 虽然这些变量是从顶层变量文件中获取的
variable "DEVICE_LOGIN_USERNAME" {
  type        = string
  description = "Username for device login"
}

variable "DEVICE_LOGIN_PASSWORD" {
  type        = string
  description = "Password for device login"
  sensitive   = true
} 