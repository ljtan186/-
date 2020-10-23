import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import time


def get_data(data_path, label_path):
    '''
    data_path为对应的数据的位置
    label_path为对应的数据标签的位置
    '''
    # data_df =  pd.read_csv(data_path)
    data_df = pd.read_excel(data_path)
    # label_df =  pd.read_csv(label_path)
    label_df = pd.read_excel(label_path)
    # print(data_df,label_df)
    if len(data_df) == len(label_df):
        print("数据长度和标签长度不同，请检查")
        return 'error'

    data_final_df = pd.merge(data_df, label_df, how='inner', on='ID')
    data_final_df = data_final_df.sort_values(by='GEARSTIME')
    data_final_df = data_final_df.reset_index(drop=True)
    print(data_final_df, len(data_final_df))
    return data_final_df.values.tolist(), data_final_df.columns.values


def find_field(data, label_coloum, point_nums):
    '''
    查找所有的田地的情况
    point_nums 多选前后的点数
    '''
    # 变量 储存每一个开始和结束的点
    places = []
    signal = 0
    place_t = []
    total_num = len(data)

    for i, p in enumerate(data):
        # print(p)
        # print(p[14])
        if p[label_coloum] == 1 and signal == 0:
            signal = 1
            place_t.append(i - point_nums if i - point_nums >= 0 else 0)

        elif p[label_coloum] == 0 and signal == 1:
            signal = 0
            place_t.append(i + point_nums if i +
                           point_nums < total_num else total_num - 1)
            places.append(place_t)
            place_t = []

    if signal == 1:
        place_t.append(total_num - 1)
        places.append(place_t)
    return places


def tellme(s, fontsize=16):
    print(s)
    plt.title(s, fontsize=fontsize)
    plt.draw()


def changeFigure(data, place, lat_coloum, lng_coloum, label_coloum, mtype,
                 now_no, all_no):
    '''
    mtype: 0是道路 1是田地
    '''
    temp_new = []
    place_now = np.array(data[place[0]:place[1] + 1])
    # print(place_now)
    tellme(str(place[0]) + "\n please click now!")
    plt.scatter(place_now[:, lat_coloum],
                place_now[:, lng_coloum],
                c=place_now[:, label_coloum])
    plt.draw()
    while True:
        tellme(
            "{0}/{1}  ".format(now_no, all_no) +
            'click 3 points to select the {0} areas \n'
            ' middle mouse button to finish \n right'
            ' mouse button to cancel'.format('field' if mtype ==
                                             1 else 'road'), 10)
        pts = np.asarray(plt.ginput(4, timeout=-1))
        if len(pts) < 4:
            tellme('Too few points, starting over')
            time.sleep(1)  # Wait a second
            break
        ph = plt.fill(pts[:, 0], pts[:, 1], c=(1, 0, 0, 0.5), lw=0)
        tellme(' Key click for yes, mouse click for no')
        if not plt.waitforbuttonpress():
            for ph_i in ph:
                ph_i.remove()
            continue
        for ph_i in ph:
            ph_i.remove()
            print(ph_i)
            print(place_now[:, lat_coloum:lng_coloum + 1].astype(np.float64))
            result = ph_i.get_path().contains_points(
                place_now[:, lat_coloum:lng_coloum + 1].astype(np.float64))
            if True in result:
                for i in range(0, len(result)):
                    if result[i]:
                        # 修改数据，首先修改读取部分的数据的tag 用于显示，然后记录修改的位置
                        # 最终确认后修改的位置
                        place_now[i, label_coloum] = mtype
                        temp_new.append(i + place[0])

        plt.scatter(place_now[:, lat_coloum],
                    place_now[:, lng_coloum],
                    c=place_now[:, label_coloum])
        plt.draw()
    tellme(' Key click for save, mouse click for cancel')
    if plt.waitforbuttonpress():
        for i in temp_new:
            data[i][label_coloum] = mtype
    return data, place


def savafile(data, path, coloum_names):
    data = pd.DataFrame(data, columns=coloum_names)
    data.to_excel(path)


if __name__ == "__main__":
    # 定义一些文件相关的常量
    lat_coloum = 2
    lng_coloum = 3
    label_coloum = 14
    point_nums = 100

    data_path = "cleandata1.xlsx"
    label_path = "labal1.xlsx"
    final_label_path = "new-table.xlsx"
    data, coloum_names = get_data(data_path, label_path)
    places = find_field(data, label_coloum, point_nums)
    print(places)
    for ti, place in enumerate(places):
        data, place = changeFigure(data, place, lat_coloum, lng_coloum,
                                   label_coloum, 2, ti, len(places))
        savafile(data, final_label_path, coloum_names)
        plt.clf()

    tellme("All done,Please Close the windows!")
    plt.show()
