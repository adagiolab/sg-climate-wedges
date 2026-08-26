def get_sector_polynomial(capacities: list[int]) -> list[int]:
    max_w = sum(capacities)
    dp = [0] * (max_w + 1)
    dp[0] = 1
    for cap in capacities:
        next_dp = [0] * (max_w + 1)
        for w in range(max_w + 1):
            if dp[w] > 0:
                for k in range(cap + 1):
                    if w + k <= max_w:
                        next_dp[w + k] += dp[w]
        dp = next_dp
    return dp  # returns [C_s(0), C_s(1), C_s(2), ...]


# 1. Define strategy capacities per sector for Singapore
singapore_sectors = {
    "Power": [19, 13, 1, 1, 19, 18, 4, 19], 
    "Industry": [1, 20], 
    "Transport": [1, 1, 1, 1], 
    "Buildings": [1, 1], 
}

# 2. Build Sector Tables
sector_tables = {
    sec: get_sector_polynomial(caps) for sec, caps in singapore_sectors.items()
}

# 3. Convolve across sectors to get economy-wide total
economy_dp = [1]
for sec, table in sector_tables.items():
    new_len = len(economy_dp) + len(table) - 1
    next_dp = [0] * new_len
    for i, a in enumerate(economy_dp):
        for j, b in enumerate(table):
            next_dp[i + j] += a * b
    economy_dp = next_dp

# Total combinations
target_wedges = 31
print(f"Total possible pathways for Singapore: {economy_dp[target_wedges]}")
