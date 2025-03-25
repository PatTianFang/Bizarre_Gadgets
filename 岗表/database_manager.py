from tinydb import TinyDB, Query
from tinydb.middlewares import CachingMiddleware
from tinydb.storages import JSONStorage
import tkinter as tk
from tkinter import ttk
from ttkthemes import ThemedTk
from tkinter import filedialog
import pandas as pd
import webbrowser
from tkinter import messagebox  # 引入 messagebox 模块

# 初始化数据库
db = TinyDB('database.json', storage=CachingMiddleware(JSONStorage), encoding="utf-8")  # 指定 utf-8 编码
User = Query()

# 创建主窗口
root = ThemedTk(theme="sun-valley")
root.title("数据库管理软件v1.0   -By 埃及猪肉")
root.geometry("800x600")

# 设置窗口图标
root.iconphoto(False, tk.PhotoImage(file='logo.png'))

# 更新数据预览表格
def update_table():
    try:
        for row in table.get_children():
            table.delete(row)
        for record in db.table("_default").all():  # 修复循环逻辑，直接遍历记录
            table.insert("", "end", values=(
                record["姓名"],
                record["学号"],
                record["免白天岗状态"],
                record["免夜间岗状态"],
                record["站岗状态"],
                record["站白天岗次数"],
                record["站夜间岗次数"]
            ))
    except FileNotFoundError:
        messagebox.showerror("错误", "数据库文件未找到！")
    except Exception as e:
        messagebox.showerror("错误", f"加载数据库失败：{str(e)}")

# 添加数据函数
def add_data():
    name = name_var.get()
    student_id = student_id_var.get()
    exempt_day = exempt_day_var.get()
    exempt_night = exempt_night_var.get()
    on_duty = on_duty_var.get()
    day_duty_count = day_duty_count_var.get()
    night_duty_count = night_duty_count_var.get()

    # 数据验证
    if not name or not student_id.isdigit():
        status_label.config(text="请输入有效的姓名和学号！", foreground="red")
        return

    if db.table("_default").contains(User.学号 == int(student_id)):  # 适配 _default 嵌套结构
        status_label.config(text="学号已存在！", foreground="red")
        return

    # 插入数据
    db.table("_default").insert({  # 适配 _default 嵌套结构
        "姓名": name,
        "学号": int(student_id),
        "免白天岗状态": int(exempt_day),
        "免夜间岗状态": int(exempt_night),
        "站岗状态": on_duty,
        "站白天岗次数": int(day_duty_count),
        "站夜间岗次数": int(night_duty_count)
    })
    db.storage.flush()  # 同步到文件
    status_label.config(text="数据添加成功！", foreground="green")
    update_table()
    clear_inputs()

# 删除数据函数
# 修改删除数据函数中的查询条件
def delete_data():
    selected_item = table.selection()
    if not selected_item:
        status_label.config(text="请选择要删除的记录！", foreground="red")
        return

    try:
        for item in selected_item:
            values = table.item(item, "values")
            student_id = int(values[1])  # 获取学号并转换为整数

            # 修改这里 ↓↓↓ 原先是 User.student_id
            if db.table("_default").contains(User.学号 == student_id):  # 适配 _default 嵌套结构
                db.table("_default").remove(User.学号 == student_id)  # 同步修改此处
                db.storage.flush()
                table.delete(item)
                status_label.config(text="数据删除成功！", foreground="green")
            else:
                status_label.config(text="未找到对应数据，删除失败！", foreground="red")
    except Exception as e:
        status_label.config(text=f"删除失败: {str(e)}", foreground="red")

