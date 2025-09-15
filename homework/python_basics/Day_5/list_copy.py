import copy

def sort_list(list: list):
    tmp_list = copy.copy(list)
    tmp_list.sort()
    return tmp_list

if __name__ == '__main__':
    l1 = [4,5,7,1,3,9,0]
    l2 = sort_list(l1)
    for i in range(len(l1)):
        print(l1[i],l2[i])