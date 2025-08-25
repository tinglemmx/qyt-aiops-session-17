'''
补齐被删除的代码
'''

department1 = 'Security'
department2 = 'Python'
depart1_m = 'cq_bomb'
depart2_m = 'qinke'
COURSE_FEES_SEC = 456789.12456
COURSE_FEES_Python = 1234.3456


# line1 = "Department1 name:%-10s Manager:%-10s COURSE FEES:%-10.2f The End!" % (
#     department1, depart1_m, COURSE_FEES_SEC
# )
# line2 = "Department2 name:%-10s Manager:%-10s COURSE FEES:%-10.2f The End!" % (
#     department2, depart2_m, COURSE_FEES_Python
# )

# line1 = "Department1 name:{:<10} Manager:{:<10} COURSE FEES:{:<10.2f} The End!".format(
#     department1, depart1_m, COURSE_FEES_SEC
# )
# line2 = "Department2 name:{:<10} Manager:{:<10} COURSE FEES:{:<10.2f} The End!".format(
#     department2, depart2_m, COURSE_FEES_Python
# ) 

line1 = (
    f"Department1 name:{department1:<10} "
    f"Manager:{depart1_m:<10} "
    f"COURSE FEES:{COURSE_FEES_SEC:<10.2f} "
    f"The End!"
)

line2 = (
    f"Department2 name:{department2:<10} "
    f"Manager:{depart2_m:<10} "
    f"COURSE FEES:{COURSE_FEES_Python:<10.2f} "
    f"The End!"
)


length = len(line1)
print('='*length)
print(line1)
print(line2)
print('='*length)