# 修改数据函数
def edit_data():
    selected_item = table.selection()
    if not selected_item:
        status_label.config(text="请选择要修改的记录！", foreground="red")
        return

    item = selected_item[0]
    values = table.item(item, "values")
    student_id = int(values[1])  # 获取学号

    # 获取输入框中的新数据
    new_name = name_var.get()
    new_student_id = student_id_var.get()
    new_exempt_day = exempt_day_var.get()
    new_exempt_night = exempt_night_var.get()
    new_on_duty = on_duty_var.get()
    new_day_duty_count = day_duty_count_var.get()
    new_night_duty_count = night_duty_count_var.get()

    # 数据验证
    if not new_name or not new_student_id.isdigit():
        status_label.config(text="请输入有效的姓名和学号！", foreground="red")
        return

    # 检查学号是否重复（排除当前记录）
    if int(new_student_id) != student_id and db.table("_default").contains(User.学号 == int(new_student_id)):  # 适配 _default 嵌套结构
        status_label.config(text="学号已存在！", foreground="red")
        return

    # 更新数据库中的记录
    db.table("_default").update({  # 适配 _default 嵌套结构
        "姓名": new_name,
        "学号": int(new_student_id),
        "免白天岗状态": int(new_exempt_day),
        "免夜间岗状态": int(new_exempt_night),
        "站岗状态": new_on_duty,
        "站白天岗次数": int(new_day_duty_count),
        "站夜间岗次数": int(new_night_duty_count)
    }, User.学号 == student_id)
    db.storage.flush()  # 同步到文件

    # 更新表格中的记录
    table.item(item, values=(
        new_name,
        new_student_id,
        new_exempt_day,
        new_exempt_night,
        new_on_duty,
        new_day_duty_count,
        new_night_duty_count
    ))

    status_label.config(text="数据修改成功！", foreground="green")
    clear_inputs()

# 清空输入框
def clear_inputs():
    name_var.set("")
    student_id_var.set("")
    exempt_day_var.set("0")
    exempt_night_var.set("0")
    on_duty_var.set("是")
    day_duty_count_var.set("0")
    night_duty_count_var.set("0")

# 当选中表格中的记录时，将数据填充到输入框
def on_table_select(event):
    selected_item = table.selection()
    if not selected_item:
        return

    item = selected_item[0]
    values = table.item(item, "values")

    # 填充输入框
    name_var.set(values[0])
    student_id_var.set(values[1])
    exempt_day_var.set(values[2])
    exempt_night_var.set(values[3])
    on_duty_var.set(values[4])
    day_duty_count_var.set(values[5])
    night_duty_count_var.set(values[6])

# 导出数据到 Excel 文件
def export_to_excel():
    file_path = filedialog.asksaveasfilename(
        defaultextension=".xlsx",
        filetypes=[("Excel 文件", "*.xlsx")],
        title="选择导出路径"
    )
    if not file_path:
        status_label.config(text="导出取消！", foreground="red")
        return

    try:
        data = db.all()
        df = pd.DataFrame(data)
        # 修复问题：移除 encoding 参数
        df.to_excel(file_path, index=False)
        status_label.config(text="数据成功导出到 Excel！", foreground="green")
    except Exception as e:
        status_label.config(text=f"导出失败: {str(e)}", foreground="red")

# 从 Excel 文件导入数据
def import_from_excel():
    file_path = filedialog.askopenfilename(
        filetypes=[("Excel 文件", "*.xlsx")],
        title="选择要导入的 Excel 文件"
    )
    if not file_path:
        status_label.config(text="导入取消！", foreground="red")
        return

    try:
        df = pd.read_excel(file_path, dtype=str)
        db.truncate()  # 清空数据库
        for _, row in df.iterrows():
            db.insert({
                "姓名": row["姓名"],
                "学号": int(row["学号"]),
                "免白天岗状态": int(row["免白天岗状态"]),
                "免夜间岗状态": int(row["免夜间岗状态"]),
                "站岗状态": row["站岗状态"],
                "站白天岗次数": int(row["站白天岗次数"]),
                "站夜间岗次数": int(row["站夜间岗次数"])
            })
        db.storage.flush()  # 同步到文件
        update_table()
        status_label.config(text="数据成功从 Excel 导入！", foreground="green")
    except Exception as e:
        status_label.config(text=f"导入失败: {str(e)}", foreground="red")

# 界面布局
name_var = tk.StringVar()
student_id_var = tk.StringVar()
exempt_day_var = tk.StringVar(value="0")
exempt_night_var = tk.StringVar(value="0")
on_duty_var = tk.StringVar(value="是")
day_duty_count_var = tk.StringVar(value="0")
night_duty_count_var = tk.StringVar(value="0")

# 主容器框架
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill="both", expand=True)

# 数据预览区域
table_frame = ttk.Frame(main_frame)
table_frame.pack(fill="both", expand=True, pady=10)

columns = ("姓名", "学号", "免白天岗状态", "免夜间岗状态", "站岗状态", "站白天岗次数", "站夜间岗次数")
table = ttk.Treeview(table_frame, columns=columns, show="headings", height=8)

# 添加滑动条
scrollbar = ttk.Scrollbar(table_frame, orient="vertical", command=table.yview)
table.configure(yscrollcommand=scrollbar.set)
scrollbar.pack(side="right", fill="y")

for col in columns:
    table.heading(col, text=col)
    table.column(col, anchor="center", width=80)

