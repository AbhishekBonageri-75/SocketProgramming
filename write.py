import sys
def wdata(data_to_write):
    file1 = open('myfile.txt', 'a')
    file1.writelines(data_to_write)
    file1.writelines("\n")
    file1.close()

