import argparse
from pathlib import Path

from path_planner import build_path_plan, print_path_plan
from config import APP_FOLDER_NAME

from selected_mover import (
    print_selectable_plan,
    ask_selection,
)

from mover import (
    execute_move_plan,
    print_execution_results,
    ask_confirmation as ask_move_confirmation,
)

from log_store import (
    save_move_session,
    load_log,
)

from scanner import get_desktop_path

from undo import (
    get_latest_undo_session,
    create_undo_plan,
    validate_undo_plan,
    execute_undo_plan,
    update_log_after_undo,
    print_undo_plan,
    print_results as print_undo_results,
    ask_confirmation as ask_undo_confirmation,
)

from redo import (
    get_latest_redo_session,
    create_redo_plan,
    validate_redo_plan,
    execute_redo_plan,
    update_log_after_redo,
    print_redo_plan,
    print_results as print_redo_results,
    ask_confirmation as ask_redo_confirmation,
)


def run_preview():
    """
    정리 미리보기 실행

    실제 이동 없이 전체 파일의 이동 예정 경로를 보여준다.
    """
    path_plan = build_path_plan()
    print_path_plan(path_plan)


def run_move(apply=False):
    """
    선택 이동 실행

    apply=False:
    선택한 파일을 dry-run으로 확인한다.

    apply=True:
    선택한 파일을 실제로 이동한다.
    """
    path_plan = build_path_plan()

    print_selectable_plan(path_plan)

    selected_plan = ask_selection(path_plan)

    if not selected_plan:
        print("선택된 파일이 없습니다.")
        return

    print()
    print("선택된 이동 계획")
    print("----------------")

    for item in selected_plan:
        print(f"- {item.get('filename')} -> {item.get('targetFolder')}")

    print()

    if not apply:
        print("현재 모드: DRY RUN")
        print("실제 이동하려면 python3 deskpilot.py move --apply 를 실행하세요.")
        print()

        results = execute_move_plan(selected_plan, dry_run=True)
        print_execution_results(results)
        return

    confirmed = ask_move_confirmation()

    if not confirmed:
        print("파일 이동을 취소했습니다.")
        return

    results = execute_move_plan(selected_plan, dry_run=False)
    print_execution_results(results)

    session = save_move_session(results)

    if session is None:
        print("저장할 이동 로그가 없습니다.")
    else:
        print()
        print("이동 로그를 저장했습니다.")
        print(f"세션 ID: {session['sessionId']}")
        print(f"저장 위치: {get_desktop_path() / APP_FOLDER_NAME / 'move-log.json'}")


def run_undo(apply=False):
    """
    되돌리기 실행

    apply=False:
    되돌리기 dry-run만 실행한다.

    apply=True:
    실제로 파일을 원래 위치로 되돌린다.
    """
    log_data = load_log()
    session = get_latest_undo_session(log_data)

    if session is None:
        print("되돌릴 이동 기록이 없습니다.")
        return

    base_path = Path(session.get("basePath", str(get_desktop_path())))
    undo_plan = create_undo_plan(session)

    print_undo_plan(session, undo_plan)

    errors = validate_undo_plan(undo_plan, base_path)

    if errors:
        print("되돌리기 전에 문제가 발견되었습니다.")
        print("-----------------------------")

        for error in errors:
            print(f"- {error}")

        return

    if not apply:
        print("현재 모드: DRY RUN")
        print("실제 되돌리기를 하려면 python3 deskpilot.py undo --apply 를 실행하세요.")
        print()

        results = execute_undo_plan(undo_plan, dry_run=True)
        print_undo_results(results)
        return

    confirmed = ask_undo_confirmation()

    if not confirmed:
        print("되돌리기를 취소했습니다.")
        return

    results = execute_undo_plan(undo_plan, dry_run=False)
    print_undo_results(results)

    all_success = all(result["status"] == "SUCCESS" for result in results)

    if all_success:
        moved_session = update_log_after_undo(log_data)

        print("move-log.json을 업데이트했습니다.")
        print(f"undoStack -> redoStack 이동 세션: {moved_session['sessionId']}")
    else:
        print("일부 파일 되돌리기에 실패하여 로그를 업데이트하지 않았습니다.")


