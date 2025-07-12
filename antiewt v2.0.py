import logging
import time

from selenium import webdriver
from selenium.common.exceptions import JavascriptException, TimeoutException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options


#输入用户的账户名称和密码

USER = ""
PASS = ""


def switch_to_new_window(driver):
    """切换到最新打开的窗口"""
    new_handle = driver.window_handles[-1]
    logging.info(f"切换到新页面: {new_handle}")
    driver.switch_to.window(new_handle)

def print_all_elements(driver):
        """打印页面所有元素的标签名和属性"""
        elements = driver.find_elements(By.CSS_SELECTOR, "div.tabs-2kE4L > ul > li")
        for elem in elements:
            try:
                print(f"标签: {elem.tag_name}, 属性: {elem.get_attribute('outerHTML')[:100]}...")
            except Exception:
                continue
        
def get_all_progress(driver):
    """等待并获取总完成度文本"""
    try:
        re=[]
        progress_element = driver.find_elements(By.CSS_SELECTOR, "div.tabs-2kE4L > ul > li")
        for i in progress_element:
            if(i.get_attribute("data-active")!="true" and i.get_attribute("data-active")!="false"):
                continue
            re.append({"element":i,"process":i.find_elements(By.TAG_NAME, "span")[1].text})
        return re
    except TimeoutException:
        logging.error("获取完成度超时")
        return ""

def login(driver):
    """完成登录操作"""
    logging.info("尝试登录...")
    user_field = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "login__password_userName"))
    )
    user_field.send_keys(USER)
    pass_field = driver.find_element(By.ID, "login__password_password")
    pass_field.send_keys(PASS)
    sub_btn = driver.find_element(By.CLASS_NAME, "ant-btn-primary")
    sub_btn.click()

def navigate_to_vacation(driver):
    """点击‘我的假期’后关闭当前窗口，并切换到新窗口"""
    vacation_link = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.LINK_TEXT, "开始学习"))
    )
    vacation_link.click()
    driver.close()
    switch_to_new_window(driver)

def click_primary_button(driver):
    """等待并点击页面上的主要按钮"""
    primary_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "ant-btn.ant-btn-link"))
    )
    primary_btn.click()
    switch_to_new_window(driver)

def wait_for_video_completion(driver,lesson_name, action_chains):
    """处理视频播放，直至视频播放完毕"""
    # 设置播放速度和静音
    driver.execute_script('function updateVariable(){document.querySelector("video").playbackRate = 2;setTimeout(updateVariable, 0);};updateVariable();')
    driver.execute_script('document.querySelector("video").muted = true')
    try:
        play_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "vjs-big-play-button"))
        )
        play_btn.click()
    except TimeoutException:
        logging.error("找不到播放按钮")
    video = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.TAG_NAME, "video"))
    )
    while True:
        # 挂机检测部分
        for cls in ["btn-3LStS"]:
            elements = driver.find_elements(By.CLASS_NAME, cls)
            if elements:
                action_chains.click(elements[0]).perform()
                logging.info(f"处理 {cls} 检测")
        # 获取视频进度
        try:
            current_time = float(video.get_attribute("currentTime"))
            duration = float(video.get_attribute("duration"))
        except Exception as e:
            logging.error("读取视频属性失败")
            break
        logging.info(f"视频进度: {current_time}/{duration}")
        time.sleep(5)
        if current_time >= duration:
            logging.info(f"{lesson_name} | 已完成")
            driver.close()
            switch_to_new_window(driver)
            break

