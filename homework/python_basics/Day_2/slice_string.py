'''
通过切片创建子字符串
现在有个字符串word = " scallywag"，创建一个变量sub_word，通过切片的方式获得字符串"ally"，将字符串的内容赋予sub_word。
'''

def slice_string():
    word = "scallywag"
    sub_word = word[2:6]
    print(sub_word)

if __name__ == "__main__":
    slice_string()