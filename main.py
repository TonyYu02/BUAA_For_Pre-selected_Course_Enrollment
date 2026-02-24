import os
import time
import requests
from bs4 import BeautifulSoup
from tabulate import tabulate

authen = {
    'username': '',
    'password': '',
}
xueqi="20252"
#这里填写学期，如20252：2025-2026学年第2学期

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36'
}

session = requests.Session()

def get_web(url):
	try:
		page =session.get(url, headers=headers, timeout=10)
		return page
	except requests.exceptions.Timeout:
		print("界面超时，请重试。")
		exit(0)

login_page = get_web("https://sso.buaa.edu.cn/login?service=https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/*default/index.do")
soup = BeautifulSoup(login_page.text, 'html.parser')
execution_input = soup.find('input', {'name': 'execution'})
execution_value = execution_input.get('value', '')

login_data = {
    'username': authen['username'],
    'password': authen['password'],
    'type': 'username_password',
    'submit': 'LOGIN',
    '_eventId': 'submit',
    'execution':execution_value
}

response = session.post("https://sso.buaa.edu.cn/login", data=login_data)

def query():
    yx_url = "https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/xsxkCourse/loadKbxx.do?sfyx=1&sfjzsyzz=1&_="
    timestamp = int(time.time() * 1000)
    yx_url = yx_url + str(timestamp)
    response = get_web(yx_url)
    yx = response.json()

    bjdm = []
    yxk = {}
    wids = {}
    for nr in yx["xkjgList"]:
        if nr["BJDM"] not in set(bjdm) and "MXMK" not in nr["BJDM"] and nr['XNXQDM']==xueqi:
            bjdm.append(nr["BJDM"])
            yxk[nr["BJDM"]] = nr["YYZ"]
            wids[nr["BJDM"]] = nr["WID"]
    base_url = "https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/xsxkCourse/loadAllCourseInfo.do?"
    timestamp = int(time.time() * 1000)
    new_url = base_url + "_=" + str(timestamp) + "&pageSize=8000"

    course = get_web(new_url)
    courses = course.json()

    bjdm_set = set(bjdm)

    head = ["编号","课程名称", "授课教师", "学分", "线下容量", "线上容量", "已选", "意愿值"]
    cours = []
    bhdic={}
    i = 1
    for course in courses["datas"]:
        if course["BJDM"] in bjdm_set:
            cours.append(
                [i, course['KCMC'], course['RKJS'], course['KCXF'], course['KXRS'], course['XSRL'], course['YXXKJGRS'],
                 yxk[course["BJDM"]]])
            bhdic[i]= wids[course["BJDM"]]
            i=i+1
    print(tabulate(cours, head, tablefmt="fancy_grid"))
    return bhdic


def loop(bhdic):
    a = int(input("按1刷新，按2修改对应意愿值，其余键退出："))
    if a == 1:
        os.system('cls')
        k = query()
        loop(k)
    elif a == 2:
        i = int(input("修改意愿值，请输入已选课程编号："))
        j= int(input("修改后的值为："))
        xg="https://yjsxk.buaa.edu.cn/yjsxkapp/sys/xsxkappbuaa/xsxkYxxk/changeYyz.do?_="
        timestamp = int(time.time() * 1000)
        xg=xg+str(timestamp)
        xg_data={
            "wid" : bhdic[i],
            "yyz" : j
        }
        r= session.post(xg, data=xg_data)
        rj=r.json()
        print(rj["code"])
        os.system('cls')
        if rj["code"] == 1:
            print("修改成功。")
        else:
            print(rj["msg"])
        k = query()
        loop(k)

    else:
        session.close()
        exit(0)

if __name__ == "__main__":
	k = query()
	loop(k)


