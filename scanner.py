from pathlib import Path

# 테스트용 가짜 Desktop 폴더 이름
TEST_DESKTOP_FOLDER_NAME = "test_desktop"

# 정리 대상에서 제외할 파일 이름 목록
EXCLUDED_FILENAMES = {
    ".DS_Store",
    "desktop.ini",
    "Thumbs.db",
    "rules.txt",
    "move-log.json",
}

def get_desktop_path():
    """
    테스트용 가짜 Desktop 폴더 경로를 가져오는 함수
    """
    return Path.home() / "Desktop" / "test_desktop"


def is_hidden_file(path):
    """
    숨김 파일인지 확인하는 함수
    """
    return path.name.startswith(".")


def is_excluded_file(path):
    """
    정리 대상에서 제외해야 하는 파일인지 확인하는 함수
    """
    return path.name in EXCLUDED_FILENAMES


def scan_desktop_files():
    """
    Desktop 바로 아래에 있는 파일만 가져오는 함수

    제외 대상:
    1. 폴더
    2. 숨김 파일
    3. 시스템 파일
    4. rules.txt
    5. move-log.json
    """
    desktop_path = get_desktop_path()

    files = []

    for item in desktop_path.iterdir():
        # 폴더는 정리 대상이 아니므로 제외한다.
        if not item.is_file():
            continue

        # 숨김 파일은 제외한다.
        if is_hidden_file(item):
            continue

        # 시스템 파일 또는 앱 설정 파일은 제외한다.
        if is_excluded_file(item):
            continue

        files.append(item)

    return files


if __name__ == "__main__":
    desktop_files = scan_desktop_files()

    print("Desktop 정리 대상 파일 목록")
    print("-----------------------")

    if not desktop_files:
        print("정리할 파일이 없습니다.")
    else:
        for file in desktop_files:
            print(file.name)
