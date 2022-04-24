def wdata(data_to_write):
    file1 = open('myfile.txt', 'a')
    file1.writelines(data_to_write)
    file1.writelines("\n")
    file1.close()

    # print the most recent ping response to the screen
    inp = input("1.Complete file \n2.Most recent ping")
    if(inp == "1"):
        file1 = open('myfile.txt', 'r')
        print(file1.read())
        file1.close()
        return

    elif(inp == "2"):
        file1 = open('myfile.txt', 'r')
        print(file1.readlines()[-2])
        print(file1.readlines()[-1])
        file1.close()
        return
    else:
        print("Invalid input")
        return

