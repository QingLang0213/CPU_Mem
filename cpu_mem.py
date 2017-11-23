#coding=utf-8
from Tkinter import *
import tkMessageBox
import sys,os,time
import xlsxwriter
import math
import threading
import tkFileDialog

Native_Heap=[]      #Native层占用内存(PSS)
Dalvik_Heap=[]      #Dalvik虚拟机占用内存(PSS)
Heap_Size_Dalvik=[] #Dalvik Heap总共的内存大小
Total_PSS=[]        #应用占用的PSS内存
Total_CPU=[]
CPU=[]
Time=[]

date=time.strftime('%Y-%m-%d-%H-%M',time.localtime(time.time()))

file_path=os.path.abspath(sys.argv[0])  
path_list=file_path.split('\\')
path_list.pop()
path='\\'.join(path_list)

path=path+'\\result\\'
log_path=path+'\\'

log_path=unicode(log_path,"gb2312")
path=unicode(path,"gb2312")

if not os.path.exists(path):#目录不存在则创建
    os.makedirs(path)
if not os.path.exists(log_path):#目录不存在则创建
    os.makedirs(log_path)

flag=False

class myThread (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, name, device,pkg_name,delay_time,limit):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.device=device
        self.pkg_name=pkg_name
        self.delay_time=delay_time
        self.limit=limit
        
    def run(self):#把要执行的代码写到run函数里面 线程在创建后会直接运行run函数
        t1=math.floor(time.time())
        while(not flag):
            try:
                self.cpu()
                self.mem()
                t2=math.floor(time.time())
                while (t2-t1)%self.delay_time!=0: #计算时间差
                    t2=math.floor(time.time())
                Time.append(time.strftime('%H:%M:%S',time.localtime(t2))) 
            except Exception as e: #捕获Ctrl+C事件 ，捕获设备断开事件
                print'thread1 run error'
                print e
                #write_xlsx(self.limit,self.pkg_name)             
                
    
    def mem(self):
        mem_info=os.popen("adb -s %s shell dumpsys meminfo %s"%(self.device,self.pkg_name)).readlines()
        for mem in mem_info:  
            if "Native Heap" in mem:
                Native_Heap.append(int(mem.split()[2])/1024)#字符转换为整形，KB单位转换为M
            elif "Dalvik Heap" in mem:
                Dalvik=mem.split()
                Dalvik_Heap.append(int(Dalvik[2])/1024)
                Heap_Size_Dalvik.append(int(Dalvik[6])/1024)
            elif "TOTAL" in mem:
                Total_PSS.append(int(mem.split()[1])/1024)
                return True


    def cpu(self):
        
        top_info =os.popen("adb -s %s shell top -d 3 -n 1"%self.device).readlines()
        total_info=top_info[3].split('%')[0]
        total=total_info[4:]
        Total_CPU.append(total)
        for info in top_info:
            if (self.pkg_name+'\r\n') in info:
                cpu=info.split('%')[0][10:]
                CPU.append(int(cpu))
                return True
                

class myThread2 (threading.Thread):   #继承父类threading.Thread
    def __init__(self, threadID, name, delay_time,app):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.app=app
        self.delay_time=delay_time

    def run(self):
        time.sleep(self.delay_time+2)
        def counter(i):#定时器
            #print i
            if not flag:
                #print CPU[i] ,Total_PSS[i]
                c=CPU[i]
                m=Total_PSS[i]
                self.app.text_msglist.insert(END, 'CPU info: '+str(c)+'%\n', 'green')
                self.app.text_msglist.insert(END, 'Mem info: '+str(m)+'M\n', 'blue')
                self.app.text_msglist.see(END)
                self.app.text_msglist.after(self.delay_time*1000,counter,i+1)
            else:
                self.app.b1.config(state=NORMAL)
                return 0
        self.app.b1.config(state=DISABLED)
        counter(0)
        
    def stop(self):
        self.stopped = True

    def isStopped(self):
        return self.stopped


def get_path(ico):
    try:
        base_path = sys._MEIPASS
    except AttributeError:
        base_path = os.path.abspath(".")
    base_path=unicode(base_path,"gb2312")
    return os.path.join(base_path, ico)

        
