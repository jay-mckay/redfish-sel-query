with open('hosts.txt', 'w') as file:
    for i in range(1, 400):
        num = str(i).rjust(3, '0')
        host = 'kp' + num + '-ipmi'
        file.write(host + '\n')
