blacklist = [".svg", ".tps", "ali-logo", "favicon", "icon-"]
src = "https://img.alicdn.com/imgextra/i3/O1CN01PHILNA1s1rTTkaOyp_!!6000000005707-55-tps-18-18.svg"
print(f"Testing: {src}")
print(f"Match .svg: {'.svg' in src.lower()}")
print(f"Match .tps: {'.tps' in src.lower()}")
print(f"Any match: {any(black in src.lower() for black in blacklist)}")
