from skyfield.api import Star, load, Topos
from skyfield.data import hipparcos

# 1. 加载数据
planets = load('de421.bsp')
with load.open(hipparcos.URL) as f:
    df = hipparcos.load_dataframe(f)

# 2. 筛选亮星（星等 magnitude 小于 2.0 的恒星）
bright_stars = df[df['magnitude'] <= 2.0]

# 3. 设置观测点
earth = planets['earth']
haidian = earth + Topos('39.9916 N', '116.3133 E')
ts = load.timescale()
t = ts.now()

print(f"--- 海淀区当前可见亮星 ---")
for hip_id, row in bright_stars.iterrows():
    star = Star.from_dataframe(row)
    pos = haidian.at(t).observe(star)
    alt, az, d = pos.apparent().altaz()
    
    if alt.degrees > 0: # 只打印地平线以上的
        print(f"HIP {hip_id}: 亮度 {row['magnitude']} | 仰角 {alt.degrees:.2f}° | 方位 {az.degrees:.2f}°")