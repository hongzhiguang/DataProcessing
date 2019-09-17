import os,re,traceback,time
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdate

def ioFileGen(old_file_path,new_file_path):

    t_pattern = re.compile(r'(\d+)/(\d+)/(\d+)\s+(\d+:\d+:\d+)')
    sda_util_pattern = re.compile(r'\s+(\d+\.\d+)$')

    try:
        fpo = open(new_file_path, "w+")
        fpo.write("DateTime" + "," + "%util" + "\n")

        with open(old_file_path, "r") as fp:
            for line in fp:
                if re.findall(t_pattern, line.strip()):
                    t_val = re.findall(t_pattern, line)[0]
                    year = "20" + t_val[2]
                    month = t_val[0]
                    day = t_val[1]
                    time = t_val[3]
                    datetime = '%s-%s-%s %s' % (year, month, day, time)
                    fpo.write(datetime + ",")
                elif re.match(r"sda",line.strip()) and re.findall(sda_util_pattern, line.strip()):
                    util_val = re.findall(sda_util_pattern, line)[0]
                    fpo.write(util_val + "\n")
                else:
                    continue
        fpo.close()
    except Exception as e:
        traceback.print_exc()

def cpuFileGen(old_file_path,new_file_path):

    d_pattern = re.compile(r'(\d+)/(\d+)/(\d+)')
    t_pattern = re.compile(r'\d+:\d+:\d+')
    idle_pattern = re.compile(r'\s+(\d+\.\d+)$')

    # 当没有date的时候，设置一个默认的date:
    date = '2019-8-25'
    try:
        fpo = open(new_file_path, "w+")
        fpo.write("DateTime" + "," + "%usage" + "\n")

        with open(old_file_path, "r") as fp:
            bef_time = ''
            for line in fp:
                if re.findall(d_pattern, line.strip()):
                    d_val = re.findall(d_pattern, line)[0]
                    year = "20" + d_val[2]
                    month = d_val[0]
                    day = d_val[1]
                    date = '%s-%s-%s' % (year, month, day)
                elif re.findall(t_pattern, line.strip()) and re.findall(idle_pattern, line.strip()):
                    time = re.findall(t_pattern, line)[0]
                    if bef_time:
                        if int(bef_time[:2])-int(time[:2]) == 23:
                            day = int(d_val[1]) + 1
                            date = '%s-%s-%s' % (year, month, str(day))
                    datetime = '%s %s' % (date,time)
                    fpo.write(datetime + ",")
                    idle_val = re.findall(idle_pattern, line)[0]
                    usage_val = 100-float(idle_val)
                    fpo.write(str(float('%.2f' % usage_val)) + "\n")
                    bef_time = time
                else:
                    continue
        fpo.close()
    except Exception as e:
        traceback.print_exc()

def memFileGen(old_file_path,new_file_path):
    t_pattern = re.compile(r'\d+-\d+-\d+\s+\d+:\d+:\d+')
    use_men_pattern = re.compile(r'-(\d+),')

    try:
        fpo = open(new_file_path, "w+")
        fpo.write("DateTime" + "," + "UserMem" + "\n")

        with open(old_file_path, "r") as fp:
            for line in fp:
                if re.findall(t_pattern, line) and re.findall(use_men_pattern, line):
                    t_val = re.findall(t_pattern, line)[0]
                    use_mem_val = re.findall(use_men_pattern, line)[0]
                    fpo.write(t_val + ",")
                    fpo.write(use_mem_val + "\n")
                else:
                    continue
        fpo.close()
    except Exception as e:
        traceback.print_exc()

def threadsFileGen(old_file_path,new_file_path):
    t_pattern = re.compile(r'\d+-\d+-\d+\s+\d+:\d+:\d+')
    actThreads_pattern = re.compile(r'-Total\s+active\s+threads\s+=\s+(\d+)\s+')

    try:
        fpo = open(new_file_path, "w+")
        fpo.write("DateTime" + "," + "ThreadNum" + "\n")

        with open(old_file_path, "r") as fp:
            for line in fp:
                if re.findall(t_pattern, line) and re.findall(actThreads_pattern, line):
                    t_val = re.findall(t_pattern, line)[0]
                    use_mem_val = re.findall(actThreads_pattern, line)[0]
                    fpo.write(t_val + ",")
                    fpo.write(use_mem_val + "\n")
                else:
                    continue
        fpo.close()
    except Exception as e:
        traceback.print_exc()

