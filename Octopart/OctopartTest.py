import ssl
import time
import logging
import traceback
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from WRTools import ChromeDriverManager

# 配置日志（调试友好，详细输出每步操作）
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局driver
driver = None
ssl._create_default_https_context = ssl._create_unverified_context

# -------------------------- 核心配置 --------------------------
TARGET_URL = "https://octopart.com/zh/pic18f97j60t-i%2Fpt-microchip-486889"
CHART_CONTAINER_SELECTOR = (By.CSS_SELECTOR, "div.recharts-responsive-container")
TARGET_COMPONENT_NAME = "AreaChart"  # 组件名包含此字符串
TARGET_DATA_SENTRY = "AreaChart"  # data-sentry-element值
MAX_WAIT_TIME = 50


# ----------------------------------------------------------------

def init_driver():
    """初始化浏览器驱动"""
    global driver
    try:
        driver = ChromeDriverManager.getWebDriver(2)
        driver.set_window_size(1200, 800)
        driver.set_page_load_timeout(60)
        logger.info(f"Chrome驱动初始化成功（版本: {driver.capabilities['browserVersion']}）")
        return True
    except Exception as e:
        logger.error(f"驱动初始化失败: {str(e)}")
        return False


def load_page():
    """加载页面并等待图表容器出现"""
    global driver
    try:
        driver.get("https://octopart.com/zh")
        time.sleep(43)  # 等待页面加载完成
        driver.get(TARGET_URL)
        time.sleep(53)
        logger.info(f"已加载页面: {TARGET_URL}")
        # 等待图表容器可见
        WebDriverWait(driver, MAX_WAIT_TIME).until(
            EC.visibility_of_element_located(CHART_CONTAINER_SELECTOR)
        )
        time.sleep(3)  # 等待数据加载
        return True
    except TimeoutException:
        logger.error("页面加载超时，未找到图表容器")
        return False
    except Exception as e:
        logger.error(f"页面加载失败: {str(e)}")
        return False


def get_raw_react_instance():
    """获取必要的React信息（只返回关键字段，避免循环引用）"""
    global driver
    try:
        chart_container = driver.find_element(*CHART_CONTAINER_SELECTOR)
        # 关键修改：JS只提取child节点的必要字段（不返回完整实例）
        js_code = """
        const container = arguments[0];
        // 找到React Fiber实例
        const fiberKeys = Object.keys(container).filter(k => 
            k.startsWith('__reactFiber$') || 
            k.startsWith('__reactInternalInstance$')
        );
        if (!fiberKeys.length) {
            return null;
        }
        const fiberInstance = container[fiberKeys[0]];
        // 只返回child节点的关键信息（避免完整实例的循环引用）
        const child = fiberInstance.child;
        if (!child) {
            return { hasChild: false };
        }
        // 提取我们需要的字段（memoizedProps、type、elementType）
        return {
            hasChild: true,
            childProps: child.memoizedProps || child.pendingProps,
            childType: child.type || child.elementType,
            childElementType: child.elementType  // 额外备份类型信息
        };
        """
        # 执行JS，返回精简后的信息（无循环引用）
        react_info = driver.execute_script(js_code, chart_container)

        if not react_info:
            logger.error("未获取到React相关信息")
            return None

        logger.debug("成功获取精简的React信息")
        return react_info
    except Exception as e:
        logger.error(f"获取React信息失败: {str(e)}")
        return None


def find_target_component(react_info):
    """用Python逻辑查找目标组件（基于精简的React信息）"""
    if not react_info or not react_info.get('hasChild'):
        logger.error("没有找到child节点")
        return None

    # 从精简信息中提取属性（避免处理完整实例）
    props = react_info.get('childProps', {})
    component_type = react_info.get('childType', {}) or react_info.get('childElementType', {})

    # 提取组件信息
    component_name = component_type.get('displayName') or component_type.get('name') or ""
    data_sentry = props.get('data-sentry-element', "")
    has_data = isinstance(props.get('data'), list) and len(props.get('data', [])) > 0

    # 打印调试信息
    logger.debug(f"检查组件: 名称={component_name}, data-sentry={data_sentry}, 有数据={has_data}")

    # 匹配条件
    if (TARGET_COMPONENT_NAME in component_name and
        data_sentry == TARGET_DATA_SENTRY and
        has_data):
        logger.info("找到目标AreaChart组件")
        return props  # 直接返回props，包含data
    else:
        logger.error("组件不匹配")
        logger.error(f"实际信息: 名称={component_name}, data-sentry={data_sentry}")
        return None


def process_data(raw_data):
    """处理数据（纯Python逻辑）"""
    if not raw_data or not isinstance(raw_data, list):
        return []

    cleaned_data = []
    for item in raw_data:
        item_copy = item.copy()
        # 删除xAxisDate字段（如果存在）
        if "xAxisDate" in item_copy:
            del item_copy["xAxisDate"]
        cleaned_data.append(item_copy)
    return cleaned_data


def main():
    global driver
    try:
        # 1. 初始化驱动
        if not init_driver():
            return
        # 2. 加载页面
        if not load_page():
            return
        # 3. 获取React实例（仅一次JS调用）
        react_instance = get_raw_react_instance()
        if not react_instance:
            return
        # 4. 用Python逻辑查找目标组件（核心优化：减少JS依赖）
        component_props = find_target_component(react_instance)
        if not component_props:
            return
        # 5. 提取并处理数据
        raw_data = component_props.get('data')
        processed_dates = process_data(raw_data)

        if processed_dates:
            logger.info(f" {processed_dates}")

    except KeyboardInterrupt:
        logger.warning("程序被手动中断")
    except Exception as e:
        logger.error(f"主程序异常: {str(e)}")
        logger.error(traceback.format_exc()[:500])
    finally:
        if driver:
            try:
                driver.quit()
                logger.info("浏览器已关闭")
            except Exception as e:
                logger.warning(f"关闭浏览器错误: {str(e)}")


if __name__ == "__main__":
    main()