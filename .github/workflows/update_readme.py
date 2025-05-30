import sys
from pathlib import Path
import re
from collections import namedtuple
import urllib
import urllib.parse


changed_dir = set(Path(x).parent for x in sys.argv[1].split(", ") if Path(x).suffix == ".ass")


for dir in changed_dir:
    table = []
    Episode = namedtuple("Episode", ["ep", "ep_title", "chs", "cht"])
    for file in dir.iterdir():
        m = re.search(r"- (?P<ep>\d{2})\.chs\.ass", file.name)
        if m:
            ep = m["ep"]
            # parse ass file, find ep_title
            with open(file) as f:
                content = f.read()
                m = re.search(r"(Dialogue|Comment): (\d+,\d+:\d{2}:\d{2}\.\d{2},\d+:\d{2}:\d{2}\.\d{2},[^,]*,ep_title,\d+,\d+,\d+,[^,]*,(?P<ep_title>.*\n))", content)
                ep_title = m["ep_title"].strip("\n") if m else ""
                ep_title = re.sub(r"\{[^\}]*\}", "", ep_title)
            fname = re.search(r"(Archive/.*).chs.ass", str(file))
            if not fname:
                exit()
            fname = urllib.parse.quote(fname[1])

            # generate ep_title and link
            table.append(Episode(ep, ep_title, f"https://raw.githubusercontent.com/SweetSub/SweetSub/master/{fname}.chs.ass",f"https://raw.githubusercontent.com/SweetSub/SweetSub/master/{fname}.cht.ass" if Path(str(file).replace(".chs", ".cht")).exists() else "N/A"))
            table.sort(key=lambda x:x.ep)

    # make it a string
    table_content = []
    for e in table:
        table_content.append(f"| {e.ep} | {e.ep_title} | [简体]({e.chs}) | " + (f"[繁体]({e.cht}) |" if e.cht != "N/A" else "N/A"))


    table_str = "<auto-generated-table>\n\n| 集数 | 标题 | 简体 | 繁体 |\n| - | - | - | - |\n" + \
        "\n".join(table_content) + \
        "\n\n</auto-generated-table>"

    readmefile = dir.joinpath("README.md")

    if not readmefile.exists():
        with open(readmefile, "w", encoding="utf-8") as f:
            f.write(table_str)

    else:
        with open(readmefile, "r+", encoding="utf-8") as f:
            readme_content = f.read()
            # print(f"readme before re.sub\n{readme_content=}")
            readme_content = re.sub(r"<auto-generated-table>.*</auto-generated-table>", table_str, readme_content, flags=re.S)
            # print(f"readme after re.sub\n{readme_content=}")
            f.seek(0)
            f.write(readme_content)
            f.truncate()
            