table.pack(fill="both", expand=True)

# 绑定表格选择事件
table.bind("<<TreeviewSelect>>", on_table_select)

# 初始化表格数据
update_table()

# 输入框区域
input_frame = ttk.Frame(main_frame)
input_frame.pack(fill="x", pady=10)

ttk.Label(input_frame, text="姓名:").grid(row=0, column=0, padx=5, pady=5, sticky="e")
ttk.Entry(input_frame, textvariable=name_var).grid(row=0, column=1, padx=5, pady=5, sticky="w")

ttk.Label(input_frame, text="学号:").grid(row=1, column=0, padx=5, pady=5, sticky="e")
ttk.Entry(input_frame, textvariable=student_id_var).grid(row=1, column=1, padx=5, pady=5, sticky="w")

ttk.Label(input_frame, text="免白天岗状态:").grid(row=2, column=0, padx=5, pady=5, sticky="e")
ttk.Entry(input_frame, textvariable=exempt_day_var).grid(row=2, column=1, padx=5, pady=5, sticky="w")

ttk.Label(input_frame, text="免夜间岗状态:").grid(row=3, column=0, padx=5, pady=5, sticky="e")
ttk.Entry(input_frame, textvariable=exempt_night_var).grid(row=3, column=1, padx=5, pady=5, sticky="w")

ttk.Label(input_frame, text="站岗状态:").grid(row=4, column=0, padx=5, pady=5, sticky="e")
ttk.Combobox(input_frame, textvariable=on_duty_var, values=["是", "否"], state="readonly").grid(row=4, column=1, padx=5, pady=5, sticky="w")

ttk.Label(input_frame, text="站白天岗次数:").grid(row=5, column=0, padx=5, pady=5, sticky="e")
ttk.Entry(input_frame, textvariable=day_duty_count_var).grid(row=5, column=1, padx=5, pady=5, sticky="w")

ttk.Label(input_frame, text="站夜间岗次数:").grid(row=6, column=0, padx=5, pady=5, sticky="e")
ttk.Entry(input_frame, textvariable=night_duty_count_var).grid(row=6, column=1, padx=5, pady=5, sticky="w")

# 按钮区域
button_frame = ttk.Frame(main_frame)
button_frame.pack(fill="x", pady=10)

ttk.Button(button_frame, text="添加数据", command=add_data).pack(side="left", padx=10)
ttk.Button(button_frame, text="删除数据", command=delete_data).pack(side="left", padx=10)
ttk.Button(button_frame, text="修改数据", command=edit_data).pack(side="left", padx=10)
ttk.Button(button_frame, text="导出Excel", command=export_to_excel).pack(side="left", padx=10)
ttk.Button(button_frame, text="导入Excel", command=import_from_excel).pack(side="left", padx=10)

# 状态区域
status_frame = ttk.Frame(main_frame)
status_frame.pack(fill="x", pady=10)

status_label = ttk.Label(status_frame, text="")
status_label.pack()

# 居中窗口函数
def center_window(window, width, height):
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    x = (screen_width - width) // 2
    y = (screen_height - height) // 2
    window.geometry(f"{width}x{height}+{x}+{y}")

# 关于窗口函数
def show_about():
    about_window = tk.Toplevel(root)
    about_window.title("关于")
    about_window.resizable(False, False)

    # 设置窗口大小并居中
    window_width, window_height = 400, 200
    center_window(about_window, window_width, window_height)

    # 显示文本
    tk.Label(about_window, text="数据库管理软件 v1.0", font=("Arial", 14)).pack(pady=10)
    tk.Label(about_window, text="作者：埃及猪肉", font=("Arial", 12)).pack(pady=5)
    tk.Label(about_window, text="有什么Bug可以到作者的博客反馈哦", font=("Arial", 12)).pack(pady=5)

    # 超链接
    def open_url():
        webbrowser.open("https://pattianfang.github.io/")

    link = tk.Label(about_window, text="https://pattianfang.github.io/", font=("Arial", 12), fg="blue", cursor="hand2")
    link.pack(pady=5)
    link.bind("<Button-1>", lambda e: open_url())

    # 确定按钮
    ttk.Button(about_window, text="确定", command=about_window.destroy).pack(pady=0)

# 关于按钮
about_button = ttk.Button(root, text="关于", command=show_about)
about_button.pack(side="bottom", pady=0)

# 设置主窗口居中
center_window(root, 800, 600)

# 启动主循环
root.mainloop()
