from influxdb import InfluxDBClient



influx_host = '172.17.9.210'
influx_db = "qytdb"
influx_port = 8086
influx_measurement = "router_monitor"
influx_user = "qytdbuser"
influx_password = "Cisc0123"



client = InfluxDBClient(influx_host, influx_port, influx_user, influx_password, influx_db)

# 查询数据
result = client.query('SELECT * FROM "router_monitor" ORDER BY time DESC LIMIT 15')
for point in result.get_points():
    print(point)
    
    
# 查看所有 measurement
measurements = client.get_list_measurements()
print(measurements)

# 删除 measurement
# client.query('DROP MEASUREMENT router_monitor')

# measurements = client.get_list_measurements()
# print(measurements)
