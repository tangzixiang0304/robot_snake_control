
send_history=[[10,0],[1,0],[1,0],[1,0],[2,0],[3,0],[3,0],[3,0],[3,0],[30,0],[30,0],[10,0]]
angle_history=[[10,0],[4,0],[1,0],[1,0],[2,0],[3,0],[3,0],[3,0],[3,0],[30,0],[30,0],[10,0]]

def make_history_data():
    datas = send_history
    data_history = 0
    data_times = 0
    for i, data in enumerate(datas):
        if data == data_history:
            data_times += 1
            if data_times > 1:
                send_history[i] = 0
                angle_history[i] = 0
        else:
            data_times = 0
        data_history = data
    print send_history
    print angle_history
    while 0 in send_history:
        send_history.remove(0)
    while 0 in angle_history:
        angle_history.remove(0)
    print send_history
    print angle_history

make_history_data()
