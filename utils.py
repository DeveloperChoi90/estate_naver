def format_price(prc, rent_prc, trade_type):
    try:
        def to_korean_unit(val):
            val = int(val)
            if val == 0: return ""
            if val >= 10000:
                uk, man = val // 10000, val % 10000
                return f"{uk}억 {man:,}만" if man > 0 else f"{uk}억"
            return f"{val:,}만"
        if trade_type == "B2": return f"{to_korean_unit(prc)} / {to_korean_unit(rent_prc)}"
        return to_korean_unit(prc)
    except: return "가격 미정"
