def file_diff(file1,file2,file3):
    """ 用for 循环判断file1中的值不在file2中，并写入到file3中,且每一行就一个值 """
    with open(file1, 'r') as f1, open(file2, 'r') as f2, open(file3, 'w') as f3:
        # 读取file2中的所有值到一个集合中
        file2_values = set(line.strip() for line in f2)

        # 遍历file1中的每个值
        for line in f1:
            value = line.strip()

            # 如果该值不在file2中，则写入到file3中
            if value not in file2_values:
                f3.write(value + '\n')
if __name__=="__main__":
    file2 = '/root/ip' # 以这个文件做基础，比对不在这个文件的值
    file1 = '/root/ip1' 
    file3 = 'test_diff.txt'
    file_diff(file1,file2,file3)
