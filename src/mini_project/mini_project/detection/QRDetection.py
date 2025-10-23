import rclpy
from rclpy.node import Node
import cv2
from cv_bridge import CvBridge
import time

from qr_interfaces.srv import GetTargetRoom


class QRDetectorCameraNode(Node):
    def __init__(self):
        super().__init__('qr_detector_camera_node')

        self.detected_qr_ids = []
        self.detected_target_rooms = []

        self.last_received_time = time.time()
        self.connected = True
        self.timeout_sec = 5.0
        self.last_qr_time = 0

        self.bridge = CvBridge()
        self.qr_detector = cv2.QRCodeDetector()

        # /robot8/
        self.cli = self.create_client(
            GetTargetRoom,
            '/target_room'
        )

        while not self.cli.wait_for_service(timeout_sec=1.0):
            self.get_logger().info(f'service not available')

        self.get_logger().info('✅ QR Detector + Camera 노드 시작됨.')
        self.setup_camera() 
        #setup이랑 카메라 순서바꿔둠
        self.timer = self.create_timer(0.1, self.process_camera_frame)


    def setup_camera(self):
        ip_address = input('IP address: ')
        self.cap = cv2.VideoCapture(f'http://{ip_address}:8080/video')

        while not self.cap.isOpened():
            self.get_logger().warn('📷 카메라 연결 실패. 재시도 중...')
            time.sleep(1)
            self.cap = cv2.VideoCapture(f'http://{ip_address}:8080/video')

        self.get_logger().info('📷 카메라 연결 성공.')

    # def check_connection(self):
    #     elapsed = time.time() - self.last_received_time
    #     if elapsed > self.timeout_sec and self.connected:
    #         self.connected = False
    #         self.get_logger().warn(f'❌ {self.timeout_sec}초 이상 수신 없음 → 카메라 연결 끊김 감지')

        # self.process_camera_frame()

    def process_camera_frame(self):
        current_time = time.time()
        if current_time - self.last_qr_time < 1.0:
            return

        ret, frame = self.cap.read()
        if not ret or frame is None:
            self.get_logger().warn('⚠️ 프레임 수신 실패')
            return

        frame = cv2.resize(frame, (640, 480), interpolation=cv2.INTER_NEAREST)
        retval, decoded_info, points, _ = self.qr_detector.detectAndDecodeMulti(frame)

        # cv2.imshow('Webcam Stream', frame)
        # cv2.waitKey(30)

        if retval:
            self.get_logger().info(f"🌀 QR 감지됨 (개수: {len(decoded_info)})")
            for idx, info in enumerate(decoded_info):
                if info:
                    full_str = info.strip()
                    self.get_logger().info(f"📷 디코딩 성공: {full_str}")
                    confidence = 1.0
                    self.qr_callback(full_str, confidence)
                    self.last_qr_time = current_time
                else:
                    self.get_logger().warn(f"⚠️ QR {idx}는 감지되었으나 디코딩 실패 (빈 문자열)")
        else:
            self.get_logger().info("👀 QR 코드 감지되지 않음.")

    def qr_callback(self, full_str: str, confidence: float):
        self.last_received_time = time.time()

        if not self.connected:
            self.connected = True
            self.get_logger().info('📱 카메라 연결 복구됨.')

        if confidence < 0.8:
            self.get_logger().warn(f'⚠️ 신뢰도 낮음 → 무시됨: {full_str} ({confidence})')
            return

        if '_' in full_str:
            qr_id, target_room = full_str.split('_', 1)
        else:
            qr_id = full_str
            target_room = 'Unknown'
            self.get_logger().info(f'📦 QR 형식 단일: {qr_id} → target_room=Unknown')

        if qr_id not in self.detected_qr_ids:
            self.detected_qr_ids.append(qr_id)
            self.detected_target_rooms.append(target_room)
            self.get_logger().info(
                f'✅ QR 감지 및 저장: qr_id={qr_id}, target_room={target_room} ({confidence})'
            )
            self.handle_qr_request(qr_id, target_room)
        else:
            self.get_logger().info(f'🔁 중복 QR 무시됨: qr_id={qr_id}')

    # def handle_qr_request(self, request, response):
    #     qr_id_requested = request.qr_id
    #     self.get_logger().info(f'📥 QR 요청 수신: {qr_id_requested}')

    #     if qr_id_requested in self.detected_qr_ids:
    #         idx = self.detected_qr_ids.index(qr_id_requested)
    #         response.success = True
    #         response.target_room = self.detected_target_rooms[idx]
    #         self.get_logger().info(f'📤 타겟룸 반환: {response.target_room}')
    #     else:
    #         response.success = False
    #         response.target_room = ''
    #         self.get_logger().warn('📤 요청한 QR ID를 찾을 수 없음')

    #     return response

    def handle_qr_request(self, qr_id, target_room):
        request = GetTargetRoom.Request()
        request.qr_id = qr_id
        request.target_room = target_room
        future = self.cli.call_async(request)
        return future


def main(args=None):
    rclpy.init(args=args)
    node = QRDetectorCameraNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.cap.release()
        cv2.destroyAllWindows()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()

