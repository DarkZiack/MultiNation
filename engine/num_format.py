def abbreviate_number(num):
    suffixes = [
        "", "k", "M", "B", "T", "Qa", "Qt", "Sx", "Sp", "Oc", "No",
        "Dc", "Ud", "Dd", "Td", "QaD", "QiD", "SxD", "SpD", "OcD", "NoD",
        "Vg", "Uv", "Dv", "Tv", "QaV", "QiV", "SxV", "SpV", "OcV", "NoV",
        "Tg", "Utg", "Dtg", "Ttg", "QaTg", "QiTg", "SxTg", "SpTg", "OcTg", "NoTg",
        "Qq", "Uq", "Dq", "Tq", "QaQq", "QiQq", "SxQq", "SpQq", "OcQq", "NoQq",
        "Sg", "Us", "Ds", "Ts", "QaSg", "QiSg", "SxSg", "SpSg", "OcSg", "NoSg",
        "Cg", "Uc"
    ]

    magnitude = 0
    while abs(num) >= 1000 and magnitude < len(suffixes) - 1:
        num /= 1000.0
        magnitude += 1

    return f"{num:.1f}{suffixes[magnitude]}" if num % 1 else f"{int(num)}{suffixes[magnitude]}"