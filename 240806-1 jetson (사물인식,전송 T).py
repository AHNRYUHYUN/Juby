import cv2
import numpy as np
import requests

# 서버 URL 설정
server_url = 'http://192.168.0.2:8000/accountapp/harvest/'  # 서버 URL을 입력하세요

# 카메라 초기화
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1440)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 색상 기반 딸기 인식 (빨간색 범위 설정)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)  # BGR에서 HSV로 변환 [명암은 COLOR_BGR2GRAY]
    
    # 딸기의 색상 범위 (Hue: 0-10, Saturation: 100-255, Value: 100-255)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    
    # 빨간색 범위를 마스크로 생성
    mask = cv2.inRange(hsv_frame, lower_red, upper_red)

    # 마스크를 사용하여 원본 이미지에서 빨간색 부분만 추출
    result = cv2.bitwise_and(frame, frame, mask=mask)

    # 딸기 윤곽선 찾기
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    for contour in contours:
        if cv2.contourArea(contour) > 500:  # 면적이 500 이상인 경우만 인식
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

    # 딸기가 인식된 경우에만 이미지를 서버로 전송
    if len(contours) > 0:
        # 인식된 이미지를 서버로 전송
        _, img_encoded = cv2.imencode('.jpg', frame)
        files = {'file': ('strawberry.jpg', img_encoded.tobytes())}

        try:
            response = requests.post(server_url, files=files)
            print('서버 응답:', response.status_code)
        except Exception as e:
            print('서버 전송 오류:', e)

    # 결과 영상 표시
    cv2.imshow('Fucking Potato', frame)

    # 'q' 키를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
