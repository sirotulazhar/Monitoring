def format_rupiah(value):
    if value >= 1_000_000_000_000:  
        return f"{value/1_000_000_000_000:,.1f} T"
    elif value >= 1_000_000_000:  
        return f"{value/1_000_000_000:,.1f} M"
    elif value >= 1_000_000:  
        return f"{value/1_000_000:,.1f} Jt"
    elif value >= 1_000:
            return f"{value/1_000:.1f} K"
    else:
        return f"{value:,.0f}"

def format_angka(value):
    return f"{int(value):,}".replace(",", ".")
