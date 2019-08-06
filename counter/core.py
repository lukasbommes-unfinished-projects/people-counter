from counter.detectors import DetectorTF


def get_cams(room_id):

    return cams


def get_people_count(cams):
    # get a snapshot from each camera
    # detect people in the snapshots
    # count people
    # return people count


if __name__ == "__main__":

    detector = DetectorTF(path="counter/data/faster_rcnn_resnet101_coco_2018_01_28/frozen_inference_graph.pb")