def GenPlot(data_path,save_path,x_label,y_label,title):
    # 解决中文显示问题
    plt.rcParams['font.sans-serif'] = ['SimHei']
    plt.rcParams['axes.unicode_minus'] = False

    DataFrame = pd.read_csv(data_path, header=0, sep=",")
    rowNum = DataFrame.shape[0]
    colNum = DataFrame.columns.size
    # print(rowNum, colNum)
    fig1 = plt.figure(figsize=(18, 12))
    # 这里只需要画一个图表
    ax1 = fig1.add_subplot(1, 1, 1)
    # 设置时间标签显示格式
    ax1.xaxis.set_major_formatter(mdate.DateFormatter('%Y-%m-%d %H:%M:%S'))
    # 设置x轴坐标值和标签旋转45°的显示方式
    plt.xticks(rotation=45)
    DataFrame[x_label] = pd.to_datetime(DataFrame[x_label])
    plt.plot(DataFrame[x_label],DataFrame[y_label],linewidth=3)
    plt.xlabel(x_label,fontsize=20)
    plt.ylabel(y_label,fontsize=20)
    plt.title(title,fontsize=20)
    plt.xticks(fontsize=20)
    plt.yticks(fontsize=20)
    plt.savefig(save_path,dpi=500,bbox_inches='tight')
    plt.show()

def main():
    current_path = os.getcwd()
    files_path = []

    for root,dirs,files in os.walk(current_path):
        for file in files:
            file_path = os.path.join(root,file)
            files_path.append(file_path)

    files_path_new = []
    for file_path in files_path:
        path,file_name = os.path.split(file_path)
        name,suf = os.path.splitext(file_name)
        if not re.findall(r"iostat_i10_new",name) and "iostat_i10" in name:
            new_io_file_path = os.path.normpath(os.path.join(path,name+"_new"+suf))
            ioFileGen(file_path, new_io_file_path)
            time.sleep(2)
            files_path_new.append(file_path)
            files_path_new.append(new_io_file_path)
        elif not re.findall(r"_sar10_new",name) and "_sar10" in name:
            new_cpu_file_path = os.path.normpath(os.path.join(path,name+"_new"+suf))
            cpuFileGen(file_path, new_cpu_file_path)
            time.sleep(2)
            files_path_new.append(file_path)
            files_path_new.append(new_cpu_file_path)
        elif not re.findall(r"PLATFORM_MEMORY[\w_]+_new",name) and "PLATFORM_MEMORY" in name:
            new_mem_path = os.path.normpath(os.path.join(path,name+"_new"+suf))
            memFileGen(file_path,new_mem_path)
            time.sleep(2)
            files_path_new.append(file_path)
            files_path_new.append(new_mem_path)
        elif not re.findall(r"PLATFORM_THREADS[\w_]+_new",name) and "PLATFORM_THREADS" in name:
            new_threads_path = os.path.normpath(os.path.join(path, name + "_new" + suf))
            threadsFileGen(file_path, new_threads_path)
            time.sleep(2)
            files_path_new.append(file_path)
            files_path_new.append(new_threads_path)
        else:
            continue

    for file_path in files_path_new:
        path, file_name = os.path.split(file_path)
        name, suf = os.path.splitext(file_name)
        if "iostat_i10_new" in name and suf == ".txt":
            save_io_path = os.path.normpath(os.path.join(path, name + ".png"))
            GenPlot(file_path,save_io_path,"DateTime","%util","磁盘IO忙闲率")
            time.sleep(2)
        elif "_sar10_new" in name and suf == ".txt":
            save_cpu_path = os.path.normpath(os.path.join(path,name+".png"))
            GenPlot(file_path,save_cpu_path,"DateTime","%usage","CPU使用率")
            time.sleep(2)
        elif re.findall(r"PLATFORM_MEMORY[\w_]+_new",name) and suf == ".txt":
            save_mem_path = os.path.normpath(os.path.join(path,name+".png"))
            GenPlot(file_path,save_mem_path,"DateTime","UserMem","Memory使用率")
            time.sleep(2)
        elif re.findall(r"PLATFORM_THREADS[\w_]+_new",name) and suf == ".txt":
            save_threads_path = os.path.normpath(os.path.join(path, name + ".png"))
            GenPlot(file_path, save_threads_path,"DateTime","ThreadNum","活动线程数")
            time.sleep(2)
        else:
            continue

if __name__ == "__main__":
    main()
