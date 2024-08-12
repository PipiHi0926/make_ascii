"""
Description: A tool to convert images to ASCII art, allowing users to generate text-based art from images.
Author: 鄭永誠
"""

import gradio as gr
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2


def get_char(pixel_intensity, chars):
    """根據像素強度選擇相應的字符"""
    return chars[int(pixel_intensity / 256 * len(chars))]


def image_to_ascii(image, output_width, output_height, chars):
    # 轉換為PIL Image
    img = Image.fromarray(image)

    # 調整圖像大小
    img = img.resize((output_width, output_height))

    # 轉換為灰度圖
    img_gray = img.convert("L")

    # 應用自適應閾值以增強對比度
    img_array = np.array(img_gray)
    img_adaptive = cv2.adaptiveThreshold(
        img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )

    # 應用邊緣檢測
    img_edges = cv2.Canny(img_adaptive, 100, 200)

    # 組合增強的圖像
    img_enhanced = cv2.addWeighted(img_array, 0.7, img_edges, 0.3, 0)

    # 轉換為ASCII藝術
    ascii_art = []
    for y in range(output_height):
        line = []
        for x in range(output_width):
            pixel = img_enhanced[y, x]
            line.append(get_char(pixel, chars))
        ascii_art.append("".join(line))

    return "\n".join(ascii_art)


def process_image(image, width, height, char_set):
    if image is None:
        return "請上傳一張圖片。", None

    ascii_result = image_to_ascii(image, width, height, char_set)

    # 創建預覽圖像
    preview_img = Image.new("RGB", (width * 10, height * 20), color="white")
    d = ImageDraw.Draw(preview_img)
    font = ImageFont.truetype("fonts/consolai.ttf", 20)  # 請替換為實際的字體路徑

    lines = ascii_result.split("\n")
    for i, line in enumerate(lines):
        d.text((0, i * 20), line, fill=(0, 0, 0), font=font)

    preview_img = np.array(preview_img)

    return ascii_result, preview_img


# 創建Gradio界面
with gr.Blocks(theme=gr.themes.Soft()) as iface:
    gr.Markdown("# 圖像轉文字小幫手σ`∀´)σ Image to ASCII Art")
    gr.Markdown("上傳一張圖片，設置輸出尺寸和字符集，即可生成可複製的文字！")
    gr.Markdown(
        "Upload an image, set the output dimensions and character set, and generate ASCII art!"
    )

    with gr.Row():
        with gr.Column(scale=1):
            input_image = gr.Image(type="numpy", label="上傳圖片")
            width = gr.Slider(
                minimum=10, maximum=200, step=1, value=100, label="輸出寬度"
            )
            height = gr.Slider(
                minimum=10, maximum=200, step=1, value=100, label="輸出高度"
            )
            char_set = gr.Textbox(
                value=" .-:=+*#%@123abc", label="字符集（可包含符號、數字、英文）"
            )
            submit_btn = gr.Button("生成ASCII藝術")

        with gr.Column(scale=1):
            output_text = gr.Textbox(label="ASCII 藝術結果", lines=20)
            preview_image = gr.Image(label="效果預覽")

    submit_btn.click(
        process_image,
        inputs=[input_image, width, height, char_set],
        outputs=[output_text, preview_image],
    )


# 啟動Gradio應用
if __name__ == "__main__":
    iface.launch()
