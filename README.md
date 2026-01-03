````md
# JUBY (SmartFarm Mobile Sensing & Harvest Support)

스마트팜 내부 **환경 편차(특히 유속 차이로 인한 온도 분포 불균형)** 문제를 해결하기 위해, **이동형 로봇**이 농장 전역의 데이터를 수집하고(온/습도·토양 등), 서버에서 저장·분석·시각화하며, 수확 시점 판단까지 확장 가능한 통합 시스템입니다.

---

## Project Explanation

기존 스마트팜은 구역별 환경 편차가 발생하기 쉽고(유속 차이 → 열 전달 효율 변화 → 온도 불균일), 이를 보정하려면 많은 고정형 센서가 필요합니다.
**JUBY**는 **이동형 로봇 기반 데이터 수집**으로 센서 설치 비용을 줄이면서, 데이터 공백을 최소화(보간/가상센서 확장)하고, 데이터 기반으로 생장환경 최적화/운영 효율을 높이는 것을 목표로 합니다.

### 기대 효과
- **초기 설비 비용 절감**: 고정형 센서 다수 → 이동형 로봇으로 대체
- **데이터 신뢰성 향상**: 공백 최소화/예측·실측 비교로 품질 개선
- **운영 효율/에너지 절약**: 불필요한 제어·소비를 줄이고 균일 환경 유지
- **생산성/품질 향상**: 균일한 환경 조성으로 성장 속도/품질 개선

---

## Key Features

- **스마트팜 환경 데이터 수집**
  - 온도/습도/조도/토양수분 등(구성에 따라 확장)
  - 로봇 이동 기반 구역별 데이터 기록
- **데이터 저장 및 API 제공**
  - Django REST Framework + MySQL
- **대시보드/알림 확장**
  - 실시간 시각화/이상치 알림(확장 지점)
- **수확 기능(확장)**
  - 이미지 기반 성숙도 예측(예: YOLO 기반 파이프라인)
- **가상 센서/예측 모델(확장)**
  - 공백 보정 및 장기 추세 예측

---

## System Architecture

```text
[IoT Sensors / Robot]
      ↓ (MQTT or HTTP)
   [Gateway]
      ↓
[Django REST API Server] ── [MySQL DB]
      ↓
[Analysis Engine / Virtual Sensor Model]
      ↓
[Dashboard / Alert / Automation]
````

---

## Tech Stack

### Backend

* Django REST Framework (Python)
* MySQL
* REST API (JSON)

### Edge / Vision (성숙도 추정)

* YOLOv5 기반 추론 파이프라인(구성에 따라 변경 가능)

---

## Specification

### Edge AI Board (Vision)

|   Item  | Spec                          |
| :-----: | :---------------------------- |
|  Board  | NVIDIA Jetson Nano (4GB RAM)  |
| JetPack | 4.6.4 (Development Kit 4.6.1) |
|    OS   | Ubuntu 18.04 LTS              |

> 참고: 기존 표기(18.6.04)는 일반적으로 **18.04 LTS**로 정리하는 것을 권장합니다.

---

## Installed (version) — YOLOv5 (Jetson 예시)

|    Program   |  Version |
| :----------: | :------: |
|      SSH     |    any   |
|     jtop     |    any   |
|      ufw     |    any   |
|    Python    |   3.9.1  |
|    OpenCV    |   4.5.5  |
|     CUDA     | 10.2.300 |
| CUDA Toolkit |   10.2   |
|    PyTorch   |   1.8.0  |
|  TorchVision |   0.9.0  |
|    Cython    |  0.29.36 |

---

## How to Use (Robot)

1. 이동 경로대로 라인트레이서가 따라갈 수 있도록 바닥에 **검은색 테이프**를 적절한 두께로 테이핑합니다.
2. 초기 위치와 정지 위치를 위해 **양쪽 IR 센서가 동시에 인식**할 만큼 두껍게 설치합니다.

   * 이때 IR 센서에 인식되는 시간이 **약 1초 이상** 유지되도록 두께를 알맞게 정합니다.
3. 테이핑을 마치면 적절한 위치에서 IR 센서가 알맞게 위치하도록 로봇 본체를 조정한 뒤 **[모니터링 모드]** 또는 **[수확 모드]**를 실행합니다.
4. 적절한 시기마다 원격 또는 직접 조정으로 수확 모드를 실행합니다.

---

## WARNING

1. 라인 이탈 시 **15초 후 정지**되도록 설정되어 있습니다.

   * [모니터링 모드]에서 라인 이탈이 발생하면 변동이 거의 없는 데이터를 계속 수집할 수 있으므로, 상황 인지 후 적절한 위치로 이동시켜 재가동해주세요.
2. 정지 구간에서 약 **4초간** 온습도 센서의 높낮이를 조절 후, **4회 주기마다 최하단 높이로 초기화**되는 것이 정상 동작입니다.

   * 초기화되지 않는다면 제작자에게 문의 바랍니다.
3. 해당 제품을 재현하기 전에 권장 버전 외 환경에서는 **호환성 체크 후 진행**을 권장합니다.

---

## Parts

* Raspberry Pi 3 Model B+
* DC motor drive board: AT8236 module (compact), L298N motor driver
* SMPS: LRS-350-12
* WHEELTEC DC reduction motor 12V
* Arduino Actuator 150mm 12V
* Level converter 3.3V → 5V
* TCRT5000 IR sensor
* NEXT 208PB-UPS portable battery

---

## Backend Setup

### Install

```bash
# (권장) 가상환경 생성
python -m venv venv
source venv/bin/activate  # Windows: venv\\Scripts\\activate