class Application(Frame):
       
    def __init__(self,master):
        Frame.__init__(self,master)
        self.root = master 
        self.root.title('CPU_MEM(v1.0.0,qing.guo)')
        self.root.geometry('635x350')
        self.root.resizable(0, 0)  # 禁止调整窗口大小
        self.root.protocol("WM_DELETE_WINDOW",self.close)
        self.root.iconbitmap(get_path('cpu.ico')) 
        
    def creatWidgets(self):
        frame_left_top=Frame(self.root,width=355, height=210,bg='#C1CDCD')
        frame_left_center=Frame(self.root,width=355, height=80,bg='#C1CDCD')
        frame_left_bottom=Frame(self.root,width=355, height=60,bg='#C1CDCD')
        frame_right=Frame(self.root,width=280,height=350,bg='#C1CDCD')
    
        frame_left_top.grid_propagate(0)
        frame_left_center.grid_propagate(0)
        frame_left_bottom.grid_propagate(0)
        frame_right.propagate(0)
        #frame_right.grid_propagate(0)

        frame_left_top.grid(row=0,column=0)
        frame_left_center.grid(row=1,column=0)
        frame_left_bottom.grid(row=2,column=0)
        frame_right.grid(row=0,column=1,rowspan=3)

        self.v1=StringVar()
        self.v2=StringVar()
        self.v3=StringVar()
        self.v4=StringVar()
        self.v3.set('5')
        self.v4.set(path)
        #Label
        Label(frame_left_top, text="设备id:", bg='#C1CDCD').grid(row=0,column=0,sticky=NW,padx=5,pady=20)
        Label(frame_left_top, text="应用包名:", bg='#C1CDCD').grid(row=1,column=0,sticky=NW,padx=5,pady=20)
        Label(frame_left_top, text="间隔时间(s):", bg='#C1CDCD').grid(row=2,column=0,sticky=NW,padx=5,pady=20)
        #Entery
        Entry(frame_left_top, width=28,textvariable=self.v1).grid(row=0,column=1,sticky=NW,padx=5,pady=20)
        Entry(frame_left_top,width=28,textvariable=self.v2).grid(row=1,column=1,sticky=NW,padx=5,pady=20)
        Entry(frame_left_top, width=28,textvariable=self.v3).grid(row=2,column=1,sticky=NW,padx=5,pady=20)
        Entry(frame_left_bottom, width=35,textvariable=self.v4).grid(row=0,column=1,ipady=4,padx=5)
        
        #Button
        Button(frame_left_top, text="点击获取",command=self.set_device, bg='#C1CDCD').grid(row=0,column=2)
        Button(frame_left_top, text="点击获取",command=self.get_package, bg='#C1CDCD').grid(row=1,column=2)
        
        self.b1=Button(frame_left_center, text="开始测试",command=self.start_test, bg='#C1CDCD')
        self.b1.grid(row=0,column=0,padx=50,pady=15)
        self.b2=Button(frame_left_center, text="停止测试",command=self.end_test, bg='#C1CDCD')
        self.b2.grid(row=0,column=1,padx=50,pady=15)
        Button(frame_left_bottom, text="打开文件",command=self.open_file, bg='#C1CDCD').grid(row=0,column=0,padx=13)
        #Scrollbar
        scrollbar=Scrollbar(frame_right)
        scrollbar.pack(side=RIGHT, fill=Y )
        self.text_msglist=Text(frame_right, yscrollcommand = scrollbar.set,width=100,bg='#C1CDCD')
        self.text_msglist.pack(side = RIGHT, fill =BOTH)
        scrollbar['command'] = self.text_msglist.yview
        self.text_msglist.tag_config('green', foreground='#008B00')
        self.text_msglist.tag_config('blue', foreground='#0000FF')
        self.text_msglist.tag_config('red', foreground='#FF3030')
        self.text_msglist.tag_config('purple', foreground='#CD00CD')
    
        
    def start_test(self):
        global flag
        flag=False
        self.b1.config(state=DISABLED)
        self.b2.config(state=NORMAL)
        device=self.v1.get()
        self.pkg_name=self.v2.get()
        delay_time=int(self.v3.get())
        if device=='' or device.isspace():
            self.text_msglist.insert(END, 'please input device id \n', 'red')
        elif self.pkg_name=='' or self.pkg_name.isspace():
            self.text_msglist.insert(END, 'please input app packagename \n', 'red')
        elif delay_time<5:
            self.text_msglist.insert(END, 'delay_time must greater than 5s\n', 'red')
            
        limit_size=os.popen('adb -s %s shell getprop|findstr heapgrowthlimit'%device).readlines()[0]
        self.limit=limit_size.split('[')[2][:-3]
        self.text_msglist.insert(END, limit_size+'\n', 'blue')
        self.text_msglist.see(END)
        self.thread1 = myThread(1, 'cpu_mem,', device, self.pkg_name,delay_time,self.limit)
        self.thread1.setDaemon(True)
        self.thread1.start()
        self.thread2 = myThread2(2,'start',delay_time,app)
        self.thread2.setDaemon(True)
        self.thread2.start()
        
        
    def end_test(self):
        global flag
        flag=tkMessageBox.askokcancel(message = "确定停止测试")
        if flag:
            write_xlsx(self.limit,self.pkg_name)
            self.b1.config(state=NORMAL)
            self.b2.config(state=DISABLED)
            
            #self.root.quit()
            #self.root.destroy()
            
    def open_file(self):
        filename = tkFileDialog.askopenfilename(initialdir=path)
        if filename=='':
            return 0
        os.startfile(filename)
    
    def set_device(self):
        device_info=os.popen('adb devices').readlines()
        #print device_info
        device=device_info[-2]
        device_id=device.split('\t')[0]
        #print device_id
        self.v1.set(device_id)
        
    def get_package(self):
        pattern = re.compile(r"[a-zA-Z0-9_\.]+/[a-zA-Z0-9_\.]+")
        device=self.v1.get()
        #print device
        out = os.popen("adb -s %s shell dumpsys window w | findstr \/ | findstr name="%device).read()
        if out=='':
            out = os.popen("adb shell dumpsys window w | findstr \/ | findstr name=").read()
        if out !='':
            component=pattern.findall(out)[-1]
            package=component.split('/')[0]
            #print package
            self.v2.set(package)
            
    def close(self):      
        result=tkMessageBox.askokcancel(title=u"退出", message=u"退出前请先停止测试以保存测试结果，确定退出程序？")
        if result:
            self.root.quit()
            self.root.destroy()