def process_lessons(driver, action_chains):
    """处理当前课程中的所有视频/学习任务"""
    process = {}
    lesson_name = ""
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ant-spin-container"))
        )
        lesson_container = container.find_element(By.XPATH, "./*")
        lesson_list = lesson_container.find_elements(By.XPATH, "./*")[1].find_elements(By.TAG_NAME, "li")
    except Exception as e:
        logging.error("获取课程列表失败")
        return
    for i in lesson_list:
        temp = i.find_elements(By.CLASS_NAME,"status-2gqgg > span")
        if(temp[0].text == "已完成"):
            continue
        if(len(temp)==0):
            lesson_name = i.find_element(By.CLASS_NAME,"lessontitle-x9B-7").text
            continue
        process[i]=temp[0].text
    #先处理当前的课程
    wait_for_video_completion(driver,lesson_name , action_chains)
    logging.info("开始处理课程...")
    for raw_lesson in process.keys():
        if(process[raw_lesson]=="已完成"):
            continue    
        action_chains.click(raw_lesson).perform()
        WebDriverWait(driver, 5).until(EC.number_of_windows_to_be(2))
        switch_to_new_window(driver)
        wait_for_video_completion(driver,lesson_name, action_chains)

def main():
    logging.basicConfig(
        format="[%(asctime)s] %(filename)s(line:%(lineno)d) - %(levelname)s: %(message)s",
        level=logging.INFO, datefmt="%Y/%m/%d %H:%M:%S"
    )
    logging.info("正在启动Chrome...")
    chrome_options = Options()
    # 指定 Chrome 可执行文件的完整路径
    chrome_options.binary_location = "C:\Program Files\chrome.exe"
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    action_chains = ActionChains(driver)
    
    driver.get("https://teacher.ewt360.com/")
    logging.info(driver.title)
    driver.implicitly_wait(10)

    login(driver)
    #navigate_to_vacation(driver)
    time.sleep(2)  # 等待新页面加载
    click_primary_button(driver)
    logging.info("获取总完成度...")
    time.sleep(5)  # 可考虑进一步用WebDriverWait优化
    progress = get_all_progress(driver)
    sProgress = progress
    # 处理完成度为百分数的情况
    temp = sProgress
    sProgress=[]
    for i in temp:
        l = i["process"][2:].split("/")
        _process = int(l[0]) / int(l[1]) * 100
        sProgress.append({"element":i["element"],"process":_process})
    for i in sProgress:
        if(i["process"] == 100):
            continue
        i["element"].click()
        switch_to_new_window(driver)
        time.sleep(1)
        #获取全部的按钮
        try:
            button = driver.find_elements(By.CLASS_NAME, "btn-3dDLy")
        except Exception as e:
            logging.error("找不到按钮")

        for i in button:
            text = i.text
            #如果是导学案或者已经完成就跳过
            if (text == "导" or i.get_attribute("data-finish")== "true"):
                continue
            #点击按钮
            action_chains.click(i).perform()
            switch_to_new_window(driver)
            if(text!="练"):
                process_lessons(driver, action_chains)
            else:
                logging.info("练习课程")
                time.sleep(1)
                #点击提交
                try:
                    practice_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "ant-btn.ant-btn-primary.my-study-button"))
                    )
                    action_chains.click(practice_btn).perform()
                except Exception as e:
                    logging.error("找不到练习按钮")
                time.sleep(1)
                try:
                    submit_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "confirm-red.confirm-right"))
                    )
                    submit_btn = driver.find_element(By.CLASS_NAME, "confirm-red.confirm-right")
                    action_chains.click(submit_btn).perform()
                except Exception as e:
                    logging.error("找不到确定按钮")
                time.sleep(1)
                try:
                    confirm_btn = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable((By.CLASS_NAME, "content-main-footer_submit_btn"))
                    )
                    action_chains.click(confirm_btn).perform()
                    try:
                        close_btn = WebDriverWait(driver, 10).until(
                            EC.element_to_be_clickable((By.CLASS_NAME, "content-main-footer_submit_btn"))
                        )
                        action_chains.click(close_btn).perform()
                    except Exception as e:
                        logging.error("找不到关闭按钮")
                    time.sleep(1)
                except Exception as e:
                    logging.error("找不到确认按钮")
                time.sleep(1)
                driver.close()
                switch_to_new_window(driver)
                

if __name__ == '__main__':
    main()
