import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


class ShapeCalculator:
    def __init__(self, size, channels=1):
        self.size = size              # اندازه ورودی (مربعی)
        self.channels = channels
        self.layers = []              # (kind, name, kernel, stride, pad, filters)

    def conv(self, name, kernel, stride=1, pad="valid", filters=1):
        self.layers.append(("conv", name, kernel, stride, pad, filters))
        return self

    def pool(self, name, kernel, stride=None, pad="valid"):
        self.layers.append(("pool", name, kernel, stride or kernel, pad, None))
        return self

    def bn(self, name="BN"):
        """BatchNormalization: اندازه و تعداد کانال را تغییر نمی‌دهد."""
        self.layers.append(("bn", name, None, None, None, None))
        return self

    @staticmethod
    def out(w, kernel, stride, pad):
        if pad == "same":
            return -(-w // stride)    # ceil(w / stride)
        p = 0 if pad == "valid" else pad
        return (w - kernel + 2 * p) // stride + 1

    def _trace(self, size=None):
        """لیست (name, kind, w, c) برای هر لایه؛ در اولین خطا متوقف می‌شود."""
        w = size or self.size
        c = self.channels
        rows = [("input", "input", w, c)]
        for kind, name, kernel, stride, pad, filters in self.layers:
            if kind != "bn":
                w = self.out(w, kernel, stride, pad)
                if kind == "conv":
                    c = filters
            rows.append((name, kind, w, c))
            if w <= 0:
                break
        return rows

    def run(self, size=None):
        rows = self._trace(size)
        for name, kind, w, c in rows:
            if w <= 0:
                print(f"{name:<7} -> {w}x{w}x{c}  ERROR")
                return
            print(f"{name:<7} -> {w}x{w}x{c}")
        print("flatten ->", w * w * c)

    def plot(self, size=None):
        rows = self._trace(size)
        error = rows.pop() if rows[-1][2] <= 0 else None   # لایه خطادار رسم نمی‌شود

        colors = {"input": "#B4B2A9", "conv": "#5DCAA5",
                  "pool": "#F0997B", "bn": "#AFA9EC"}
        n = len(rows)
        max_w = max(r[2] for r in rows)
        max_c = max(r[3] for r in rows)

        fig, ax = plt.subplots(figsize=(10, 0.55 * (n + 2)))
        for i, (name, kind, w, c) in enumerate(rows):
            col = colors[kind]
            ax.text(0, i, name, va="center", fontsize=11)

            s = 0.7 * w / max_w                                # مربع = اندازه مکانی
            ax.add_patch(Rectangle((3 - s / 2, i - s / 2), s, s,
                                   color=col, ec="k", lw=0.5))
            ax.text(4, i, f"{w}×{w}×{c}", va="center", fontsize=10)

            L = 5 * c / max_c                                  # میله = تعداد کانال
            ax.add_patch(Rectangle((6.5, i - 0.2), L, 0.4,
                                   color=col, ec="k", lw=0.5))
            ax.text(6.5 + L + 0.15, i, str(c), va="center", fontsize=10)

        if error:
            ax.text(0, n, f"{error[0]}: ERROR (size {error[2]})",
                    va="center", color="red", fontsize=11)
            title = f"input {size or self.size}: error at {error[0]}"
        else:
            _, _, w, c = rows[-1]
            ax.text(0, n, "flatten", va="center", fontsize=11)
            ax.text(4, n, f"{w}×{w}×{c} = {w * w * c}", va="center", fontsize=10)
            title = f"input {size or self.size}"

        ax.set_title(title)
        ax.set_xlim(0, 13)
        ax.set_ylim(n + 0.5, -0.8)       # ردیف اول بالا باشد
        ax.axis("off")
        plt.show()

    def min_input(self):
        for n in range(1, 3000):
            w = n
            for kind, _, kernel, stride, pad, _ in self.layers:
                if kind == "bn":
                    continue
                w = self.out(w, kernel, stride, pad)
                if w <= 0:
                    break
            else:
                return n