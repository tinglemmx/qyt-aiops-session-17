
import influxdb_client, os, time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS



def write_data(client,bucket):
    write_api = client.write_api(write_options=SYNCHRONOUS)
    
    for value in range(5):
        point = (
            Point("measurement1")
            .tag("tagname1", "tagvalue1")
            .field("field1", value)
        )
    write_api.write(bucket=bucket, org="mylab", record=point)
    time.sleep(1) # separate points by 1 second
    
def simple_query_data(client,bucket):
    query_api = client.query_api()

    query = f"""from(bucket: "{bucket}")
	|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "Cisco-IOS-XE-interfaces-oper:interfaces/interface/statistics")
    |> filter(fn: (r) => r["_field"] == "rx_kbps" or r["_field"] == "tx_pps")
    |> filter(fn: (r) => r["host"] == "telegraf-c9kv")
    |> filter(fn: (r) => r["name"] == "GigabitEthernet1/0/1")
    |> filter(fn: (r) => r["path"] == "Cisco-IOS-XE-interfaces-oper:interfaces/interface/statistics")
    |> filter(fn: (r) => r["source"] == "C9Kv")
    |> filter(fn: (r) => r["subscription"] == "671")"""
    tables = query_api.query(query, org="mylab")

    for table in tables:
        for record in table.records:
            print(record)

def aggregate_query_data(client,bucket):
    query_api = client.query_api()

    query = f"""from(bucket: "{bucket}")
	|> range(start: v.timeRangeStart, stop: v.timeRangeStop)
    |> filter(fn: (r) => r["_measurement"] == "Cisco-IOS-XE-interfaces-oper:interfaces/interface/statistics")
    |> filter(fn: (r) => r["_field"] == "rx_kbps" or r["_field"] == "tx_pps")
    |> filter(fn: (r) => r["host"] == "telegraf-c9kv")
    |> filter(fn: (r) => r["name"] == "GigabitEthernet1/0/1")
    |> filter(fn: (r) => r["path"] == "Cisco-IOS-XE-interfaces-oper:interfaces/interface/statistics")
    |> filter(fn: (r) => r["source"] == "C9Kv")
    |> filter(fn: (r) => r["subscription"] == "671")"""
    tables = query_api.query(query, org="mylab")

    for table in tables:
        for record in table.records:
            print(record)



        
if __name__ == "__main__":
    # export INFLUXDB_TOKEN=dUX9YUHrk5QrUqLGnIe9aXmQaoRO8BgugkZ1P9TTuWvXXRdJHmrhOIcXJ8TvN1vDiqkfQ3xbayJsG4oOBk9GAg==
    # token = os.environ.get("INFLUXDB_TOKEN")
    token = "4wYGeODrl8Do42uaYpWSFp542s5bOL3Gwl8YMr9eTmmMt8aU7B4-VrcWJ7aEiQrnCKWvRp8Idzj_FDXzycs_wA=="
    org = "mylab"
    url = "http://172.17.9.210:8086"

    client = influxdb_client.InfluxDBClient(url=url, token=token, org=org)
    bucket = "network_monitor"    

    with InfluxDBClient(url=url, token=token, org=org) as client:
        query = """option v = {timeRangeStart: -10s, timeRangeStop: now()}

    from(bucket: "network_monitor")
        |> range(start: v.timeRangeStart, stop: v.timeRangeStop)
        |> filter(
            fn: (r) =>
                r["_measurement"] == "Cisco-IOS-XE-interfaces-oper:interfaces/interface/statistics",
        )
        |> filter(fn: (r) => r["_field"] == "rx_kbps" or r["_field"] == "tx_kbps")
        |> filter(fn: (r) => r["host"] == "telegraf-c9kv")
        |> filter(fn: (r) => r["name"] == "GigabitEthernet1/0/1")
        |> filter(
            fn: (r) => r["path"] == "Cisco-IOS-XE-interfaces-oper:interfaces/interface/statistics",
        )
        |> filter(fn: (r) => r["source"] == "C9Kv")
        |> filter(fn: (r) => r["subscription"] == "671")
    """
        tables = client.query_api().query(query, org=org)
        for table in tables:
            for record in table.records:
                print(record)          