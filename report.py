import os
import sys

# ===== 自動檢查並安裝 Pillow =====
try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("Pillow 未安裝，正在安裝...")
    os.system(f'{sys.executable} -m pip install pillow')
    from PIL import Image, ImageDraw, ImageFont

from tkinter import Tk, Label, Button, Entry, filedialog, StringVar, Scale, HORIZONTAL, OptionMenu, colorchooser

# ===== 主介面 =====
root = Tk()
root.title("圖片批量添加水印工具")
root.geometry("450x500")

# ===== 功能函式 =====
def select_folder():
    folder = filedialog.askdirectory(title="選擇圖片資料夾")
    if folder:
        folder_var.set(folder)

def select_font():
    font_path = filedialog.askopenfilename(filetypes=[("TrueType Font", "*.ttf")])
    if font_path:
        font_var.set(font_path)

def choose_color():
    color_code = colorchooser.askcolor(title="選擇水印顏色")
    if color_code[1]:
        color_var.set(color_code[1])
        color_label.config(bg=color_code[1])

def add_watermark():
    folder = folder_var.get()
    font_path = font_var.get()
    text = text_var.get()
    position = position_var.get()
    opacity = opacity_var.get()
    font_size = font_size_var.get()
    color = color_var.get()

    if not folder or not os.path.isdir(folder):
        status_var.set("⚠️ 請選擇有效的圖片資料夾")
        return
    if not font_path or not os.path.isfile(font_path):
        status_var.set("⚠️ 請選擇字體檔 (.ttf)")
        return
    if not text.strip():
        status_var.set("⚠️ 請輸入水印文字")
        return

    output_folder = os.path.join(folder, "watermarked")
    os.makedirs(output_folder, exist_ok=True)

    font = ImageFont.truetype(font_path, font_size)
    count = 0

    for filename in os.listdir(folder):
        if filename.lower().endswith((".jpg", ".jpeg", ".png")):
            img_path = os.path.join(folder, filename)
            try:
                img = Image.open(img_path).convert("RGBA")
                txt_layer = Image.new("RGBA", img.size, (255, 255, 255, 0))
                draw = ImageDraw.Draw(txt_layer)

                bbox = draw.textbbox((0, 0), text, font=font)
                text_w = bbox[2] - bbox[0]
                text_h = bbox[3] - bbox[1]
                margin = 20

                if position == "右下":
                    pos = (img.width - text_w - margin, img.height - text_h - margin)
                elif position == "右上":
                    pos = (img.width - text_w - margin, margin)
                elif position == "左下":
                    pos = (margin, img.height - text_h - margin)
                elif position == "左上":
                    pos = (margin, margin)
                else:  # 中央
                    pos = ((img.width - text_w) // 2, (img.height - text_h) // 2)

                # 轉換顏色字串為 RGBA
                r, g, b = root.winfo_rgb(color)
                r = r >> 8
                g = g >> 8
                b = b >> 8
                draw.text(pos, text, fill=(r, g, b, opacity), font=font)

                watermarked = Image.alpha_composite(img, txt_layer)
                watermarked.convert("RGB").save(os.path.join(output_folder, filename))
                count += 1
            except Exception as e:
                print(f"❌ {filename} 處理失敗：{e}")

    status_var.set(f"✅ 已完成 {count} 張圖片，輸出於：{output_folder}")

# ===== GUI 元件 =====
folder_var = StringVar()
font_var = StringVar()
text_var = StringVar()
position_var = StringVar(value="右下")
status_var = StringVar()
font_size_var = Scale(root, from_=10, to=200, orient=HORIZONTAL)
opacity_var = Scale(root, from_=0, to=255, orient=HORIZONTAL)
color_var = StringVar(value="#FFFFFF")

Label(root, text="圖片資料夾：").pack()
Button(root, text="選擇資料夾", command=select_folder).pack()
Label(root, textvariable=folder_var, wraplength=400, fg="gray").pack()

Label(root, text="字體檔 (.ttf)：").pack()
Button(root, text="選擇字體", command=select_font).pack()
Label(root, textvariable=font_var, wraplength=400, fg="gray").pack()

Label(root, text="水印文字：").pack()
Entry(root, textvariable=text_var, width=40).pack()

Label(root, text="水印位置：").pack()
OptionMenu(root, position_var, "右下", "右上", "左下", "左上", "中央").pack()

Label(root, text="水印字體大小：").pack()
font_size_var.set(40)
font_size_var.pack()

Label(root, text="透明度 (0~255)：").pack()
opacity_var.set(150)
opacity_var.pack()

Label(root, text="水印顏色：").pack()
Button(root, text="選擇顏色", command=choose_color).pack()
color_label = Label(root, text="          ", bg=color_var.get())
color_label.pack(pady=5)

Button(root, text="生成水印圖片", command=add_watermark, bg="#4CAF50", fg="white").pack(pady=10)

Label(root, textvariable=status_var, fg="blue", wraplength=400).pack()

root.mainloop()

