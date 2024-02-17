from io import BytesIO

import matplotlib.pyplot as plt

COLORS = {
    0: "gray",  # awake
    1: "royalblue", # light sleep
    2: "darkblue", # deep sleep
    3: "lightsteelblue",  # REM
}

HEIGHTS = {
    0: 4,
    3: 3,
    1: 2,
    2: 1,
}


def make_sleep_chart(data) -> BytesIO:
    # plt.xkcd()
    # Use just this font so we don't see warnings about the other funny fonts not being found.
    # plt.rcParams["font.family"] = "xkcd script"

    fig, ax = plt.subplots()

    # https://stackoverflow.com/questions/70477458/how-can-i-plot-bar-plots-with-variable-widths-but-without-gaps-in-python-and-ad
    #  {
    #     "startdate": 1708065900,
    #     "state": 0,
    #     "enddate": 1708066020,
    #     "model": "Aura Sensor V2",
    #     "hr": {"1708065900": 60, "1708065960": 82},
    #     "rr": {"1708065900": 16, "1708065960": 18},
    #     "snoring": {"1708065900": 0, "1708065960": 0},
    #     "hash_deviceid": "38a4a1ed23ecb6a607e3b58a07f2fda9dcd29791",
    #     "model_id": 63,
    # },
    x = []
    y = []
    w = []
    color = []
    for blob in data["body"]["series"]:
        startdate = blob["startdate"]
        enddate = blob["enddate"]
        state = blob["state"]
        x.append((startdate + enddate) / 2)
        y.append(HEIGHTS[state])
        w.append(enddate - startdate)
        color.append(COLORS[state])

    # fruits = ["apple", "blueberry", "cherry", "orange"]
    # counts = [40, 100, 30, 55]
    # bar_labels = ["red", "blue", "_red", "orange"]
    # bar_colors = ["tab:red", "tab:blue", "tab:red", "tab:orange"]

    ax.bar(x=x, height=y, width=w, color=color)

    # ax.set_ylabel("fruit supply")
    # ax.set_title("Fruit supply by kind and color")
    # ax.legend(title="Fruit color")

    outf = BytesIO()
    plt.savefig(outf)
    return outf
