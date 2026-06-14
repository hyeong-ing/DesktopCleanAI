import argparse
import shutil
from pathlib import Path

from log_store import load_log, save_log
from scanner import get_desktop_path


CONFIRM_TEXT = "앞으로가기"


def is_inside_base_path(path, base_path):
    """
    주어진 path가 base_path 내부에 있는지 확인하는 함수

    안전장치:
    test_desktop 밖의 파일을 실수로 건드리지 않기 위해 사용한다.
    """
    try:
        path.resolve().relative_to(base_path.resolve())
        return True
    except ValueError:
        return False


def get_latest_redo_session(log_data):
    """
    redoStack에서 가장 최근 세션을 가져오는 함수
    """
    redo_stack = log_data.get("redoStack", [])

    if not redo_stack:
        return None

    return redo_stack[-1]


def create_redo_plan(session):
    """
    redoStack의 세션을 바탕으로 앞으로가기 계획을 만드는 함수

    originalPath -> movedPath 방향으로 다시 이동한다.
    """
    moves = session.get("moves", [])

    redo_plan = []

    for move in moves:
        redo_plan.append(
            {
                "filename": move.get("filename"),
                "fromPath": move.get("originalPath"),
                "toPath": move.get("movedPath"),
                "source": move.get("source"),
            }
        )

    return redo_plan


def validate_redo_plan(redo_plan, base_path):
    """
    앞으로가기 실행 전에 모든 항목이 안전한지 검사하는 함수

    하나라도 문제가 있으면 실제 이동을 실행하지 않는다.
    """
    errors = []

    for item in redo_plan:
        filename = item.get("filename")
        from_path = Path(item.get("fromPath"))
        to_path = Path(item.get("toPath"))

        if not is_inside_base_path(from_path, base_path):
            errors.append(f"{filename}: 현재 파일 위치가 test_desktop 밖입니다.")
            continue

        if not is_inside_base_path(to_path, base_path):
            errors.append(f"{filename}: 이동할 위치가 test_desktop 밖입니다.")
            continue

        if not from_path.exists():
            errors.append(f"{filename}: 앞으로가기 할 파일을 찾을 수 없습니다.")
            continue

        if not from_path.is_file():
            errors.append(f"{filename}: 앞으로가기 대상이 파일이 아닙니다.")
            continue

        if not to_path.parent.exists():
            errors.append(f"{filename}: 이동할 폴더를 찾을 수 없습니다.")
            continue

        if to_path.exists():
            errors.append(f"{filename}: 이동할 위치에 같은 이름의 파일이 이미 있습니다.")
            continue

    return errors


def execute_redo_plan(redo_plan, dry_run=True):
    """
    앞으로가기 계획을 실행하는 함수

    dry_run=True:
    실제 이동 없이 앞으로가기 예정만 확인한다.

    dry_run=False:
    실제로 파일을 다시 이동한다.
    """
    results = []

    for item in redo_plan:
        filename = item.get("filename")
        from_path = Path(item.get("fromPath"))
        to_path = Path(item.get("toPath"))

        if dry_run:
            results.append(
                {
                    "filename": filename,
                    "fromPath": str(from_path),
                    "toPath": str(to_path),
                    "status": "DRY_RUN",
                    "message": "실제 이동 없이 앞으로가기 예정만 확인했습니다.",
                }
            )
            continue

        try:
            shutil.move(str(from_path), str(to_path))

            results.append(
                {
                    "filename": filename,
                    "fromPath": str(from_path),
                    "toPath": str(to_path),
                    "status": "SUCCESS",
                    "message": "파일을 다시 이동했습니다.",
                }
            )

        except Exception as error:
            results.append(
                {
                    "filename": filename,
                    "fromPath": str(from_path),
                    "toPath": str(to_path),
                    "status": "ERROR",
                    "message": f"앞으로가기 중 오류가 발생했습니다: {error}",
                }
            )

    return results


