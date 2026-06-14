import argparse

from path_planner import build_path_plan
from mover import execute_move_plan, print_execution_results, ask_confirmation
from log_store import save_move_session
from scanner import get_desktop_path
from config import APP_FOLDER_NAME


def print_selectable_plan(path_plan):
    """
    사용자가 선택할 수 있도록 이동 계획을 번호와 함께 출력하는 함수
    """
    print("선택 이동 미리보기")
    print("----------------")

    if not path_plan:
        print("정리할 파일이 없습니다.")
        return

    for index, item in enumerate(path_plan, start=1):
        filename = item.get("filename")
        action = item.get("action")
        target_folder = item.get("targetFolder")
        source = item.get("source")
        confidence = item.get("confidence")
        reason = item.get("reason")

        if action == "MOVE":
            print(
                f"{index}. [이동 예정] {filename} -> {target_folder} "
                f"/ 출처: {source} "
                f"/ 확신도: {confidence} "
                f"/ 이유: {reason}"
            )
        else:
            print(
                f"{index}. [남기기] {filename} "
                f"/ 출처: {source} "
                f"/ 확신도: {confidence} "
                f"/ 이유: {reason}"
            )

    print()
    print("입력 예시:")
    print("  all      전체 선택")
    print("  none     선택 안 함")
    print("  1,3      1번과 3번만 선택")
    print("  2-4      2번부터 4번까지 선택")
    print("  1,3-5    1번, 3번, 4번, 5번 선택")
    print()


def parse_selection(selection_text, max_number):
    """
    사용자가 입력한 선택 문자열을 번호 set으로 바꾸는 함수

    예:
    all      -> {1, 2, 3, ...}
    none     -> set()
    1,3      -> {1, 3}
    2-4      -> {2, 3, 4}
    1,3-5    -> {1, 3, 4, 5}
    """
    selection_text = selection_text.strip().lower()

    if selection_text == "all":
        return set(range(1, max_number + 1))

    if selection_text == "none" or selection_text == "":
        return set()

    selected_numbers = set()

    parts = selection_text.split(",")

    for part in parts:
        part = part.strip()

        if part == "":
            continue

        # 범위 선택 처리: 2-4
        if "-" in part:
            start_text, end_text = part.split("-", 1)

            if not start_text.strip().isdigit() or not end_text.strip().isdigit():
                raise ValueError(f"잘못된 범위 입력입니다: {part}")

            start = int(start_text.strip())
            end = int(end_text.strip())

            if start > end:
                raise ValueError(f"범위 시작 번호가 끝 번호보다 큽니다: {part}")

            for number in range(start, end + 1):
                if number < 1 or number > max_number:
                    raise ValueError(f"선택 번호가 범위를 벗어났습니다: {number}")

                selected_numbers.add(number)

        # 단일 번호 선택 처리: 3
        else:
            if not part.isdigit():
                raise ValueError(f"잘못된 번호 입력입니다: {part}")

            number = int(part)

            if number < 1 or number > max_number:
                raise ValueError(f"선택 번호가 범위를 벗어났습니다: {number}")

            selected_numbers.add(number)

    return selected_numbers


def filter_selected_plan(path_plan, selected_numbers):
    """
    사용자가 선택한 번호에 해당하는 이동 계획만 남기는 함수
    """
    selected_plan = []

    for index, item in enumerate(path_plan, start=1):
        if index in selected_numbers:
            selected_plan.append(item)

    return selected_plan


def ask_selection(path_plan):
    """
    사용자에게 이동할 파일 번호를 입력받는 함수
    """
    if not path_plan:
        return []

    while True:
        selection_text = input("이동할 번호를 입력하세요: ").strip()

        try:
            selected_numbers = parse_selection(selection_text, len(path_plan))
            return filter_selected_plan(path_plan, selected_numbers)

        except ValueError as error:
            print(f"입력 오류: {error}")
            print("다시 입력해주세요.")
            print()


def parse_args():
    """
    터미널 명령어 옵션을 읽는 함수

    기본:
    python3 selected_mover.py
    -> 선택 후 dry-run

    실제 이동:
    python3 selected_mover.py --apply
    -> 선택 후 확인 문구 입력 시 실제 이동
    """
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--apply",
        action="store_true",
        help="선택한 파일을 실제로 이동합니다.",
    )

    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()

    path_plan = build_path_plan()

    print_selectable_plan(path_plan)

    selected_plan = ask_selection(path_plan)

    if not selected_plan:
        print("선택된 파일이 없습니다.")
    else:
        print()
        print("선택된 이동 계획")
        print("----------------")

        for item in selected_plan:
            print(f"- {item.get('filename')} -> {item.get('targetFolder')}")

        print()

        if not args.apply:
            print("현재 모드: DRY RUN")
            print("실제 이동하려면 python3 selected_mover.py --apply 를 실행하세요.")
            print()

            results = execute_move_plan(selected_plan, dry_run=True)
            print_execution_results(results)

        else:
            confirmed = ask_confirmation()

            if not confirmed:
                print("파일 이동을 취소했습니다.")
            else:
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
