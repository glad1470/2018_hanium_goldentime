import os
import cv2
import numpy as np
import tensorflow as tf
import sys
import urllib.request

# 현재 폴더의 디렉토리를 저장할수있게 추가합니다
sys.path.append("..")

# Import utilites
from utils import label_map_util
from utils import visualization_utils as vis_util
import multiprocessing

# Initialize webcam feed
video = cv2.VideoCapture(0)
video2 = cv2.VideoCapture(1)


def status_handler(int):
    # 객체 인식을 실행하는 프로그램의 디렉토리를 저장하여 프로그램을 실행하기 위한 유틸 파일을 사용할수 있게 설정합니다
    sys.path.insert(0, 'C:/models/research/object_detection')
    # 학습 모델이 저장되어 있는 폴더의 이름을 저장합니다.
    MODEL_NAME = 'inference_graph'
    # 작업 중인 디렉토리를 저장합니다
    CWD_PATH = 'C:/models/research/object_detection'

    # 학습 모델 파일을 지정합니다
    PATH_TO_CKPT = os.path.join(CWD_PATH,MODEL_NAME,'frozen_inference_graph.pb')

    # 학습 모델을 사용하여 구분할 class명이 저장되어있는 폴더와 파일을 지정합니다.
    PATH_TO_LABELS = os.path.join(CWD_PATH,'training','labelmap.pbtxt')
    # 인식을 할 가짓수는 2가지입니다. (안전[Person], 위험[Warning])
    NUM_CLASSES = 2
    # 객체의 라벨과 클래스를 연관지어 저장합니다.
    label_map = label_map_util.load_labelmap(PATH_TO_LABELS)
    categories = label_map_util.convert_label_map_to_categories(label_map, max_num_classes=NUM_CLASSES, use_display_name=True)
    category_index = label_map_util.create_category_index(categories)
    # 머신 러닝한 모델을 사용하기 위해 텐서플로우를 메모리에 로드합니다.
    detection_graph = tf.Graph()
    with detection_graph.as_default():
        od_graph_def = tf.GraphDef()
        with tf.gfile.GFile(PATH_TO_CKPT, 'rb') as fid:
            serialized_graph = fid.read()
            od_graph_def.ParseFromString(serialized_graph)
            tf.import_graph_def(od_graph_def, name='')
        sess = tf.Session(graph=detection_graph)

    # 영상의 한 프레임마다 나오는 이미지에 대해 텐서를 지정합니다.
    image_tensor = detection_graph.get_tensor_by_name('image_tensor:0')
    # 출력하는 텐서를 지정합니다.
    detection_boxes = detection_graph.get_tensor_by_name('detection_boxes:0')
    # 영상 분석을 하여 나온 해당 객체의 이름(class)과 정밀도(scores)를 지정합니다.
    detection_scores = detection_graph.get_tensor_by_name('detection_scores:0')
    detection_classes = detection_graph.get_tensor_by_name('detection_classes:0')
    # 총 인식된 객체의 수를 지정합니다.
    num_detections = detection_graph.get_tensor_by_name('num_detections:0')
    if int == 0: # 카메라 1
        video = cv2.VideoCapture(0)
        ret = video.set(3, 1280)
        ret = video.set(4, 720)
    elif int == 1: # 카메라 2
        video = cv2.VideoCapture(1)
        ret = video.set(3, 1280)
        ret = video.set(4, 720)

    while(True):
        # 영상 분석 시작
        ret, frame = video.read()
        frame_expanded = np.expand_dims(frame, axis=0)
        # 객체에 씌울 경계선, 정밀도, 이름, 확률 값을 텐서에 넣어 지정합니다.
        (boxes, scores, classes, num) = sess.run(
            [detection_boxes, detection_scores, detection_classes, num_detections],
            feed_dict={image_tensor: frame_expanded})
        # 유틸 프로그램에 해당 변수를 넣어 나온 결과물들을 저장합니다.
        vis_util.visualize_boxes_and_labels_on_image_array(
            frame,
            np.squeeze(boxes),
            np.squeeze(classes).astype(np.int32),
            np.squeeze(scores),
            category_index,
            use_normalized_coordinates=True,
            min_score_thresh=0.60)  # 객체의 정밀도가 60% 이상일때만 화면에 표시합니다
        # 최종 출력물을 이미지에 씌워 출력합니다.
        cv2.imshow('Object detector', frame)
        if cv2.waitKey(1) == ord('q'):
            break

    # Clean up
    video.release()
    cv2.destroyAllWindows()

cam_list = [0,1]
if __name__ == '__main__':
    pool = multiprocessing.Pool(processes=2) # 동시에 2개의 카메라를 운용
    pool.map(status_handler,cam_list) # 프로세스 하나 당 하나의 카메라가 제공하는 영상 처리를 할당합니다
    pool.close()
    pool.join()
    # pr1 = multiprocessing.Process(target=status_handler,args=([video]))
    # pr2 = multiprocessing.Process(target=status_handler,args=([video2]))
    # pr1.start()
    # pr2.start()
    # pr1.join()
    # pr2.join()

     # status_handler(0)