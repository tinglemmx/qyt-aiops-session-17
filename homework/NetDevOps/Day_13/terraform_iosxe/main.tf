// 加载模块c8kv1
module "c8kv1" {
  source = "./modules/c8kv1"
  DEVICE_LOGIN_USERNAME = var.DEVICE_LOGIN_USERNAME  # 从变量文件中获取, 并且传递给模块
  DEVICE_LOGIN_PASSWORD = var.DEVICE_LOGIN_PASSWORD  # 从变量文件中获取, 并且传递给模块
}

// 加载模块c8kv2
module "c8kv2" {
  source = "./modules/c8kv2"
  DEVICE_LOGIN_USERNAME = var.DEVICE_LOGIN_USERNAME  # 从变量文件中获取, 并且传递给模块
  DEVICE_LOGIN_PASSWORD = var.DEVICE_LOGIN_PASSWORD  # 从变量文件中获取, 并且传递给模块
}

# ~~~~~~~~~添加主机名解析~~~~~~~~~
# 185.199.109.133 objects.githubusercontent.com
# 185.199.111.133 objects.githubusercontent.com
# 185.199.108.133 objects.githubusercontent.com

