#!/usr/bin/env python3

import rospy
from geometry_msgs.msg import Twist

def forward_forever():
    rospy.init_node('tb3_forward_gazebo', anonymous=False)

    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
    rate = rospy.Rate(10)

    cmd = Twist()
    cmd.linear.x = 2.0
    cmd.angular.z = 0.0

    while not rospy.is_shutdown():
        pub.publish(cmd)
        rate.sleep()

if __name__ == '__main__':
    forward_forever()