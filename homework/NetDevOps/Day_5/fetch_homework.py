#!/usr/bin/env python3
from pathlib import Path
import requests
import json
import getpass
from bs4 import BeautifulSoup
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams


# 指定中文字体文件路径
rcParams['font.sans-serif'] = ['Noto Sans CJK JP']
# 解决坐标轴负号显示问题
rcParams['axes.unicode_minus'] = False
BASE_DIR = Path(__file__).parent


class HomeworkFetcher:
    def __init__(self, base_url, cookies_file=None):
        self.base_url = base_url
        self.login_url = f"{base_url}/accounts/login/"
        self.sess = requests.Session()
        self.headers = {"User-Agent": "Mozilla/5.0"}

        # cookies 文件路径，默认放在当前脚本目录
        self.cookies_file = Path(
            cookies_file) if cookies_file else BASE_DIR / ".session_cookies.json"

    # ------------------ Cookie 方法 ------------------
    def load_cookies(self):
        if not self.cookies_file.exists():
            return False
        try:
            with self.cookies_file.open("r", encoding="utf-8") as f:
                cookies = json.load(f)
            self.sess.cookies.update(cookies)
            return True
        except Exception:
            return False

    def save_cookies(self):
        try:
            with self.cookies_file.open("w", encoding="utf-8") as f:
                json.dump(self.sess.cookies.get_dict(), f)
            # 设置文件权限为 600
            try:
                self.cookies_file.chmod(0o600)
            except Exception:
                pass
        except Exception as e:
            print("保存 cookies 失败:", e)

    # ------------------ 登录状态检查 ------------------
    def is_cookie_valid(self):
        try:
            r = self.sess.get(self.login_url, headers=self.headers, timeout=10)
            return '乾頤堂Python强化班系统' in r.text
        except Exception:
            return False

    # ------------------ 获取 CSRF token ------------------
    def fetch_csrf(self):
        try:
            r = self.sess.get(self.base_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            for name in ["csrfmiddlewaretoken", "_csrf", "csrf_token", "csrf"]:
                inp = soup.find("input", {"name": name})
                if inp and inp.get("value"):
                    return {name: inp.get("value")}
            meta = soup.find("meta", {"name": "csrf-token"})
            if meta and meta.get("content"):
                return {"csrf-token": meta.get("content")}
        except Exception:
            pass
        return {}

    # ------------------ 登录方法 ------------------
    def login(self, username=None, password=None):
        from urllib.parse import urljoin
        if not username:
            username = input("用户名: ").strip()
        if not password:
            password = getpass.getpass("密码 (不会回显): ")

        data = {"username": username, "password": password}
        data.update(self.fetch_csrf())

        r = self.sess.post(self.login_url, data=data,
                           headers={**self.headers, "Referer": self.base_url},
                           allow_redirects=True, timeout=10)
        if self.is_cookie_valid():
            self.save_cookies()
            print("[+] 登录成功，cookie 已保存")
            return True
        print("[-] 登录失败，请检查用户名/密码或可能需要额外验证")
        return False

    # ------------------ 抓取并解析表格 ------------------
    def fetch_homework(self, target_url):
        try:
            r = self.sess.get(target_url, headers=self.headers, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            table = soup.find("table", {"id": "table-for-student"})
            if not table:
                print("[-] 找不到表格，可能未登录或页面结构变了")
                return None
            headers = [th.get_text(strip=True)
                       for th in table.find("thead").find_all("th")]
            rows = [
                [td.get_text(strip=True) for td in tr.find_all("td")]
                for tr in table.find("tbody").find_all("tr")
            ]
            df = pd.DataFrame(rows, columns=headers[:len(rows[0])])
            out_csv = BASE_DIR / "homework.csv"
            df.to_csv(out_csv, index=False, encoding="utf-8-sig")
            print(f"[+] 表格已保存为 {out_csv}")
            return df
        except Exception as e:
            print("抓取失败:", e)
            return None


def draw_pie(labels, sizes, title="饼图", figsize=(7, 5), shadow=False, colors=None):

    plt.figure(figsize=figsize)
    wedges, texts, autotexts = plt.pie(
        sizes,
        labels=labels,
        autopct="%1.1f%%",
        startangle=90,
        shadow=shadow,
        colors=colors
    )

    plt.title(title, pad=30)

    plt.legend(
        wedges, labels,
        loc="upper right",
    )

    plt.axis("equal")
    plt.tight_layout()
    file = BASE_DIR / f"{title}.png"
    plt.savefig(file, dpi=200)


if __name__ == "__main__":
    BASE = "https://qytsystem.qytang.com"
    TARGET_URL = f"{BASE}/python_enhance/python_enhance_homework"

    fetcher = HomeworkFetcher(BASE)

    # 尝试加载已有 cookie
    if not fetcher.load_cookies() or not fetcher.is_cookie_valid():
        print("[*] cookie 无效或不存在，开始登录...")
        if not fetcher.login():
            exit(1)

    # 抓取表格
    df = fetcher.fetch_homework(TARGET_URL)
    if df is not None:
        print(df.head())

    # 按成绩统计
    grade_counts = df["成绩"].value_counts()
    print("按成绩统计：")
    print(grade_counts)
    print(grade_counts.index)
    draw_pie(grade_counts.index, grade_counts, title="课程分数分布图")
    # 按课程统计
    course_counts = df["课程"].value_counts()
    print("\n按课程统计：")
    print(course_counts)
    print(course_counts.index)
    draw_pie(course_counts.index, course_counts, title="课程作业分布图")
