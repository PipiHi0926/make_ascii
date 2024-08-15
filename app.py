from flask import Flask, render_template, request, jsonify
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import cv2
import base64
import io

app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024  # 限制上傳大小為 16MB


def get_char(pixel_intensity, chars):
    return chars[int(pixel_intensity / 256 * len(chars))]


def image_to_ascii(image, output_width, output_height, chars):
    img = Image.fromarray(image)
    img = img.resize((output_width, output_height))
    img_gray = img.convert("L")
    img_array = np.array(img_gray)
    img_adaptive = cv2.adaptiveThreshold(
        img_array, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 11, 2
    )
    img_edges = cv2.Canny(img_adaptive, 100, 200)
    img_enhanced = cv2.addWeighted(img_array, 0.7, img_edges, 0.3, 0)

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

    preview_img = Image.new("RGB", (width * 10, height * 20), color="white")
    d = ImageDraw.Draw(preview_img)
    font = ImageFont.truetype("fonts/consolai.ttf", 20)  # 請確保字體文件存在

    lines = ascii_result.split("\n")
    for i, line in enumerate(lines):
        d.text((0, i * 20), line, fill=(0, 0, 0), font=font)

    buffered = io.BytesIO()
    preview_img.save(buffered, format="PNG")
    preview_img_str = base64.b64encode(buffered.getvalue()).decode()

    return ascii_result, preview_img_str


@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        file = request.files["file"]
        width = int(request.form["width"])
        height = int(request.form["height"])
        char_set = request.form["char_set"]

        if file:
            image = Image.open(file.stream).convert("RGB")
            image_np = np.array(image)
            ascii_result, preview_img = process_image(image_np, width, height, char_set)
            return jsonify({"ascii_result": ascii_result, "preview_img": preview_img})

    return render_template("index.html")


if __name__ == "__main__":
    app.run(debug=True)
