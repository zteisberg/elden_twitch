from pymem.pattern import scan_pattern_page


def pattern_find_allocated(handle, pattern):
    base_address = 0x10000000000
    max_address = 0x2FFFFFFFFFF
    page_address = base_address
    found = None
    while page_address < max_address:
        next_page, found = scan_pattern_page(handle, page_address, pattern)

        if found:
            break

        page_address = next_page
    return found