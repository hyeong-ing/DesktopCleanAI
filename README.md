# DeskPilot Local MVP

DeskPilot은 사용자의 Desktop 파일을 자동으로 분석하고, 적절한 폴더로 이동할 수 있도록 도와주는 로컬 파일 정리 도구입니다.

현재 버전은 실제 Desktop 전체가 아니라 테스트용 폴더인 `test_desktop`만 대상으로 동작합니다.

---

## 현재 개발 단계

현재는 **AI 서버, OCR, PDF 분석 없이 로컬 규칙 기반 MVP**를 구현한 상태입니다.

### 구현된 기능

* 테스트 Desktop 폴더 스캔
* 정리 대상 파일 스캔
* 이동 목적지 폴더 스캔
* 파일명 앞 `[태그]` 기반 분류
* `rules.txt` 기반 키워드 분류
* 한글 파일명 정규화 처리
* `archive` fallback 처리
* 이동 경로 미리보기
* dry-run 이동 확인
* 실제 파일 이동
* `move-log.json` 저장
* 되돌리기 undo
* 앞으로가기 redo
* 선택한 파일만 이동
* 상태 점검 doctor 명령어
* 통합 실행 파일 `deskpilot.py`

---

## 폴더 구조

테스트용 Desktop 폴더는 다음 위치에 있어야 합니다.

```text
~/Desktop/test_desktop
```

예시 구조:

```text
test_desktop/
├── .deskpilot/
│   ├── rules.txt
│   └── move-log.json
├── archive/
├── project/
├── school/
├── study/
└── 정리 대상 파일들...
```

---

## 주요 폴더 설명

| 폴더명            | 설명                     |
| -------------- | ---------------------- |
| `test_desktop` | 테스트용 가짜 Desktop 폴더     |
| `.deskpilot`   | 앱 설정 및 로그 저장 폴더        |
| `archive`      | 분류되지 않은 파일을 보내는 보관함 폴더 |
| `school`       | 학교 관련 파일 이동 폴더         |
| `study`        | 공부 관련 파일 이동 폴더         |
| `project`      | 프로젝트 관련 파일 이동 폴더       |

---

## 주요 파일 설명

| 파일명                 | 역할                     |
| ------------------- | ---------------------- |
| `config.py`         | 프로젝트 설정값 관리            |
| `scanner.py`        | 파일과 폴더 스캔              |
| `rules.py`          | `rules.txt` 읽기         |
| `classifier.py`     | 태그와 `rules.txt` 기준 분류  |
| `planner.py`        | 파일별 정리 계획 생성           |
| `path_planner.py`   | 실제 이동될 경로 계산           |
| `mover.py`          | 파일 이동 실행               |
| `log_store.py`      | `move-log.json` 저장과 읽기 |
| `undo.py`           | 되돌리기 기능                |
| `redo.py`           | 앞으로가기 기능               |
| `selected_mover.py` | 선택한 파일만 이동             |
| `doctor.py`         | 프로젝트 상태 점검             |
| `deskpilot.py`      | 통합 실행 파일               |

---

## rules.txt 사용법

`rules.txt`는 아래 위치에 둡니다.

```text
~/Desktop/test_desktop/.deskpilot/rules.txt
```

예시:

```text
school: 정보처리기사, 서술형, 기사
study: 스프링, 강의, 공부, 기본편
project: project, api, test, lotto
```

파일명에 키워드가 포함되면 해당 폴더로 이동 추천됩니다.

예:

```text
스프링기본편.png -> study
정보처리기사 정리본.pdf -> school
lotto-api-test.java -> project
```

---

## 파일명 태그 규칙

파일명 맨 앞에 `[폴더명]`을 붙이면 해당 폴더로 우선 분류됩니다.

예:

```text
[school]정보처리기사 정리본.pdf -> school
[study]스프링 기본편.png -> study
[project]lotto-api-test.java -> project
```

이동 후에는 파일명 앞의 태그가 제거됩니다.

예:

```text
[school]정보처리기사 정리본.pdf
```

이동 후:

```text
school/정보처리기사 정리본.pdf
```

---

## 명령어 사용법

### 1. 상태 점검

```bash
python3 deskpilot.py doctor
```

프로젝트 상태를 점검합니다.

확인 항목:

* `test_desktop` 폴더 존재 여부
* `.deskpilot` 폴더 존재 여부
* `rules.txt` 존재 여부
* `archive` 폴더 존재 여부
* `move-log.json` 정상 여부
* 이동 목적지 폴더 목록

---

### 2. 이동 경로 미리보기

```bash
python3 deskpilot.py preview
```

실제 이동 없이 파일이 어디로 이동될 예정인지 보여줍니다.

---

### 3. 선택 이동 Dry Run

```bash
python3 deskpilot.py move
```

이동할 파일을 번호로 선택하고, 실제 이동 없이 dry-run으로 확인합니다.

입력 예시:

```text
all
none
1,3
2-4
1,3-5
```

입력 의미:

| 입력      | 의미                |
| ------- | ----------------- |
| `all`   | 전체 선택             |
| `none`  | 선택 안 함            |
| `1,3`   | 1번과 3번만 선택        |
| `2-4`   | 2번부터 4번까지 선택      |
| `1,3-5` | 1번, 3번, 4번, 5번 선택 |

