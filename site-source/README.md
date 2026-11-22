# 아라인사이트 Pages CMS 운영

[Pages CMS](https://app.pagescms.org/)에서 GitHub로 로그인한 뒤 noonisstart/arainsight-homepage 저장소와 arainsight-pages-cms 브랜치를 선택합니다. 병합 후 운영 편집은 main에서 진행합니다. 기존 저장소 접근 권한으로 선택 가능한지 먼저 확인하세요.

- 인사이트, 교육 프로그램, 프로젝트·실적에서 새 항목을 작성하거나 기존 항목을 엽니다. 기존 카테고리에 추가할 때 같은 카테고리 URL과 이름을 씁니다.
- URL은 영문 소문자, 숫자, 하이픈으로 작성합니다. 발행 후 상세 URL을 바꾸면 공유한 링크도 달라집니다.
- 대표 사진에서 파일을 선택하거나 업로드하고 사진의 대체 텍스트를 적습니다. 프로젝트에는 추가 사진도 넣을 수 있습니다.
- 프로젝트 실적은 확인된 내용으로 바꾼 뒤 샘플 표시를 해제합니다. 인사이트는 게시일과 예시 여부를 설정합니다.
- 메인 화면·사이트 설정에서 헤드라인, 사진, 상담 문구, 테마와 글꼴을 바꿉니다. FAQ는 문의 페이지에 표시됩니다.
- 저장하면 선택한 GitHub 브랜치에 커밋됩니다. Actions에서 빌드 결과를 확인하고 arainsight-preview 파일을 내려받아 index.html을 엽니다.
- 문의 접수는 준비 중이며 이 버전은 개인 연락처를 수집하지 않습니다.

## 배포와 확인

검토 브랜치에서 생성된 사이트를 확인한 뒤 병합 여부를 결정합니다. 공개 운영 시 저장소의 Pages 설정에서 GitHub Actions를 선택하고, 저장소 Actions 변수 ARAIN_PAGES_DEPLOY를 true로 설정하면 이후 main 편집이 재빌드 및 배포됩니다. 비공개 저장소의 Pages 사용 가능 여부와 공개 정책을 먼저 확인하세요.

로컬 확인은 저장소 루트에서 python site-source/build.py --output dist 및 python site-source/verify.py dist 를 실행합니다.

## 상담 접수 연결

Formspree에서 수신 이메일 확인과 양식 생성 후 공개 폼 주소를 content/contact.json의 formspree_endpoint에 입력합니다. 실제 운영 기준의 개인정보 보유·이용 기간을 retention_period에 입력합니다. 외부 서비스의 개인정보 처리 방식과 운영 안내를 확정한 후 연결합니다. 두 값이 준비되기 전에는 입력과 제출이 비활성화됩니다. 적용 후 이름과 전화번호 대신 합성 테스트 값을 사용해 양식 기록과 수신함 도착을 확인하세요.
