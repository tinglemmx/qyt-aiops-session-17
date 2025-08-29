
def port_sort_key(port):
    # 'eth 1/101/1/42' -> [1,101,1,42]
    return [int(x) if x.isdigit() else x for x in port.replace("eth ","").split("/")]



if __name__=="__main__":

    port_list = [
        'eth 1/101/1/42','eth 1/101/1/26','eth 1/101/1/23',
        'eth 1/101/1/7','eth 1/101/2/46','eth 1/101/1/34',
        'eth 1/101/1/18','eth 1/101/1/13','eth 1/101/1/32',
        'eth 1/101/1/25','eth 1/101/1/45','eth 1/101/2/8'
    ]
    sorted_ports = sorted(port_list, key=port_sort_key)
    print(sorted_ports)


