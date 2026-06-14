from pathlib import Path

from config import (
    TEST_DESKTOP_FOLDER_NAME,
    EXCLUDED_FILENAMES,
    EXCLUDED_FOLDER_NAMES,
)

def get_desktop_path():
    """
    테스트용 가짜 Desktop 폴더 경로를 가져오는 함수

    실제 Desktop 전체를 바로 스캔하지 않고,
    Desktop 안에 만든 test_desktop 폴더만 사용한다.
    """
    return Path.home() / "Desktop" / TEST_DESKTOP_FOLDER_NAME


def validate_desktop_path(desktop_path):
    """
    테스트용 Desktop 폴더가 실제로 존재하는지 확인하는 함수

    폴더가 없으면 이후 코드에서 오류가 나기 때문에,
    미리 알아보기 쉬운 에러 메시지를 보여준다.
    """
    if not desktop_path.exists():
        raise FileNotFoundError(f"테스트 Desktop 폴더를 찾을 수 없습니다: {desktop_path}")

    if not desktop_path.is_dir():
        raise NotADirectoryError(f"Desktop 경로가 폴더가 아닙니다: {desktop_path}")


def is_hidden_path(path):
    """
    숨김 파일 또는 숨김 폴더인지 확인하는 함수

    macOS나 Linux에서는 이름이 . 으로 시작하면 숨김 항목이다.
    예: .DS_Store, .env, .deskpilot
    """
    return path.name.startswith(".")


def is_excluded_file(path):
    """
    정리 대상에서 제외해야 하는 파일인지 확인하는 함수
    """
    return path.name in EXCLUDED_FILENAMES


def is_excluded_folder(path):
    """
    이동 목적지에서 제외해야 하는 폴더인지 확인하는 함수
    """
    return path.name in EXCLUDED_FOLDER_NAMES


def scan_desktop_files():
    """
    test_desktop 바로 아래에 있는 파일만 가져오는 함수

    제외 대상:
    1. 폴더
    2. 숨김 파일
    3. 시스템 파일
    4. rules.txt
    5. move-log.json
    """
    desktop_path = get_desktop_path()
    validate_desktop_path(desktop_path)

    files = []

    for item in desktop_path.iterdir():
        # 파일이 아니면 제외한다.
        # 즉, 폴더는 여기서 제외된다.
        if not item.is_file():
            continue

        # 숨김 파일은 제외한다.
        if is_hidden_path(item):
            continue

        # 시스템 파일이나 앱 설정 파일은 제외한다.
        if is_excluded_file(item):
            continue

        files.append(item)

    # 이름순으로 정렬해서 결과가 매번 비슷하게 나오도록 한다.
    return sorted(files, key=lambda path: path.name.lower())


def scan_destination_folders():
    """
    test_desktop 바로 아래에 있는 폴더만 가져오는 함수

    이 폴더들은 나중에 파일을 이동할 목적지 후보가 된다.

    제외 대상:
    1. 파일
    2. 숨김 폴더
    3. 앱 내부 설정 폴더
    4. 파이썬 캐시 폴더
    """
    desktop_path = get_desktop_path()
    validate_desktop_path(desktop_path)

    folders = []

    for item in desktop_path.iterdir():
        # 폴더가 아니면 제외한다.
        # 즉, 파일은 여기서 제외된다.
        if not item.is_dir():
            continue

        # 숨김 폴더는 제외한다.
        if is_hidden_path(item):
            continue

        # 앱 설정 폴더나 캐시 폴더는 제외한다.
        if is_excluded_folder(item):
            continue

        folders.append(item)

    # 이름순으로 정렬해서 결과가 매번 비슷하게 나오도록 한다.
    return sorted(folders, key=lambda path: path.name.lower())


if __name__ == "__main__":
    desktop_files = scan_desktop_files()
    destination_folders = scan_destination_folders()

    print("정리 대상 파일 목록")
    print("----------------")

    if not desktop_files:
        print("정리할 파일이 없습니다.")
    else:
        for file in desktop_files:
            print(file.name)

    print()
    print("이동 목적지 폴더 목록")
    print("-------------------")

    if not destination_folders:
        print("이동 목적지 폴더가 없습니다.")
    else:
        for folder in destination_folders:
            print(folder.name)
