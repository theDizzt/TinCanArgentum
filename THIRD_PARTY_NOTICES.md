# Third-Party Notices

이 프로젝트는 아래의 오픈소스 패키지와 외부 서비스를 사용합니다.
이 문서는 편의를 위한 목록이며, 각 프로젝트의 원문 라이선스와 각 서비스의
최신 약관이 우선합니다.

## Python 직접 의존성

버전은 `requirements-windows.txt`와 `requirements-ubuntu.txt`를 기준으로
정리했습니다. Python 패키지 자체는 이 저장소에 포함하지 않으며, 설치된
wheel 또는 source distribution에 포함된 저작권 및 라이선스 파일을
삭제하지 마십시오.

| 패키지 | 버전 | 라이선스 | 프로젝트 |
| --- | ---: | --- | --- |
| discord.py | 2.7.1 | MIT | <https://github.com/Rapptz/discord.py> |
| Flask | 3.0.1 | BSD-3-Clause | <https://github.com/pallets/flask> |
| Flask-Compress | 1.14 | MIT | <https://github.com/colour-science/flask-compress> |
| gevent | 23.9.1 | MIT | <https://github.com/gevent/gevent> |
| KoNLPy | 0.6.0 | GPL-3.0-or-later | <https://github.com/konlpy/konlpy> |
| korean-lunar-calendar | 0.4.0 | MIT | <https://github.com/usingsky/korean_lunar_calendar_py> |
| NumPy | 1.26.3 | BSD-3-Clause | <https://github.com/numpy/numpy> |
| openai | 2.30.0 | Apache-2.0 | <https://github.com/openai/openai-python> |
| openpyxl | 3.1.2 | MIT | <https://foss.heptapod.net/openpyxl/openpyxl> |
| pandas | 2.3.3 | BSD-3-Clause | <https://github.com/pandas-dev/pandas> |
| Pillow | 10.2.0 | HPND | <https://github.com/python-pillow/Pillow> |
| pydantic | 2.12.5 | MIT | <https://github.com/pydantic/pydantic> |
| PyNaCl | 1.5.0 | Apache-2.0 | <https://github.com/pyca/pynacl> |
| python-dotenv | 1.0.1 | BSD-3-Clause | <https://github.com/theskumar/python-dotenv> |
| PyYAML | 6.0.1 | MIT | <https://github.com/yaml/pyyaml> |
| requests | 2.25.1 | Apache-2.0 | <https://github.com/psf/requests> |
| scikit-learn | 1.7.2 | BSD-3-Clause | <https://github.com/scikit-learn/scikit-learn> |
| tqdm | 4.66.1 | MPL-2.0 AND MIT | <https://github.com/tqdm/tqdm> |
| tzdata (Windows) | 2026.1 | Apache-2.0 | <https://github.com/python/tzdata> |

이 표는 직접 의존성만 다룹니다. 배포 환경에서 함께 설치되는 전이 의존성도
각자의 라이선스를 유지합니다. 특히 KoNLPy는 GPL-3.0-or-later이므로
KoNLPy를 포함한 애플리케이션을 재배포할 때에는 GPL 의무와 전체 결합물에
미치는 영향을 별도로 검토해야 합니다.

## 외부 API 및 서비스

API는 프로젝트 코드의 MIT License로 제공되는 소프트웨어가 아닙니다.
API 키 발급 및 호출, 입력 데이터 전송, 결과 저장·표시에는 각 제공자의
최신 약관, 개인정보 처리방침, 사용량 제한 및 표시 의무가 적용됩니다.

| 서비스 | 사용 위치 | 적용 문서 |
| --- | --- | --- |
| Discord API / Gateway | `main.py`, Discord cog 전체 | <https://support-dev.discord.com/hc/en-us/articles/8562894815383-Discord-Developer-Terms-of-Service> |
| DeepL API | `fcts/translator.py`, 번역 스크립트 | <https://www.deepl.com/pro-license> |
| OpenAI API | `cogs/Chat.py` | <https://openai.com/policies/services-agreement/> 및 <https://openai.com/policies/> |
| Kakao 음성 합성 API | `cogs/Voice.py` | <https://developers.kakao.com/terms/ko/site-terms-20241223> 및 <https://developers.kakao.com/docs/in/voice/rest-api> |
| 국립국어원 우리말샘 Open API | `fcts/koreansearch.py` | <https://opendict.korean.go.kr/> 및 <https://www.korean.go.kr/front/page/pageView.do?mn_id=105&page_id=P000189> |
| Free Dictionary API | `fcts/koreansearch.py` | <https://github.com/meetDeveloper/freeDictionaryAPI> (서버 구현 GPL-3.0, 응답 데이터 권리는 별도 확인 필요) |
| NAVER Papago API (백업 코드, 서비스 종료) | `fcts/backup/` | <https://developers.naver.com/products/terms/> |

서비스 약관은 변경될 수 있습니다. 특히 백업 폴더의 NAVER Papago 개발자센터
API는 제공이 종료된 엔드포인트이므로 활성 기능으로 간주해서는 안 됩니다.

## 글꼴

글꼴별 상태와 OFL 원문은 `font/LICENSES/README.md` 및
`font/LICENSES/OFL-1.1.txt`에 있습니다. OFL이 확인된 글꼴만 해당
라이선스에 따라 재배포할 수 있습니다. 나머지 글꼴에는 OFL을 적용하지
마십시오.

## 이미지, 게임 데이터 및 기타 파일

이미지·데이터 파일과 소스 코드에 직접 연결된 외부 콘텐츠의 상태는
`ASSET_LICENSES.md`에 정리했습니다. 출처 또는 재배포 허가가 확인되지 않은
자료는 프로젝트 MIT License의 대상이 아닙니다.

## 상표

Discord, DeepL, OpenAI, Kakao, NAVER, Pokémon, Riot Games,
League of Legends, Mabinogi 및 기타 제품명과 상표는 각 권리자의
소유입니다. 이 저장소의 라이선스는 상표 사용권이나 제휴 관계를 부여하지
않습니다.
