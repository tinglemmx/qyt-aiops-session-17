import os
from pathlib import Path

def init(job_dir):
    os.chdir(str(job_dir))
    if os.path.exists('test'):
        clean(job_dir)
    os.mkdir('test')
    os.chdir('test')
    qytang1 = open('qytang1','w')
    qytang1.write('test file\n')
    qytang1.write('this is qytang\n')
    qytang1.close()
    qytang2 = open('qytang2','w')
    qytang2.write('test file\n')
    qytang2.write('qytang python\n')
    qytang2.close()
    qytang3 = open('qytang3','w')
    qytang3.write('test file\n')
    qytang3.write('this is python\n')
    qytang3.close()
    os.mkdir('qytang4')
    os.mkdir('qytang5')

def clean(job_dir):
    os.chdir(str(job_dir))
    for root, dirs, files in os.walk('test',topdown=False):
        for name in files:
            tmp_file = os.path.join(root, name)
            # print(f'删除文件：{tmp_file}')
            os.remove(tmp_file)
        for name in dirs:
            tmp_dir = os.path.join(root, name)
            # print(f'删除目录：{tmp_dir}')
            os.rmdir(tmp_dir)
    # print(f'删除目录：test')
    os.removedirs('test')

def scenario1(job_dir):
    os.chdir(str(job_dir/'test'))
    for file_or_dir in sorted(os.listdir(os.getcwd())):
        if os.path.isfile(file_or_dir):
            with open(file_or_dir,'r') as f:
                if 'qytang' in f.read():
                    print(file_or_dir)
                    
def scenario2(job_dir):
    os.chdir(str(job_dir))
    for root, dirs, files in os.walk('test',topdown=False):
        for name in sorted(files):
            tmp_file = os.path.join(root, name)
            with open(tmp_file,'r') as f:
                if 'qytang' in f.read():
                    print(name)


if __name__ == '__main__':
    job_dir = Path(__file__).parent
    print(f'作业测试根目录：{job_dir}')
    print(f'初始化test目录结构{job_dir/"test"}')
    init(job_dir)
    print('文件中包含"qytang"关键字的文件为：')
    print('方案一：')
    scenario1(job_dir)
    print('方案二：')
    scenario2(job_dir)
    print(f'删除test目录结构{job_dir/"test"}')
    clean(job_dir)