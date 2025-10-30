terraform {
  required_providers {
    iosxe = {
      source = "CiscoDevNet/iosxe"
      version = "0.9.3"
    }
  }
}

provider "iosxe" {
  alias    = "c8kv2" //名字
  username = var.DEVICE_LOGIN_USERNAME
  password = var.DEVICE_LOGIN_PASSWORD
  url      = "https://172.17.9.216"
}
