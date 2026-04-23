from PIL import Image, ImageDraw, ImageFilter
import math

# --- 1. 设定图像参数 (高清 2048px) ---
WIDTH, HEIGHT = 2048, 2048
CENTER_X = WIDTH // 2
CENTER_Y = HEIGHT // 2
R_MAX = WIDTH // 2  # 这是地平线的半径，所有星星都在这个圆内

# 创建全黑画布
canvas = Image.new('RGB', (WIDTH, HEIGHT), color=(0, 0, 0))
draw = ImageDraw.Draw(canvas)

# --- 2. 定义星星数据 (你提供的) ---
stars_data = [
    {"hip": 11767, "mag": 1.97, "alt": 40.61, "az": 359.89, "name": "Polaris"},
    {"hip": 15863, "mag": 1.79, "alt": 79.91, "az": 351.64, "name": "Alpha Ari"},
    {"hip": 21421, "mag": 0.87, "alt": 62.96, "az": 145.60, "name": "Aldebaran"},
    {"hip": 24436, "mag": 0.18, "alt": 36.53, "az": 148.45, "name": "Rigel"},
]

# --- 3. 核心函数：天体坐标 -> 图像像素坐标 (Stereographic Projection) ---
def sky_to_pixel(alt_deg, az_deg):
    """
    将仰角和方位角转换为图像上的 (x, y) 坐标。
    天顶 (alt=90) 在中心。地平线 (alt=0) 在 R_MAX 圆周。
    """
    # 将角度转换为弧度
    alt_rad = math.radians(alt_deg)
    # Skyfield 的方位角 0 是北，90 是东。数学中 0 是东，90 是北。
    # 我们需要顺时针旋转，且北在上方。
    az_rad = math.radians(az_deg - 180) 

    # 计算星星离天顶的角度 (Zenith Distance)
    # z = 90° - 仰角。
    z_rad = (math.pi / 2) - alt_rad

    # 立体投影公式: r = 2 * R_MAX * tan(z/2)
    # 这个公式可以无失真地投影到地平线（z=90°）
    r = 2 * R_MAX * math.tan(z_rad / 2) / 2 # 除以2是为了防止 tan(90/2) 时r溢出画布

    # 转换为笛卡尔坐标 (x, y)
    # 在这个投影里：北是 -y 方向，东是 +x 方向
    x_pixel = CENTER_X + r * math.sin(az_rad)
    y_pixel = CENTER_Y + r * math.cos(az_rad)

    return int(x_pixel), int(y_pixel)

# --- 4. 绘图循环 ---
print("开始在 Pillow 画布上绘制星星...")

for star in stars_data:
    # 1. 转换坐标
    x, y = sky_to_pixel(star["alt"], star["az"])
    
    # 2. 根据星等计算大小 (半径)
    # 星等越小（越亮），半径越大。
    # 比如：Rigel (0.18) -> 约 10px, Polaris (1.97) -> 约 6px
    radius = max(2, int((5 - star["mag"]) * 2))
    
    # 3. 绘制实心白圆
    draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                 fill=(255, 255, 255))
    
    print(f"绘制 HIP {star['hip']} ({star['name']}) -> 像素: ({x}, {y}), 半径: {radius}")

# --- 5. 进阶：加一点模糊处理，增加真实感 (Glow) ---
print("添加高斯模糊，模拟星光晕影...")
# 复制一份作为底层
blur_layer = canvas.filter(ImageFilter.GaussianBlur(radius=3))
# 上面两行叠加有点复杂，简单点：我们直接给原图加一个细微模糊
canvas = canvas.filter(ImageFilter.GaussianBlur(radius=0.7))

# --- 6. 保存并预览 ---
output_file = "haitian_four_stars.png"
canvas.save(output_file)
print(f"成功保存星图为: {output_file}")
canvas.show() # 在 MacBook 上弹窗预览