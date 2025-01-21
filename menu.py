import os
import cv2
import subprocess
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
import glob

# 用户可以直接修改下面这行代码来更改菜单标题
menu_title = "我的视频菜单"  # 修改这里的内容来更改菜单标题

# 获取视频文件列表
def get_video_files():
    video_extensions = ['*.mp4', '*.mpg', '*.mlv', '*.avi', '*.st']
    files = []
    for ext in video_extensions:
        files.extend(glob.glob(ext))
    return files

# 截取视频的第24帧
def capture_frame(video_file):
    cap = cv2.VideoCapture(video_file)
    cap.set(cv2.CAP_PROP_POS_FRAMES, 24)  # 跳转到第24帧
    ret, frame = cap.read()
    if ret:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        image = Image.fromarray(frame)
        # 调整图片大小（最大宽度200，高度150）
        image.thumbnail((200, 150))
        return image
    else:
        return None

# 播放视频
def play_video(video_file):
    vlc_command = f"vlc --fullscreen --no-video-title-show {video_file}"
    vlc_process = subprocess.Popen(vlc_command, shell=True)
    return vlc_process

# 截断长标题：根据容器宽度动态调整
def shorten_title(root, title, max_width=200):
    # 去掉文件扩展名
    title_without_ext = os.path.splitext(title)[0]

    # 创建一个临时Label来计算文本宽度
    temp_label = tk.Label(root, text=title_without_ext, font=("Arial", 10))
    temp_label.update_idletasks()  # 确保文本被渲染，获取宽度
    title_width = temp_label.winfo_width()

    # 如果标题宽度超过了最大允许宽度，则需要截断
    if title_width > max_width:
        # 找到合适的截断位置
        while title_width > max_width:
            title_without_ext = title_without_ext[:-1]  # 每次去掉一个字符
            temp_label.config(text=title_without_ext + "...")
            temp_label.update_idletasks()
            title_width = temp_label.winfo_width()

        title_without_ext = title_without_ext + "..."

    return title_without_ext

# 创建菜单界面
class VideoMenuApp:
    def __init__(self, root):
        self.root = root
        self.root.title(menu_title)  # 使用用户定义的标题
        self.root.geometry("1100x700")  # 调整窗口大小
        self.videos = get_video_files()
        self.frames = [capture_frame(video) for video in self.videos]
        self.current_page = 0
        self.vlc_process = None

        # 顶部的标题
        self.title_label = tk.Label(self.root, text=menu_title, font=("Arial", 20), pady=20)
        self.title_label.pack(pady=20)

        # 显示视频封面和控制按钮的Canvas
        self.canvas = tk.Canvas(self.root)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.buttons = []
        self.create_menu()

        # 翻页按钮
        self.prev_button = tk.Button(self.root, text="上一页", command=self.prev_page)
        self.prev_button.pack(side=tk.LEFT, padx=20)

        self.next_button = tk.Button(self.root, text="下一页", command=self.next_page)
        self.next_button.pack(side=tk.RIGHT, padx=20)

        # 结束按钮
        self.exit_button = tk.Button(self.root, text="结束", command=self.exit_vlc)
        self.exit_button.pack(side=tk.BOTTOM, pady=20)

    # 创建菜单界面
    def create_menu(self):
        self.canvas.delete("all")  # 清除之前的封面按钮
        self.buttons.clear()

        start_index = self.current_page * 12  # 每页显示12个视频封面
        end_index = min((self.current_page + 1) * 12, len(self.videos))

        for i in range(start_index, end_index):
            image = self.frames[i]
            video_name = os.path.basename(self.videos[i])

            # 截断并去除扩展名
            video_name = shorten_title(self.root, video_name, max_width=200)

            # 转换为tkinter兼容格式
            image = ImageTk.PhotoImage(image)

            # 创建按钮
            button = tk.Button(self.canvas, image=image, text=video_name, compound=tk.TOP,
                               command=lambda i=i: self.on_video_select(i))
            button.image = image  # 保持引用
            button.grid(row=(i - start_index) // 4, column=(i - start_index) % 4, padx=10, pady=10)
            self.buttons.append(button)

    # 用户点击菜单封面时播放视频
    def on_video_select(self, index):
        if self.vlc_process:
            self.vlc_process.terminate()
        self.vlc_process = play_video(self.videos[index])

        # 关闭菜单界面
        self.root.withdraw()

        # 监控VLC进程结束
        self.root.after(100, self.monitor_vlc)

    # 监控VLC进程
    def monitor_vlc(self):
        if self.vlc_process.poll() is None:  # VLC进程仍然在运行
            self.root.after(100, self.monitor_vlc)
        else:
            self.root.deiconify()  # 显示菜单界面

    # 前一页
    def prev_page(self):
        if self.current_page > 0:
            self.current_page -= 1
            self.create_menu()

    # 下一页
    def next_page(self):
        if (self.current_page + 1) * 12 < len(self.videos):
            self.current_page += 1
            self.create_menu()

    # 结束VLC进程
    def exit_vlc(self):
        if self.vlc_process:
            self.vlc_process.terminate()
        self.root.quit()

# 启动GUI
if __name__ == "__main__":
    root = tk.Tk()
    app = VideoMenuApp(root)
    root.mainloop()
