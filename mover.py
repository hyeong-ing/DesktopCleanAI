from pathlib import Path

from path_planner import build_path_plan


def create_result(item, status, message):
    """
    이동 실행 결과를 딕셔너리로 만드는 함수

    나중에 move-log.json을 만들 때도 이런 구조를 사용할 수 있다.
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


def execute_move_plan(path_plan, dry_run=True):
    """
    이동 계획을 실행하는 함수

    지금 챕터에서는 dry_run=True만 사용한다.
    즉, 실제 파일을 이동하지 않고 이동 예정 정보만 결과로 만든다.
    """
    results = []

    for item in path_plan:
        action = item.get("action")
        original_path_text = item.get("originalPath")
        target_path_text = item.get("targetPath")

        # KEEP 항목은 이동하지 않는다.
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

        # 실제 이동은 다음 챕터에서 구현한다.
        results.append(
            create_result(
                item,
                "NOT_IMPLEMENTED",
                "실제 이동 기능은 아직 구현하지 않았습니다.",
            )
        )

    return results


def print_execution_results(results):
    """
    dry-run 실행 결과를 터미널에 출력하는 함수
    """
    print("Dry Run 이동 실행 결과")
    print("--------------------")

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


if __name__ == "__main__":
    path_plan = build_path_plan()

    # 현재 챕터에서는 반드시 dry_run=True로 실행한다.
    results = execute_move_plan(path_plan, dry_run=True)

    print_execution_results(results)