pip install -r requirements.txt
```

### Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

### Run Server

```bash
python manage.py runserver 0.0.0.0:8000
```

---

## Server Libraries

> 아래 목록은 README에 그대로 넣을 경우 너무 길어질 수 있습니다.
> 보통은 `requirements.txt`로 관리하고, README에는 설치 방법만 유지하는 것을 권장합니다.

<details>
<summary><b>Click to expand full pip list</b></summary>

```text
absl-py==2.1.0
asgiref==3.8.1
astunparse==1.6.3
awscli==1.35.19
boto3==1.35.53
botocore==1.35.53
certifi==2024.7.4
chardet==5.2.0
charset-normalizer==3.3.2
click==8.1.7
colorama==0.4.6
contourpy==1.3.0
cycler==0.12.1
Django==5.0.7
django-cors-headers==4.4.0
django-request-logging==0.7.5
djangorestframework==3.15.2
docker==7.1.0
docutils==0.16
et-xmlfile==1.1.0
filelock==3.16.1
flatbuffers==24.3.25
fonttools==4.54.1
fsspec==2024.10.0
gast==0.6.0
google-pasta==0.2.0
grpcio==1.64.1
h5py==3.11.0
idna==3.7
jaraco.classes==3.4.0
jaraco.context==6.0.1
Jinja2==3.1.4
jmespath==1.0.1
keras==3.4.1
keyring==8.7
keyrings.alt==5.0.2
kiwisolver==1.4.7
libclang==18.1.1
Markdown==3.6
markdown-it-py==3.0.0
MarkupSafe==2.1.5
matplotlib==3.9.2
mdurl==0.1.2
ml-dtypes==0.4.0
more-itertools==10.5.0
mpmath==1.3.0
mysqlclient==2.2.4
namex==0.0.8
networkx==3.4.2
numpy==1.26.4
opencv-python==4.10.0.84
openpyxl==3.1.5
opt-einsum==3.3.0
optree==0.12.1
packaging==24.1
pandas==2.2.2
pillow==11.0.0
protobuf==4.25.3
psutil==6.1.0
py-cpuinfo==9.0.0
pyasn1==0.6.1
Pygments==2.18.0
pyparsing==3.2.0
python-dateutil==2.9.0.post0
pytz==2024.1
pywin32==308
pywin32-ctypes==0.2.3
PyYAML==6.0.2
requests==2.32.3
rich==13.7.1
rsa==4.7.2
ruamel.yaml==0.18.6
ruamel.yaml.clib==0.2.12
s3transfer==0.10.3
scipy==1.14.1
seaborn==0.13.2
setuptools==70.3.0
six==1.16.0
sqlparse==0.5.1
sympy==1.13.1
tabulate==0.9.0
tensorboard==2.17.0
tensorboard-data-server==0.7.2
tensorflow==2.17.0
tensorflow-intel==2.17.0
termcolor==2.4.0
torch==2.5.1
torchvision==0.20.1
tqdm==4.66.6
typing_extensions==4.12.2
tzdata==2024.1
ultralytics==8.3.27
ultralytics-thop==2.0.10
urllib3==2.2.2
voluptuous==0.15.2
Werkzeug==3.0.3
wheel==0.43.0
wrapt==1.16.0
yolo==0.3.1
```

</details>

---

## API Documentation

### Member

* **Method**: POST
* **URL**: `/create_member/`
* **Description**: 회원 생성

**Request Body**

```json
{
  "member_ID": "user@example.com",
  "password": "securepassword"
}
```

---

### SmartFarm

* **Method**: POST
* **URL**: `/create_smart_farm/`
* **Description**: 스마트 농장 생성

**Request Body**

```json
{
  "farm_name": "Farm1",
  "member": 1,
  "robot_id": "1234",
  "crop": "Tomatoes"
}
```

---

### JubyAdministrator

* **Method**: POST
* **URL**: `/create_admin/`
* **Description**: 관리자 생성

**Request Body**

```json
{
  "admin_ID": "admin@example.com",
  "admin_password": "adminpassword"
}
```

---

### Robot

* **Method**: POST
* **URL**: `/create_robot/`
* **Description**: 로봇 생성

**Request Body**

```json
{
  "member": 1,
  "farm": 1,
  "area": "Area1",
  "height": "1.5m",
  "temperature": "25C",
  "humidity": "60%",
  "soil_temperature": "20C",
  "soil_humidity": "55%"
}
```

---

### Harvest

* **Method**: POST
* **URL**: `/create_harvest/`
* **Description**: 수확 정보 생성 및 이미지 기반 성숙도 예측

**Request Body**

```json
{
  "image": "<파일>",
  "robot_id": 1,
  "farm_name": "Farm1",
  "member_id": "user@example.com"
}
```

---

## CODE Interpret (TODO)

* [ ] 모듈별 역할 정리
* [ ] 함수 전달인자/반환값 정리
* [ ] 로봇(라인트레이서/센서) 제어 흐름 정리
* [ ] 서버(요청→뷰→시리얼라이저→모델) 흐름 정리

---

## Diagrams / Docs (Add Files)

README에서 아래 경로로 파일을 연결하는 것을 권장합니다.

* 회로도: `docs/circuits/` (e.g., `circuit_diagram.png` or `.pdf`)
* 부품 제원: `docs/parts/` (e.g., `BOM.xlsx`, `datasheets/`)
* 기능 구조도: `docs/diagrams/` (e.g., `system_overview.png`)

---

## LICENSE

JUNGBU Univercity Student ID Number 20 한승준

---

## Status

**Free**

---

## Contributors

* 92017011 한승준
* 92016902 이은호
* 92016847 안류현
* (지도교수: 이성규)

```
```
