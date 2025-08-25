'''
创造自己的语言 我们将在英语的基础上创建自己的语言：在单词的最后加上-，然后将单词的第一个字母拿出来放到单词的最后，然后在单词的最后加上y，例如，Python，就变成了ython-Py
'''

def my_language(word):
    return word[1:] + '-' + word[0] + 'y'

if __name__ == "__main__":
    print(my_language("Python"))  # 输出: ython-Py
    print(my_language("hello"))   # 输出: ello-hy
    print(my_language("world"))   # 输出: orld-wy