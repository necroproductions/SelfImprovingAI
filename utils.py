# utils.py: Pure Python unified diff applier
import re

_hdr_pat = re.compile("^@@ -(\\d+),?(\\d+)? \\+(\\d+),?(\\d+)? @@$")
_no_eol = "\\ No newline at end of file"

def apply_patch(s, patch, revert=False):
    """
    Apply unified diff patch to string s to recover newer string.
    If revert is True, treat s as the newer string, recover older string.
    """
    s = s.splitlines(True)
    p = patch.splitlines(True)
    t = ''
    i = sl = 0
    (midx, sign) = (1, '+') if not revert else (3, '-')
    while i < len(p) and p[i].startswith(("---", "+++")): 
        i += 1  # skip header lines
    while i < len(p):
        m = _hdr_pat.match(p[i])
        if not m: 
            raise Exception("Cannot process diff")
        i += 1
        l = int(m.group(midx)) - 1 + (m.group(midx + 1) == '0')
        t += ''.join(s[sl:l])
        sl = l
        while i < len(p) and p[i][0] != '@':
            if i + 1 < len(p) and p[i + 1][0] == '\\': 
                line = p[i][:-1]; 
                i += 2
            else: 
                line = p[i]; 
                i += 1
            if len(line) > 0:
                if line[0] == sign or line[0] == ' ': 
                    t += line[1:]
                sl += (line[0] != sign)
    t += ''.join(s[sl:])
    return t

# Test (comment out for production)
if __name__ == "__main__":
    original = "line1\nline2\nline3\n"
    patch = "--- original\n+++ modified\n@@ -1,3 +1,3 @@\n line1\n-line2\n+new line2\n line3\n"
    print(apply_patch(original, patch))