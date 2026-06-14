# 테스트용 가짜 Desktop 폴더 이름
TEST_DESKTOP_FOLDER_NAME = "test_desktop"


# 앱 내부 설정 폴더 이름
APP_FOLDER_NAME = ".deskpilot"


# 분류되지 않은 파일을 보낼 기본 보관함 폴더 이름
ARCHIVE_FOLDER_NAME = "archive"


# 실제 파일 이동 확인 문구
MOVE_CONFIRM_TEXT = "정리하기"


# 되돌리기 확인 문구
UNDO_CONFIRM_TEXT = "되돌리기"


# 앞으로가기 확인 문구
REDO_CONFIRM_TEXT = "앞으로가기"


# 정리 대상에서 제외할 파일 이름 목록
EXCLUDED_FILENAMES = {
    ".DS_Store",
    "desktop.ini",
    "Thumbs.db",
    "rules.txt",
    "move-log.json",
}


# 이동 목적지 폴더 목록에서 제외할 폴더 이름
EXCLUDED_FOLDER_NAMES = {
    APP_FOLDER_NAME,
    "deskpilot",
    "__pycache__",
}