def run_redo(apply=False):
    """
    앞으로가기 실행

    apply=False:
    앞으로가기 dry-run만 실행한다.

    apply=True:
    실제로 파일을 다시 이동한다.
    """
    log_data = load_log()
    session = get_latest_redo_session(log_data)

    if session is None:
        print("앞으로가기 할 기록이 없습니다.")
        return

    base_path = Path(session.get("basePath", str(get_desktop_path())))
    redo_plan = create_redo_plan(session)

    print_redo_plan(session, redo_plan)

    errors = validate_redo_plan(redo_plan, base_path)

    if errors:
        print("앞으로가기 전에 문제가 발견되었습니다.")
        print("-----------------------------")

        for error in errors:
            print(f"- {error}")

        return

    if not apply:
        print("현재 모드: DRY RUN")
        print("실제 앞으로가기를 하려면 python3 deskpilot.py redo --apply 를 실행하세요.")
        print()

        results = execute_redo_plan(redo_plan, dry_run=True)
        print_redo_results(results)
        return

    confirmed = ask_redo_confirmation()

    if not confirmed:
        print("앞으로가기를 취소했습니다.")
        return

    results = execute_redo_plan(redo_plan, dry_run=False)
    print_redo_results(results)

    all_success = all(result["status"] == "SUCCESS" for result in results)

    if all_success:
        moved_session = update_log_after_redo(log_data)

        print("move-log.json을 업데이트했습니다.")
        print(f"redoStack -> undoStack 이동 세션: {moved_session['sessionId']}")
    else:
        print("일부 파일 앞으로가기에 실패하여 로그를 업데이트하지 않았습니다.")


def run_log():
    """
    move-log.json 상태를 간단히 출력한다.
    """
    log_data = load_log()

    undo_stack = log_data.get("undoStack", [])
    redo_stack = log_data.get("redoStack", [])

    print("move-log.json 상태")
    print("-----------------")
    print(f"version: {log_data.get('version')}")
    print(f"undoStack 개수: {len(undo_stack)}")
    print(f"redoStack 개수: {len(redo_stack)}")
    print()

    if undo_stack:
        latest_undo = undo_stack[-1]

        print("최근 undoStack 세션")
        print("------------------")
        print(f"세션 ID: {latest_undo.get('sessionId')}")
        print(f"실행 시각: {latest_undo.get('executedAt')}")
        print(f"이동 파일 수: {len(latest_undo.get('moves', []))}")
        print()

    if redo_stack:
        latest_redo = redo_stack[-1]

        print("최근 redoStack 세션")
        print("------------------")
        print(f"세션 ID: {latest_redo.get('sessionId')}")
        print(f"실행 시각: {latest_redo.get('executedAt')}")
        print(f"이동 파일 수: {len(latest_redo.get('moves', []))}")
        print()


def parse_args():
    """
    deskpilot.py 명령어를 읽는 함수
    """
    parser = argparse.ArgumentParser(
        description="Desktop 정리 AI 로컬 MVP 실행 도구"
    )

    subparsers = parser.add_subparsers(dest="command")

    subparsers.add_parser(
        "preview",
        help="정리 미리보기를 출력합니다.",
    )

    move_parser = subparsers.add_parser(
        "move",
        help="선택한 파일을 이동합니다.",
    )
    move_parser.add_argument(
        "--apply",
        action="store_true",
        help="실제 이동을 실행합니다.",
    )

    undo_parser = subparsers.add_parser(
        "undo",
        help="최근 이동을 되돌립니다.",
    )
    undo_parser.add_argument(
        "--apply",
        action="store_true",
        help="실제 되돌리기를 실행합니다.",
    )

    redo_parser = subparsers.add_parser(
        "redo",
        help="되돌린 이동을 다시 실행합니다.",
    )
    redo_parser.add_argument(
        "--apply",
        action="store_true",
        help="실제 앞으로가기를 실행합니다.",
    )

    subparsers.add_parser(
        "log",
        help="move-log.json 상태를 출력합니다.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    if args.command == "preview":
        run_preview()

    elif args.command == "move":
        run_move(apply=args.apply)

    elif args.command == "undo":
        run_undo(apply=args.apply)

    elif args.command == "redo":
        run_redo(apply=args.apply)

    elif args.command == "log":
        run_log()

    else:
        print("명령어를 입력해주세요.")
        print()
        print("사용 예시:")
        print("  python3 deskpilot.py preview")
        print("  python3 deskpilot.py move")
        print("  python3 deskpilot.py move --apply")
        print("  python3 deskpilot.py undo")
        print("  python3 deskpilot.py undo --apply")
        print("  python3 deskpilot.py redo")
        print("  python3 deskpilot.py redo --apply")
        print("  python3 deskpilot.py log")
