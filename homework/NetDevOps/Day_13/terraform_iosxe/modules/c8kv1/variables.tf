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