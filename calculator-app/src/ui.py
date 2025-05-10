import ttkbootstrap as ttk
from ttkbootstrap.constants import *
from PIL import Image, ImageTk, ImageFilter, ImageGrab
import math
import threading

class CalculatorUI:
    def __init__(self):
        self.root = ttk.Window(themename="cosmo")  # 使用 Material Design 风格主题
        self.root.title("Scientific Calculator")
        self.root.geometry("500x800")
        self.last_result = None  # 用于存储上一次计算结果
        self.bg_image = None  # 动态背景图片
        self.original_image = None  # 原始截取的背景图像
        self.update_timer = None  # 定时器
        self.bg_label = None  # 背景标签
        self.create_background()  # 创建动态毛玻璃背景
        self.create_interface()

    def create_background(self):
        """创建动态毛玻璃效果的背景"""
        # 初始化背景标签
        self.bg_label = ttk.Label(self.root)
        self.bg_label.place(x=0, y=0, relwidth=1, relheight=1)

        # 初始化背景
        self.update_background()
        self.root.bind("<Configure>", self.schedule_background_update)  # 窗口移动时更新背景

    def schedule_background_update(self, event=None):
        """限制背景更新频率"""
        if self.update_timer:
            self.root.after_cancel(self.update_timer)  # 取消之前的定时器
        self.update_timer = self.root.after(100, self.update_background)  # 延迟 100 毫秒更新背景

    def update_background(self):
        """更新毛玻璃背景"""
        try:
            # 获取窗口位置
            x = self.root.winfo_rootx()
            y = self.root.winfo_rooty()
            width = self.root.winfo_width()
            height = self.root.winfo_height()

            # 截取桌面背景
            self.original_image = ImageGrab.grab(bbox=(x, y, x + width, y + height))
            blurred_image = self.original_image.filter(ImageFilter.GaussianBlur(15))  # 模糊处理
            self.bg_image = ImageTk.PhotoImage(blurred_image)

            # 更新背景标签的图像
            self.bg_label.configure(image=self.bg_image)
        except Exception as e:
            print(f"Error updating background: {e}")

    def create_interface(self):
        """创建计算器界面"""
        # 字体和颜色设置
        self.font_large = ("Roboto", 20, "bold")
        self.font_medium = ("Roboto", 14)

        # 显示框
        self.entry = ttk.Entry(
            self.root,
            font=self.font_large,
            justify="right",
            bootstyle="info",
        )
        self.entry.pack(fill="x", padx=20, pady=20, ipady=10)

        # 按钮布局
        button_frame = ttk.Frame(self.root, style="secondary.TFrame")
        button_frame.pack(expand=True, fill="both", padx=20, pady=10)

        buttons = [
            ('7', '8', '9', '/'),
            ('4', '5', '6', '*'),
            ('1', '2', '3', '-'),
            ('C', '0', '=', '+'),
            ('sin', 'cos', 'tan', '√'),
            ('x^y', 'log', 'π', 'e'),
            ('mod', 'exp', '(', ')'),
            ('deg', 'rad', 'abs', '!'),
            ('AC', 'ANS', 'DEL', '1/x')
        ]

        for row_index, row in enumerate(buttons):
            for col_index, text in enumerate(row):
                style = "primary" if text == "=" else "secondary"
                button = ttk.Button(
                    button_frame,
                    text=text,
                    bootstyle=style,
                    command=lambda t=text: self.handle_button_click(t)
                )
                button.grid(row=row_index, column=col_index, sticky="nsew", padx=5, pady=5)

        for i in range(4):
            button_frame.columnconfigure(i, weight=1)
        for i in range(len(buttons)):
            button_frame.rowconfigure(i, weight=1)

    def handle_button_click(self, text):
        """处理按钮点击事件"""
        if text == "C":
            self.clear()
        elif text == "AC":
            self.clear_all()
        elif text == "DEL":
            self.delete_last()
        elif text == "=":
            self.calculate()
        elif text == "√":
            self.append_to_entry("math.sqrt(")
        elif text in {"sin", "cos", "tan", "log", "exp", "abs"}:
            self.append_to_entry(f"math.{text}(")
        elif text == "x^y":
            self.append_to_entry("**")
        elif text == "π":
            self.append_to_entry(str(math.pi))
        elif text == "e":
            self.append_to_entry(str(math.e))
        elif text == "mod":
            self.append_to_entry("%")
        elif text == "deg":
            self.append_to_entry("math.degrees(")
        elif text == "rad":
            self.append_to_entry("math.radians(")
        elif text == "!":
            self.append_to_entry("math.factorial(")
        elif text == "1/x":
            self.append_to_entry("1/")
        elif text == "ANS":
            if self.last_result is not None:
                self.append_to_entry(str(self.last_result))
        else:
            self.append_to_entry(text)

    def append_to_entry(self, value):
        """在输入框中追加值"""
        self.entry.insert(ttk.END, value)

    def clear(self):
        """清除当前输入"""
        self.entry.delete(0, ttk.END)

    def clear_all(self):
        """清除所有输入和历史结果"""
        self.entry.delete(0, ttk.END)
        self.last_result = None

    def delete_last(self):
        """删除最后一个字符"""
        current_text = self.entry.get()
        self.entry.delete(0, ttk.END)
        self.entry.insert(0, current_text[:-1])

    def calculate(self):
        """计算表达式"""
        try:
            expression = self.entry.get()
            result = eval(expression)  # 替换为更安全的解析器以避免安全风险
            self.last_result = result
            self.entry.delete(0, ttk.END)
            self.entry.insert(0, result)
        except Exception:
            self.entry.delete(0, ttk.END)
            self.entry.insert(0, "Error")

    def run(self):
        """运行主循环"""
        self.root.mainloop()