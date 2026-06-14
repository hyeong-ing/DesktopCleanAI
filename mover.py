import argparse
import shutil
from pathlib import Path

from log_store import save_move_session
from scanner import get_desktop_path
from path_planner import build_path_plan
from config import MOVE_CONFIRM_TEXT, APP_FOLDER_NAME



def create_result(item, status, message):
    """
    이동 실행 결과를 딕셔너리로 만드는 함수

    나중에 move-log.json에 저장할 때도 이 구조를 사용할 수 있다.
    """
    return {
        "filename": item.get("filename"),
        "action": item.get("action"),
        "source": item.get("source"),
        "originalPath": item.get("originalPath"),
        "targetPath": item.get("targetPath"),
        "status": status,
        "message": message,
    }


def is_inside_base_path(path, base_path):
    """
    주어진 path가 base_path 내부에 있는지 확인하는 함수

    안전장치:
    test_desktop 밖의 파일을 실수로 이동하지 않기 위해 사용한다.
    """
    try:
        path.resolve().relative_to(base_path.resolve())
        return True
    except ValueError:
        return False


def execute_move_plan(path_plan, dry_run=True):
    """
    이동 계획을 실행하는 함수

    dry_run=True:
    실제 파일 이동 없이 예정 정보만 확인한다.

    dry_run=False:
    실제로 파일을 이동한다.
    """
    results = []
    base_path = get_desktop_path()

    for item in path_plan:
        action = item.get("action")
        original_path_text = item.get("originalPath")
        target_path_text = item.get("targetPath")

        # MOVE가 아닌 항목은 이동하지 않는다.
        if action != "MOVE":
            results.append(
                create_result(
                    item,
                    "SKIPPED",
                    "MOVE 대상이 아니므로 이동하지 않습니다.",
                )
            )
            continue

        # 원본 경로나 대상 경로가 없으면 이동할 수 없다.
        if not original_path_text or not target_path_text:
            results.append(
                create_result(
                    item,
                    "ERROR",
                    "원본 경로 또는 대상 경로가 없습니다.",
                )
            )
            continue

        original_path = Path(original_path_text)
        target_path = Path(target_path_text)

        # 원본 파일이 실제로 없으면 이동할 수 없다.
        if not original_path.exists():
            results.append(
                create_result(
                    item,
                    "ERROR",
                    "원본 파일을 찾을 수 없습니다.",
                )
            )
            continue

        # 원본이 파일이 아니면 이동하지 않는다.
        if not original_path.is_file():
            results.append(
                create_result(
                    item,
                    "ERROR",
                    "원본 경로가 파일이 아닙니다.",
                )
            )
            continue

        # 대상 폴더가 실제로 없으면 이동할 수 없다.
        if not target_path.parent.exists():
            results.append(
                create_result(
                    item,
                    "ERROR",
                    "대상 폴더를 찾을 수 없습니다.",
                )
            )
            continue

        # 대상 폴더가 폴더가 아니면 이동할 수 없다.
        if not target_path.parent.is_dir():
            results.append(
                create_result(
                    item,
                    "ERROR",
                    "대상 경로의 부모가 폴더가 아닙니다.",
                )
            )
            continue

        # test_desktop 밖으로 이동하려는 경우 차단한다.
        if not is_inside_base_path(original_path, base_path):
            results.append(
                create_result(
                    item,
                    "ERROR",
                    "원본 파일이 test_desktop 밖에 있어 이동하지 않습니다.",
                )
            )
            continue

        if not is_inside_base_path(target_path, base_path):
            results.append(
                create_result(
                    item,
                    "ERROR",
                    "대상 경로가 test_desktop 밖에 있어 이동하지 않습니다.",
                )
            )
            continue

        # 혹시 대상 경로에 이미 파일이 있으면 덮어쓰지 않는다.
        if target_path.exists():
            results.append(
                create_result(
                    item,
                    "ERROR",
                    "대상 경로에 이미 파일이 있어 덮어쓰지 않습니다.",
                )
            )
            continue

        # dry-run 모드에서는 실제 이동하지 않는다.
        if dry_run:
            results.append(
                create_result(
                    item,
                    "DRY_RUN",
                    "실제 이동 없이 이동 예정만 확인했습니다.",
                )
            )
            continue

        # 실제 파일 이동
        try:
            shutil.move(str(original_path), str(target_path))

            results.append(
                create_result(
                    item,
                    "SUCCESS",
                    "파일 이동을 완료했습니다.",
                )
            )

        except Exception as error:
            results.append(
                create_result(
                    item,
                    "ERROR",
                    f"파일 이동 중 오류가 발생했습니다: {error}",
                )
            )

    return results


def print_execution_results(results):
    """
    이동 실행 결과를 터미널에 출력하는 함수
    """
    print("파일 이동 실행 결과")
    print("----------------")

    if not results:
        print("실행할 이동 계획이 없습니다.")
        return

    for result in results:
        status = result["status"]
        filename = result["filename"]
        original_path = result["originalPath"]
        target_path = result["targetPath"]
        message = result["message"]

        if status == "DRY_RUN":
            print(f"[DRY RUN] {filename}")
            print(f"  원본: {original_path}")
            print(f"  대상: {target_path}")
            print(f"  메시지: {message}")
            print()

        elif status == "SUCCESS":
            print(f"[이동 완료] {filename}")
            print(f"  원본: {original_path}")
            print(f"  대상: {target_path}")
            print(f"  메시지: {message}")
            print()

        elif status == "SKIPPED":
            print(f"[건너뜀] {filename}")
            print(f"  이유: {message}")
            print()

        else:
            print(f"[{status}] {filename}")
            print(f"  원본: {original_path}")
            print(f"  대상: {target_path}")
            print(f"  메시지: {message}")
            print()


def ask_confirmation():
    """
    실제 이동 전 사용자 확인을 받는 함수

    정확히 '정리하기'를 입력해야만 실제 이동한다.
    """
    print()
    print("주의: 이제 실제 파일 이동을 실행합니다.")
    print("현재는 test_desktop 폴더 안에서만 이동되도록 제한되어 있습니다.")
    print(f"정말 파일을 이동하려면 '{MOVE_CONFIRM_TEXT}'를 입력하세요.")
    print("취소하려면 아무 글자나 입력하거나 Enter를 누르세요.")
    print()

    user_input = input("입력: ").strip()

    return user_input == MOVE_CONFIRM_TEXT


def parse_args():
    """
    터미널 명령어 옵션을 읽는 함수

    기본:
    python3 mover.py
    -> dry-run 실행

    실제 이동:
    python3 mover.py --apply
    -> 사용자 확인 후 실제 이동
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="실제 파일 이동을 실행합니다.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    path_plan = build_path_plan()

    if not args.apply:
        print("현재 모드: DRY RUN")
        print("실제 이동하려면 python3 mover.py --apply 를 실행하세요.")
        print()

        results = execute_move_plan(path_plan, dry_run=True)
        print_execution_results(results)

    else:
        confirmed = ask_confirmation()
    

        if not confirmed:
            print("파일 이동을 취소했습니다.")
        else:
            results = execute_move_plan(path_plan, dry_run=False)
            print_execution_results(results)

            session = save_move_session(results)

            if session is None:
                print("저장할 이동 로그가 없습니다.")
            else:
                print()
                print("이동 로그를 저장했습니다.")
                print(f"세션 ID: {session['sessionId']}")
                print(f"저장 위치: {get_desktop_path() / APP_FOLDER_NAME / 'move-log.json'}")
