import argparse
import shutil
from pathlib import Path

from log_store import load_log, save_log
from scanner import get_desktop_path


CONFIRM_TEXT = "되돌리기"


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


def get_latest_undo_session(log_data):
    """
    undoStack에서 가장 최근 정리 세션을 가져오는 함수
    """
    undo_stack = log_data.get("undoStack", [])

    if not undo_stack:
        return None

    return undo_stack[-1]


def create_undo_plan(session):
    """
    최근 이동 세션을 바탕으로 되돌리기 계획을 만드는 함수

    movedPath -> originalPath 방향으로 되돌린다.
    """
    moves = session.get("moves", [])

    undo_plan = []

    # 여러 파일을 되돌릴 때는 마지막 이동부터 거꾸로 처리한다.
    for move in reversed(moves):
        undo_plan.append(
            {
                "filename": move.get("filename"),
                "fromPath": move.get("movedPath"),
                "toPath": move.get("originalPath"),
                "source": move.get("source"),
            }
        )

    return undo_plan


def validate_undo_plan(undo_plan, base_path):
    """
    되돌리기 실행 전에 모든 항목이 안전한지 검사하는 함수

    하나라도 문제가 있으면 실제 이동을 실행하지 않는다.
    """
    errors = []

    for item in undo_plan:
        filename = item.get("filename")
        from_path = Path(item.get("fromPath"))
        to_path = Path(item.get("toPath"))

        if not is_inside_base_path(from_path, base_path):
            errors.append(f"{filename}: 현재 파일 위치가 test_desktop 밖입니다.")
            continue

        if not is_inside_base_path(to_path, base_path):
            errors.append(f"{filename}: 되돌릴 위치가 test_desktop 밖입니다.")
            continue

        if not from_path.exists():
            errors.append(f"{filename}: 되돌릴 파일을 찾을 수 없습니다.")
            continue

        if not from_path.is_file():
            errors.append(f"{filename}: 되돌릴 대상이 파일이 아닙니다.")
            continue

        if not to_path.parent.exists():
            errors.append(f"{filename}: 원래 위치의 폴더를 찾을 수 없습니다.")
            continue

        if to_path.exists():
            errors.append(f"{filename}: 원래 위치에 같은 이름의 파일이 이미 있습니다.")
            continue

    return errors


def execute_undo_plan(undo_plan, dry_run=True):
    """
    되돌리기 계획을 실행하는 함수

    dry_run=True:
    실제 이동 없이 되돌릴 예정만 확인한다.

    dry_run=False:
    실제로 파일을 원래 위치로 되돌린다.
    """
    results = []

    for item in undo_plan:
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
                    "message": "실제 이동 없이 되돌리기 예정만 확인했습니다.",
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
                    "message": "파일을 원래 위치로 되돌렸습니다.",
                }
            )

        except Exception as error:
            results.append(
                {
                    "filename": filename,
                    "fromPath": str(from_path),
                    "toPath": str(to_path),
                    "status": "ERROR",
                    "message": f"되돌리기 중 오류가 발생했습니다: {error}",
                }
            )

    return results


def update_log_after_undo(log_data):
    """
    되돌리기 성공 후 로그를 업데이트하는 함수

    undoStack의 가장 최근 세션을 꺼내 redoStack으로 옮긴다.
    """
    session = log_data["undoStack"].pop()
    log_data["redoStack"].append(session)

    save_log(log_data)

    return session


def print_undo_plan(session, undo_plan):
    """
    되돌리기 미리보기를 출력하는 함수
    """
    print("되돌리기 미리보기")
    print("----------------")

    if session is None:
        print("되돌릴 이동 기록이 없습니다.")
        return

    print(f"세션 ID: {session.get('sessionId')}")
    print(f"실행 시각: {session.get('executedAt')}")
    print()

    for item in undo_plan:
        print(f"[되돌리기 예정] {item['filename']}")
        print(f"  현재 위치: {item['fromPath']}")
        print(f"  원래 위치: {item['toPath']}")
        print()


def print_results(results):
    """
    되돌리기 실행 결과를 출력하는 함수
    """
    print("되돌리기 실행 결과")
    print("----------------")

    if not results:
        print("실행할 되돌리기 계획이 없습니다.")
        return

    for result in results:
        status = result["status"]

        if status == "DRY_RUN":
            print(f"[DRY RUN] {result['filename']}")
        elif status == "SUCCESS":
            print(f"[되돌리기 완료] {result['filename']}")
        else:
            print(f"[{status}] {result['filename']}")

        print(f"  현재 위치: {result['fromPath']}")
        print(f"  원래 위치: {result['toPath']}")
        print(f"  메시지: {result['message']}")
        print()


def ask_confirmation():
    """
    실제 되돌리기 전 사용자 확인을 받는 함수
    """
    print()
    print("주의: 이제 실제 되돌리기를 실행합니다.")
    print("현재는 test_desktop 폴더 안에서만 되돌리도록 제한되어 있습니다.")
    print(f"정말 되돌리려면 '{CONFIRM_TEXT}'를 입력하세요.")
    print("취소하려면 아무 글자나 입력하거나 Enter를 누르세요.")
    print()

    user_input = input("입력: ").strip()

    return user_input == CONFIRM_TEXT


def parse_args():
    """
    터미널 명령어 옵션을 읽는 함수

    기본:
    python3 undo.py
    -> dry-run 되돌리기 미리보기

    실제 되돌리기:
    python3 undo.py --apply
    -> 사용자 확인 후 실제 되돌리기
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="실제 되돌리기를 실행합니다.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    log_data = load_log()
    session = get_latest_undo_session(log_data)

    if session is None:
        print("되돌릴 이동 기록이 없습니다.")
    else:
        base_path = Path(session.get("basePath", str(get_desktop_path())))
        undo_plan = create_undo_plan(session)

        print_undo_plan(session, undo_plan)

        errors = validate_undo_plan(undo_plan, base_path)

        if errors:
            print("되돌리기 전에 문제가 발견되었습니다.")
            print("-----------------------------")
            for error in errors:
                print(f"- {error}")
        else:
            if not args.apply:
                print("현재 모드: DRY RUN")
                print("실제 되돌리기를 하려면 python3 undo.py --apply 를 실행하세요.")
                print()

                results = execute_undo_plan(undo_plan, dry_run=True)
                print_results(results)

            else:
                confirmed = ask_confirmation()

                if not confirmed:
                    print("되돌리기를 취소했습니다.")
                else:
                    results = execute_undo_plan(undo_plan, dry_run=False)
                    print_results(results)

                    all_success = all(result["status"] == "SUCCESS" for result in results)

                    if all_success:
                        moved_session = update_log_after_undo(log_data)

                        print("move-log.json을 업데이트했습니다.")
                        print(f"undoStack -> redoStack 이동 세션: {moved_session['sessionId']}")
                    else:
                        print("일부 파일 되돌리기에 실패하여 로그를 업데이트하지 않았습니다.")