---

### 4. 선택 이동 실제 실행

```bash
python3 deskpilot.py move --apply
```

선택한 파일을 실제로 이동합니다.

실제 이동 전 확인 문구가 나옵니다.

```text
정리하기
```

위 문구를 정확히 입력해야 이동됩니다.

---

### 5. 되돌리기 Dry Run

```bash
python3 deskpilot.py undo
```

가장 최근 이동 기록을 기준으로 되돌리기 예정 경로를 확인합니다.

---

### 6. 되돌리기 실제 실행

```bash
python3 deskpilot.py undo --apply
```

가장 최근 이동 기록을 실제로 되돌립니다.

확인 문구:

```text
되돌리기
```

---

### 7. 앞으로가기 Dry Run

```bash
python3 deskpilot.py redo
```

되돌린 이동 기록을 다시 앞으로가기 할 수 있는지 확인합니다.

---

### 8. 앞으로가기 실제 실행

```bash
python3 deskpilot.py redo --apply
```

되돌린 이동 기록을 실제로 다시 이동합니다.

확인 문구:

```text
앞으로가기
```

---

### 9. 로그 상태 확인

```bash
python3 deskpilot.py log
```

`move-log.json` 상태를 간단히 출력합니다.

확인 항목:

* version
* undoStack 개수
* redoStack 개수
* 최근 undo 세션
* 최근 redo 세션

---

## move-log.json 구조

파일 이동이 성공하면 `.deskpilot/move-log.json`에 기록됩니다.

예시:

```json
{
  "version": 1,
  "undoStack": [
    {
      "sessionId": "20260614-190450",
      "executedAt": "2026-06-14T19:04:50",
      "basePath": "/Users/user/Desktop/test_desktop",
      "moves": [
        {
          "filename": "스프링 선택 테스트.md.rtf",
          "originalPath": "/Users/user/Desktop/test_desktop/스프링 선택 테스트.md.rtf",
          "movedPath": "/Users/user/Desktop/test_desktop/study/스프링 선택 테스트.md.rtf",
          "source": "RULES_TXT",
          "status": "SUCCESS"
        }
      ]
    }
  ],
  "redoStack": []
}
```

---

## undo / redo 동작 방식

### undo

최근 이동 기록을 기준으로 파일을 원래 위치로 되돌립니다.

```text
movedPath -> originalPath
```

성공하면 로그는 다음처럼 이동합니다.

```text
undoStack -> redoStack
```

### redo

되돌린 이동 기록을 다시 실행합니다.

```text
originalPath -> movedPath
```

성공하면 로그는 다음처럼 이동합니다.

```text
redoStack -> undoStack
```

---

## 안전장치

현재 MVP에는 다음 안전장치가 있습니다.

* 기본 실행은 dry-run입니다.
* 실제 이동은 `--apply` 옵션이 있어야 실행됩니다.
* 실제 이동 전 확인 문구를 입력해야 합니다.
* `test_desktop` 밖의 파일은 이동하지 않습니다.
* 대상 경로에 같은 이름의 파일이 있으면 덮어쓰지 않습니다.
* 실제 이동 성공 기록만 `move-log.json`에 저장합니다.
* 되돌리기와 앞으로가기는 로그를 기반으로 동작합니다.
* `.deskpilot` 폴더는 이동 목적지에서 제외됩니다.
* 숨김 파일과 시스템 파일은 정리 대상에서 제외됩니다.

---

## 정리 대상 제외 파일

다음 파일들은 정리 대상에서 제외됩니다.

```text
.DS_Store
desktop.ini
Thumbs.db
rules.txt
move-log.json
```

---

## 이동 목적지 제외 폴더

다음 폴더들은 이동 목적지에서 제외됩니다.

```text
.deskpilot
deskpilot
__pycache__
```

---

## 현재 한계

현재 버전에는 아직 다음 기능이 없습니다.

* GUI 화면
* 실제 Desktop 전체 대상 실행
* AI 서버 연동
* PDF 텍스트 추출
* 이미지 OCR 분석
* 스캔 문서 자동 분류
* Cloud Run 배포
* Kubernetes 배포
* 자동 백그라운드 감시

---

## 앞으로 추가할 기능

예정 기능:

* 코드 폴더 구조 정리
* 테스트 코드 작성
* GUI 또는 간단한 데스크톱 앱 화면
* AI 서버 인터페이스 추가
* PDF 첫 페이지 텍스트 추출
* 이미지 OCR 분석
* 스캔 문서 자동 분류
* Cloud Run 버전
* Kubernetes 버전

---

## 개발 원칙

이 프로젝트의 핵심 원칙은 다음과 같습니다.

```text
AI 또는 프로그램이 파일을 마음대로 이동하지 않는다.
사용자가 미리보기로 확인하고 승인한 뒤에만 로컬에서 실제 이동한다.
```

현재 로컬 MVP는 이 원칙을 지키기 위해 dry-run, 확인 문구, 로그 저장, undo/redo 기능을 포함합니다.