def write_xlsx(limit,pkg_name):
    w=xlsxwriter.Workbook(path+'CPU_Mem_'+date+'.xlsx')
    ws1=w.add_worksheet('data')
    ws2=w.add_worksheet('chart')
    title=['Time','App Used CPU(%)','Total Used CPU(%)','App Used Memory PSS(MB)',\
           'Native_Heap','Dalvik_Heap','Heap_Size_Dalvik <'+limit]
    #写入标题
    for i in range(7):
        ws1.write(0,i,title[i])

    result_list=[Time,CPU,Total_CPU,Total_PSS,Native_Heap,Dalvik_Heap,Heap_Size_Dalvik]
  
    c=['A','B','C','D','E','F','G']
    for i in range(7):
        ws1.write_column(c[i]+'2', result_list[i])
    
    #绘制图表
    chart1=w.add_chart({'type':'line'})
    chart2=w.add_chart({'type':'line'})
    
    chart1.add_series(  
    { 'name': '=data!$B$1'
     ,'categories':'=data!$A$2:$A$%d'%(len(Time))
     ,'values':'=data!$B$2:$B$%d'%(len(Time))
     ,'line':   {'width': 1.25 ,'color': 'green'}
    })
    
    chart2.add_series(  
    { 'name': '=data!$D$1'
     ,'categories':'=data!$A$2:$A$%d'%(len(Time))
     ,'values': '=data!$D$2:$D$%d'%(len(Time))
     ,'line':   {'width': 1.25 ,'color': 'blue'}
    })
    
    chart1.set_title({'name': pkg_name+':CPU'})#图表名称
    chart1.set_size({'width': 1500, 'height': 800})
    chart2.set_title({'name': pkg_name+':Mem'})#图表名称
    chart2.set_size({'width': 1500, 'height': 800})
    #插入图表
    ws2.insert_chart('A2',chart1,{'x_offset':10,'y_offset':10})     
    ws2.insert_chart('A50',chart2,{'x_offset':10,'y_offset':10})         
    w.close()    


    
if __name__ == "__main__":

    f=open(log_path+'cpu_mem_log.txt','w')
    sys.stderr=f
    root=Tk()
    app=Application(root)
    app.creatWidgets()
    app.mainloop()
    f.close()
   

