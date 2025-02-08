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

USER = "username"
PASS = "userpassword"


def switch_to_new_window(driver):
    """切换到最新打开的窗口"""
    new_handle = driver.window_handles[-1]
    logging.info(f"切换到新页面: {new_handle}")
    driver.switch_to.window(new_handle)

def get_all_progress(driver):
    """等待并获取总完成度文本"""
    try:
        progress_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "#rc-tabs-0-panel-1 > section > section > section > span:nth-child(1) > span")
            )
        )
        return progress_element.text
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
        EC.element_to_be_clickable((By.LINK_TEXT, "我的假期"))
    )
    vacation_link.click()
    driver.close()
    switch_to_new_window(driver)

def click_primary_button(driver):
    """等待并点击页面上的主要按钮"""
    primary_btn = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "ant-btn-primary"))
    )
    primary_btn.click()

def wait_for_video_completion(driver, lesson_name, action_chains):
    """处理视频播放，直至视频播放完毕"""
    try:
        play_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.CLASS_NAME, "vjs-big-play-button"))
        )
        play_btn.click()
    except TimeoutException:
        logging.error("找不到播放按钮")

    # 设置播放速度和静音
    driver.execute_script('document.querySelector("video").playbackRate = 2')
    driver.execute_script('document.querySelector("video").muted = true')
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
    try:
        container = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ant-spin-container"))
        )
        lesson_container = container.find_element(By.XPATH, "./*")
        lesson_list = lesson_container.find_elements(By.XPATH, "./*")
    except Exception as e:
        logging.error("获取课程列表失败")
        return

    # 若最后一个元素为“加载更多”，点击后重新获取列表
    if lesson_list and lesson_list[-1].text == "加载更多":
        logging.info("发现更多课程,重新获取...")
        action_chains.click(lesson_list[-1]).perform()
        lesson_list = container.find_element(By.XPATH, "./*").find_elements(By.XPATH, "./*")[:-1]
    elif lesson_list:
        lesson_list.pop()  # 去掉多余项

    for raw_lesson in lesson_list:
        logging.info(f"总进度: {get_all_progress(driver)}")
        action_chains.move_to_element(raw_lesson).perform()
        lessons = raw_lesson.find_elements(By.XPATH, "./*")
        if not lessons or len(lessons) < 2:
            continue
        # 获取课程名称和状态
        lesson_name = lessons[0].find_element(By.XPATH, "./*").text
        lesson_status = (lessons[1].find_elements(By.XPATH, "./*")[1].text
                         if lessons[1].text != "已完成" else "已完成")
        logging.info(f"{lesson_name} | {lesson_status}")
        if lesson_status == "去学习":
            action_chains.click(lessons[0]).perform()
            WebDriverWait(driver, 10).until(EC.number_of_windows_to_be(2))
            switch_to_new_window(driver)
            # 根据当前URL判断是否为自动完成的页面
            if ("xinli.ewt360.com" in driver.current_url or
                    "web.ewt360.com/spiritual-growth" in driver.current_url):
                time.sleep(5)
                logging.info(f"{lesson_name} | 已完成")
                driver.close()
                switch_to_new_window(driver)
            else:
                time.sleep(1)
                wait_for_video_completion(driver, lesson_name, action_chains)

def main():
    logging.basicConfig(
        format="[%(asctime)s] %(filename)s(line:%(lineno)d) - %(levelname)s: %(message)s",
        level=logging.INFO, datefmt="%Y/%m/%d %H:%M:%S"
    )
    logging.info("正在启动Chrome...")
    chrome_options = Options()
    # 指定 Chrome 可执行文件的完整路径
    chrome_options.binary_location = "C:/example.exe"
    driver = webdriver.Chrome(options=chrome_options)
    driver.maximize_window()
    action_chains = ActionChains(driver)
    
    driver.get("https://teacher.ewt360.com/")
    logging.info(driver.title)
    driver.implicitly_wait(10)

    login(driver)
    navigate_to_vacation(driver)
    time.sleep(5)  # 等待新页面加载
    click_primary_button(driver)
    logging.info("获取总完成度...")
    time.sleep(10)  # 可考虑进一步用WebDriverWait优化
    progress = get_all_progress(driver)
    sProgress = progress.split("/")
    if sProgress[0] == sProgress[1]:
        logging.info("所有课程已完成,按下回车退出")
        input()
    else:
        logging.info("寻找左滑按钮...")
        time.sleep(5)
        try:
            left_btn = driver.find_element(By.CLASS_NAME, "left-icon")
        except Exception as e:
            logging.error("找不到左滑按钮")
            left_btn = None

        start = True
        turn_left = False
        confirm_quit = False
        while True:
            if turn_left and left_btn:
                try:
                    action_chains.click(left_btn).perform()
                except JavascriptException:
                    logging.info("页面最左")
                    time.sleep(10)
                    turn_left = False
                    start = True
            if start:
                logging.info("获取完成度...")
                time.sleep(1)
                try:
                    swiper_box = driver.find_element(By.CLASS_NAME, "swiper-item-box")
                    data_container = swiper_box.find_element(By.XPATH, "./*")
                    data_items = data_container.find_elements(By.XPATH, "./*")
                except Exception as e:
                    logging.error("获取数据失败")
                    break
                for index, item in enumerate(data_items):
                    progress = get_all_progress(driver)
                    sProgress = progress.split("/")
                    if sProgress[0] == sProgress[1]:
                        logging.info("已完成所有课程!")
                        logging.info("回车退出")
                        start = False
                        confirm_quit = True
                        input()
                        break
                    if not item.text.strip():
                        continue
                    try:
                        pdata = item.find_element(By.TAG_NAME, "div")
                        pdata2 = item.find_element(By.TAG_NAME, "p")
                    except Exception:
                        continue
                    day = pdata.text
                    progress_text = pdata2.text
                    parts = progress_text.split("/")
                    if parts[0] != parts[1]:
                        logging.info(f"{day}的进度为{progress_text}")
                        action_chains.click(item).perform()
                        time.sleep(1)
                        process_lessons(driver, action_chains)
                    else:
                        # 如果下一个元素为空，则右滑
                        if index + 1 < len(data_items) and not data_items[index + 1].text.strip():
                            logging.info("右滑")
                            try:
                                right_btn = driver.find_element(By.CLASS_NAME, "right-icon")
                                action_chains.click(right_btn).perform()
                            except Exception as e:
                                logging.error("找不到右滑按钮")
                            time.sleep(3)
                            break
            elif confirm_quit:
                break
        driver.quit()

if __name__ == '__main__':
    main()