def update_log_after_redo(log_data):
    """
    앞으로가기 성공 후 로그를 업데이트하는 함수

    redoStack의 가장 최근 세션을 꺼내 undoStack으로 옮긴다.
    """
    session = log_data["redoStack"].pop()
    log_data["undoStack"].append(session)

    save_log(log_data)

    return session


def print_redo_plan(session, redo_plan):
    """
    앞으로가기 미리보기를 출력하는 함수
    """
    print("앞으로가기 미리보기")
    print("------------------")

    if session is None:
        print("앞으로가기 할 기록이 없습니다.")
        return

    print(f"세션 ID: {session.get('sessionId')}")
    print(f"실행 시각: {session.get('executedAt')}")
    print()

    for item in redo_plan:
        print(f"[앞으로가기 예정] {item['filename']}")
        print(f"  현재 위치: {item['fromPath']}")
        print(f"  이동 위치: {item['toPath']}")
        print()


def print_results(results):
    """
    앞으로가기 실행 결과를 출력하는 함수
    """
    print("앞으로가기 실행 결과")
    print("------------------")

    if not results:
        print("실행할 앞으로가기 계획이 없습니다.")
        return

    for result in results:
        status = result["status"]

        if status == "DRY_RUN":
            print(f"[DRY RUN] {result['filename']}")
        elif status == "SUCCESS":
            print(f"[앞으로가기 완료] {result['filename']}")
        else:
            print(f"[{status}] {result['filename']}")

        print(f"  현재 위치: {result['fromPath']}")
        print(f"  이동 위치: {result['toPath']}")
        print(f"  메시지: {result['message']}")
        print()


def ask_confirmation():
    """
    실제 앞으로가기 전 사용자 확인을 받는 함수
    """
    print()
    print("주의: 이제 실제 앞으로가기를 실행합니다.")
    print("현재는 test_desktop 폴더 안에서만 이동되도록 제한되어 있습니다.")
    print(f"정말 앞으로가기를 하려면 '{CONFIRM_TEXT}'를 입력하세요.")
    print("취소하려면 아무 글자나 입력하거나 Enter를 누르세요.")
    print()

    user_input = input("입력: ").strip()

    return user_input == CONFIRM_TEXT


def parse_args():
    """
    터미널 명령어 옵션을 읽는 함수

    기본:
    python3 redo.py
    -> dry-run 앞으로가기 미리보기

    실제 앞으로가기:
    python3 redo.py --apply
    -> 사용자 확인 후 실제 앞으로가기
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="실제 앞으로가기를 실행합니다.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    log_data = load_log()
    session = get_latest_redo_session(log_data)

    if session is None:
        print("앞으로가기 할 기록이 없습니다.")
    else:
        base_path = Path(session.get("basePath", str(get_desktop_path())))
        redo_plan = create_redo_plan(session)

        print_redo_plan(session, redo_plan)

        errors = validate_redo_plan(redo_plan, base_path)

        if errors:
            print("앞으로가기 전에 문제가 발견되었습니다.")
            print("-----------------------------")
            for error in errors:
                print(f"- {error}")
        else:
            if not args.apply:
                print("현재 모드: DRY RUN")
                print("실제 앞으로가기를 하려면 python3 redo.py --apply 를 실행하세요.")
                print()

                results = execute_redo_plan(redo_plan, dry_run=True)
                print_results(results)

            else:
                confirmed = ask_confirmation()

                if not confirmed:
                    print("앞으로가기를 취소했습니다.")
                else:
                    results = execute_redo_plan(redo_plan, dry_run=False)
                    print_results(results)

                    all_success = all(result["status"] == "SUCCESS" for result in results)

                    if all_success:
                        moved_session = update_log_after_redo(log_data)

                        print("move-log.json을 업데이트했습니다.")
                        print(f"redoStack -> undoStack 이동 세션: {moved_session['sessionId']}")
                    else:
                        print("일부 파일 앞으로가기에 실패하여 로그를 업데이트하지 않았습니다.")
