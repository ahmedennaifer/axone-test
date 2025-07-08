import time
import csv
import os
import requests
import logging
import argparse
import uuid
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from dotenv import load_dotenv

load_dotenv()


def setup_logging() -> logging.Logger:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(message)s")
    return logging.getLogger(__name__)


def setup_browser() -> webdriver.Chrome:
    # driver pour tourner le navigateur en headless
    # options pour être plus discrets
    # ref: `https://www.selenium.dev/documentation/webdriver/drivers/options/`

    options = Options()
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)
    options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    )

    options.add_argument("--memory-pressure-off")
    options.add_argument("--max_old_space_size=4096")
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")

    options.add_argument("--disable-background-timer-throttling")
    options.add_argument("--disable-backgrounding-occluded-windows")
    options.add_argument("--disable-renderer-backgrounding")
    options.add_argument("--disable-features=TranslateUI")
    options.add_argument("--disable-ipc-flooding-protection")

    driver = webdriver.Chrome(options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )

    return driver


def login(driver: webdriver.Chrome, logger: logging.Logger) -> bool:
    # on target les champs email et pw, on essaie d'ecrire a la maniere d'un "humain" pour ne pas flagger l'anti-bot
    # on doit avoir un fichier .env avec : EMAIL & PW
    email = os.getenv("EMAIL")
    password = os.getenv("PW")
    if not email or not password:
        logger.error("EMAIL or PW not found in .env file")
        return False

    logger.info("attempting login")
    driver.get("https://www.facebook.com")
    time.sleep(5)  # on attend un peu

    try:
        # on ecrit char par char, comme un humain
        email_field = driver.find_element(By.ID, "email")
        email_field.clear()
        for char in email:
            email_field.send_keys(char)
            time.sleep(0.1)

        time.sleep(1)

        pass_field = driver.find_element(By.ID, "pass")
        pass_field.clear()
        for char in password:
            pass_field.send_keys(char)
            time.sleep(0.1)

        time.sleep(2)  # petite pause avant de clicker

        driver.execute_script("document.querySelector('[name=\"login\"]').click();")
        time.sleep(8)

        if "login" not in driver.current_url and "checkpoint" not in driver.current_url:
            # checkpoint peut parfois venir dans le cas d'un flag
            logger.info("logged in successfully")
            return True
        else:
            logger.error("login failed")
            return False
    except Exception as e:
        logger.error(f"login error: {e}")
        return False


def is_valid_image(src: str) -> bool | str:
    return (
        src
        and "scontent" in src
        and "emoji" not in src.lower()
        and "static.xx.fbcdn.net/images/emoji" not in src
        and "profile" not in src.lower()
        and len(src)
        > 150  # le type d'url d'image de fb sont long. si < 150 -> emoji, donc on jette.
        and ("_n.jpg" in src or "_n.png" in src)
    )


def download_image(image_url: str, filename: str) -> str | None:
    # download l'image dont l'url a été parsé
    # res dans le folder `images`
    try:
        response = requests.get(image_url, timeout=10)
        if response.status_code == 200:
            os.makedirs("images", exist_ok=True)
            filepath = f"images/{filename}.jpg"
            with open(filepath, "wb") as f:
                f.write(response.content)
            return filepath
    except Exception as _:
        return None


def scrape_posts(
    driver: webdriver.Chrome, query: str, num_scrolls: int, logger: logging.Logger
) -> int:
    logger.info(f"starting search for: {query}")

    driver.get(f"https://www.facebook.com/search/posts/?q={query}")
    time.sleep(3)
    driver.execute_script("document.body.click();")  # TODO:
    time.sleep(2)

    csv_file = open("data/data.csv", "w", newline="", encoding="utf-8")
    writer = csv.DictWriter(csv_file, fieldnames=["post_id", "text", "images"])
    writer.writeheader()

    seen_texts = set()  # des doublons sont fréquemment incluses dans les scroll. on stock une set avec les hash de chaque post
    post_count = 0

    for scroll in range(num_scrolls):
        logger.info(f"scroll {scroll + 1}/{num_scrolls}")

        # scroll
        if scroll > 0:
            for _ in range(3):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
                time.sleep(0.5)
            driver.find_element(By.TAG_NAME, "body").send_keys(Keys.END)
            time.sleep(2)

        # balise des posts est `data-ad-preview`
        containers = driver.find_elements(
            By.CSS_SELECTOR, 'div[data-ad-preview="message"], div[dir="auto"]'
        )
        new_posts = 0

        for container in containers:
            try:
                text = container.text.strip()

                #  text hash -> set
                text_hash = hash(text)
                if len(text) > 30 and text_hash not in seen_texts:
                    images = []
                    current = container
                    for _ in range(3):
                        try:
                            parent = current.find_element(By.XPATH, "..")
                            imgs = parent.find_elements(
                                By.CSS_SELECTOR, 'img[src*="scontent"]'
                            )
                            for img in imgs:
                                src = img.get_attribute("src")
                                if is_valid_image(src):  # pyright: ignore
                                    filename = download_image(
                                        src,  # pyright: ignore
                                        f"post_{post_count}_{len(images)}",
                                    )
                                    if filename:
                                        images.append(filename)
                            current = parent
                            if images:
                                break
                        except Exception as _:
                            break

                    writer.writerow(
                        {
                            "post_id": str(uuid.uuid4()),
                            "text": text,
                            "images": ";".join(images),
                        }
                    )
                    csv_file.flush()
                    seen_texts.add(text_hash)
                    post_count += 1
                    new_posts += 1

                    logger.info(f"saved post {post_count} with {len(images)} images")

            except Exception as _:
                continue

        if new_posts == 0 and scroll > 3:
            logger.info("no new content, stopping")
            break

    csv_file.close()
    logger.info(f"completed: {post_count} posts saved to data.csv")
    return post_count


def main() -> None:
    parser = argparse.ArgumentParser(description="Facebook Post Scraper")
    parser.add_argument("--query", required=True, help="Search query")
    parser.add_argument("--num_scrolls", type=int, default=10, help="Number of scrolls")

    args = parser.parse_args()
    logger = setup_logging()
    driver = setup_browser()

    try:
        if login(driver, logger):
            scrape_posts(driver, args.query, args.num_scrolls, logger)
        else:
            logger.error("login failed, exiting")
    except Exception as e:
        logger.error(f"error: {e}")
    finally:
        driver.quit()


if __name__ == "__main__":
    main()
