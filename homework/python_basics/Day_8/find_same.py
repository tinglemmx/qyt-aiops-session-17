
def find_same(list1, list2):
    for item in list1:
        if item in list2:
            print(f"{item} in List1 and List2")
        else:
            print(f"{item} only in List1")

if __name__ == '__main__':
    list1 = ['aaa', 111, (4, 5), 2.01]
    list2 = ['bbb', 333, 111, 3.14, (4, 5)]
    print('方案一')
    print("\n".join(f"{x} in List1 and List2" if x in list2 else f"{x} only in List1" for x in list1))
    print('方案二')
    find_same(list1, list2)