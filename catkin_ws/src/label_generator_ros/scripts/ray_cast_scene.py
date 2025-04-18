#!/usr/bin/env python3

import rospy
import numpy as np
from Modules import PILBridge
from label_gen import label_generation_ros
from sensor_msgs.msg import Image
from std_msgs.msg import Header, Float64MultiArray
from label_generator_ros.msg import LabelGenInit, LabelGenResponse

class LabelGenNode:
    def __init__(self):

        rospy.init_node('label_generator_node')

        self.label_generator_init = False
        self.label_generator = None

        rospy.Subscriber('/label_generator/init', LabelGenInit, self.hadle_init)
        rospy.Subscriber('/label_generator/request', Float64MultiArray, self.handle_request)

        self.label_pub = rospy.Publisher('/label_generator/label', LabelGenResponse, queue_size=10)

        rospy.loginfo("Label Generator Node ready.")
        rospy.spin()

    def hadle_init(self, msg):

        mesh_path = msg.mesh_path
        map_path = msg.map_serialized_path
        visu3d = False
        r_sub = 1

        # Get intrinsics
        k_image = np.array(msg.k_image).reshape(3, 3)
        self.label_generator = label_generation_ros.LabelGenerator(
                image_shape=(msg.height,msg.width),
                k_color=k_image,
                mesh_path=mesh_path,
                map_serialized_path=map_path,
                r_sub=r_sub,
                visu3d=visu3d
            )
        
        self.label_generator_init = False
        rospy.loginfo("Label Generator initialized")

    def handle_request(self, msg):

        if not self.label_generator_init:
            self.label_pub.publish(LabelGenResponse( 
                label=Image(),
                success=False,
                error_msg="Labeler not initialized"))
            return
        
        rospy.loginfo("Generating label for incoming request.")

        pose = np.array(msg.data).reshape(4, 4)
        probs = self.label_generator.get_label(pose)
        label = np.argmax(probs[:, :, 1:], axis=-1).astype(np.uint8)

        label_msg = PILBridge.numpy_to_rosimg(label, encoding="mono8")
        label_msg.header = Header()
        label_msg.header.stamp = rospy.Time.now()

        self.label_pub.publish(LabelGenResponse( 
            label=label_msg,
            success=True,
            error_msg=""))

        rospy.loginfo("Label published.")


if __name__ == "__main__":
    try:
        LabelGenNode()
    except rospy.ROSInterruptException:
        pass
