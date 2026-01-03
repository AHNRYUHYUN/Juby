import cv2
import numpy as np
import requests
import threading
import time

# 서버 URL 설정
server_url = 'http://192.168.0.2:8000/accountapp/harvest/'

# 카메라 초기화
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

# 전송할 이미지를 저장할 큐
image_queue = []
lock = threading.Lock()

def send_images():
    while True:
        if image_queue:
            lock.acquire()
            frame = image_queue.pop(0)  # 큐에서 이미지 가져오기
            lock.release()

            # 인식된 이미지를 서버로 전송
            _, img_encoded = cv2.imencode('.jpg', frame)
            files = {'file': ('strawberry.jpg', img_encoded.tobytes())}

            try:
                response = requests.post(server_url, files=files)
                print('서버 응답:', response.status_code)
            except Exception as e:
                print('서버 전송 오류:', e)
        else:
            time.sleep(0.1)  # 큐가 비어있으면 잠시 대기

# 이미지 전송 스레드 시작
threading.Thread(target=send_images, daemon=True).start()

while True:
    ret, frame = cap.read()
    if not ret:
        break

    # 색상 기반 딸기 인식 (빨간색 범위 설정)
    hsv_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 100, 100])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv_frame, lower_red, upper_red)

    # 딸기 윤곽선 찾기
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) > 500:  # 면적이 500 이상인 경우만 인식
            (x, y, w, h) = cv2.boundingRect(contour)
            cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

            # 딸기가 인식된 경우에만 이미지를 큐에 추가
            lock.acquire()
            image_queue.append(frame.copy())  # 현재 프레임을 큐에 추가
            lock.release()

    # 결과 영상 표시
    cv2.imshow('Fucking Potato', frame)

    # 'q' 키를 눌러 종료
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

# 자원 해제
cap.release()
cv2.destroyAllWindows()
