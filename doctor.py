import json

from scanner import get_desktop_path, scan_destination_folders
from rules import get_rules_path
from log_store import get_log_path
from config import APP_FOLDER_NAME, ARCHIVE_FOLDER_NAME


def create_check_result(status, message):
    """
    점검 결과를 딕셔너리로 만드는 함수

    status:
    - OK
    - WARN
    - ERROR
    """
    return {
        "status": status,
        "message": message,
    }


def check_test_desktop_exists():
    """
    test_desktop 폴더가 존재하는지 확인한다.
    """
    desktop_path = get_desktop_path()

    if not desktop_path.exists():
        return create_check_result(
            "ERROR",
            f"테스트 Desktop 폴더가 없습니다: {desktop_path}",
        )

    if not desktop_path.is_dir():
        return create_check_result(
            "ERROR",
            f"테스트 Desktop 경로가 폴더가 아닙니다: {desktop_path}",
        )

    return create_check_result(
        "OK",
        f"테스트 Desktop 폴더가 존재합니다: {desktop_path}",
    )


def check_app_folder_exists():
    """
    .deskpilot 설정 폴더가 존재하는지 확인한다.
    """
    app_folder_path = get_desktop_path() / APP_FOLDER_NAME

    if not app_folder_path.exists():
        return create_check_result(
            "WARN",
            f"{APP_FOLDER_NAME} 폴더가 없습니다. rules.txt나 move-log.json 저장 시 자동 생성될 수 있습니다.",
        )

    if not app_folder_path.is_dir():
        return create_check_result(
            "ERROR",
            f"{APP_FOLDER_NAME} 경로가 폴더가 아닙니다: {app_folder_path}",
        )

    return create_check_result(
        "OK",
        f"{APP_FOLDER_NAME} 폴더가 존재합니다.",
    )


def check_rules_file_exists():
    """
    rules.txt 파일이 존재하는지 확인한다.
    """
    rules_path = get_rules_path()

    if not rules_path.exists():
        return create_check_result(
            "WARN",
            f"rules.txt 파일이 없습니다: {rules_path}",
        )

    if not rules_path.is_file():
        return create_check_result(
            "ERROR",
            f"rules.txt 경로가 파일이 아닙니다: {rules_path}",
        )

    return create_check_result(
        "OK",
        "rules.txt 파일이 존재합니다.",
    )


def check_archive_folder_exists():
    """
    archive 폴더가 존재하는지 확인한다.
    """
    archive_path = get_desktop_path() / ARCHIVE_FOLDER_NAME

    if not archive_path.exists():
        return create_check_result(
            "WARN",
            f"{ARCHIVE_FOLDER_NAME} 폴더가 없습니다. 분류 실패 파일은 Desktop에 남게 될 수 있습니다.",
        )

    if not archive_path.is_dir():
        return create_check_result(
            "ERROR",
            f"{ARCHIVE_FOLDER_NAME} 경로가 폴더가 아닙니다: {archive_path}",
        )

    return create_check_result(
        "OK",
        f"{ARCHIVE_FOLDER_NAME} 폴더가 존재합니다.",
    )


def check_move_log_json():
    """
    move-log.json 파일이 정상 JSON인지 확인한다.
    """
    log_path = get_log_path()

    if not log_path.exists():
        return create_check_result(
            "WARN",
            "move-log.json 파일이 아직 없습니다. 실제 이동을 하면 생성됩니다.",
        )

    if not log_path.is_file():
        return create_check_result(
            "ERROR",
            f"move-log.json 경로가 파일이 아닙니다: {log_path}",
        )

    try:
        with open(log_path, "r", encoding="utf-8") as file:
            log_data = json.load(file)

    except json.JSONDecodeError:
        return create_check_result(
            "ERROR",
            "move-log.json 파일의 JSON 형식이 깨져 있습니다.",
        )

    if "undoStack" not in log_data:
        return create_check_result(
            "ERROR",
            "move-log.json에 undoStack이 없습니다.",
        )

    if "redoStack" not in log_data:
        return create_check_result(
            "ERROR",
            "move-log.json에 redoStack이 없습니다.",
        )

    return create_check_result(
        "OK",
        "move-log.json 파일이 정상입니다.",
    )


def check_destination_folders():
    """
    이동 목적지 폴더가 있는지 확인한다.
    """
    try:
        destination_folders = scan_destination_folders()

    except Exception as error:
        return create_check_result(
            "ERROR",
            f"이동 목적지 폴더를 스캔하는 중 오류가 발생했습니다: {error}",
        )

    if not destination_folders:
        return create_check_result(
            "WARN",
            "이동 목적지 폴더가 없습니다. school, study, project, archive 같은 폴더를 만들어주세요.",
        )

    folder_names = [folder.name for folder in destination_folders]

    return create_check_result(
        "OK",
        f"이동 목적지 폴더 {len(folder_names)}개를 찾았습니다: {', '.join(folder_names)}",
    )


def run_checks():
    """
    전체 상태 점검을 실행하는 함수
    """
    checks = [
        check_test_desktop_exists(),
        check_app_folder_exists(),
        check_rules_file_exists(),
        check_archive_folder_exists(),
        check_move_log_json(),
        check_destination_folders(),
    ]

    return checks


def print_checks(checks):
    """
    상태 점검 결과를 출력하는 함수
    """
    print("DeskPilot 상태 점검")
    print("------------------")

    error_count = 0
    warn_count = 0

    for check in checks:
        status = check["status"]
        message = check["message"]

        if status == "ERROR":
            error_count += 1
            print(f"[ERROR] {message}")

        elif status == "WARN":
            warn_count += 1
            print(f"[WARN] {message}")

        else:
            print(f"[OK] {message}")

    print()
    print("상태 점검 요약")
    print("------------")
    print(f"ERROR: {error_count}")
    print(f"WARN: {warn_count}")

    if error_count > 0:
        print("결과: 반드시 수정해야 할 문제가 있습니다.")
    elif warn_count > 0:
        print("결과: 실행은 가능하지만 확인하면 좋은 항목이 있습니다.")
    else:
        print("결과: 문제 없음")


if __name__ == "__main__":
    checks = run_checks()
    print_checks(checks)
