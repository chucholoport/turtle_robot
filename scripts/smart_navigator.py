#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist
import numpy as np
import time

class SmartExploreNavigator:
    def __init__(self):
        rospy.init_node('smart_explore_navigator', anonymous=True)
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        rospy.Subscriber('/scan', LaserScan, self.laser_callback)
        self.twist = Twist()
        self.safe_distance = 0.45   # umbral ajustado
        self.state = "FORWARD"
        self.escape_start = None
        rospy.loginfo("Smart Explore Navigator iniciado.")

    def laser_callback(self, data):
        ranges = np.array(data.ranges)
        ranges = np.where(np.isinf(ranges), data.range_max, ranges)

        # Sectores
        front_sector = np.concatenate((ranges[0:15], ranges[-15:]))
        left_sector = ranges[60:120]
        right_sector = ranges[240:300]

        front_min = np.min(front_sector)
        left_min = np.min(left_sector)
        right_min = np.min(right_sector)

        rospy.loginfo(f"Front: {front_min:.2f}, Left: {left_min:.2f}, Right: {right_min:.2f}, State: {self.state}")

        if self.state == "FORWARD":
            if front_min > self.safe_distance:
                # Avanzar con corrección angular suave
                self.twist.linear.x = 0.25
                correction = (right_min - left_min) * 0.01
                self.twist.angular.z = correction
                rospy.loginfo(f"Avanzando recto con corrección {correction:.2f}")
            else:
                self.state = "AVOID"

        elif self.state == "AVOID":
            if front_min > self.safe_distance:
                # Si el frente mejora, volver a avanzar
                self.state = "FORWARD"
            else:
                # Rodear con avance lento + giro
                self.twist.linear.x = 0.15
                if left_min > right_min:
                    self.twist.angular.z = 0.3
                    rospy.loginfo("Rodeando por izquierda con avance")
                else:
                    self.twist.angular.z = -0.3
                    rospy.loginfo("Rodeando por derecha con avance")

                # Escape más rápido si el frente está muy bloqueado
                if front_min < 0.25:
                    self.state = "ESCAPE"
                    self.escape_start = time.time()

        elif self.state == "ESCAPE":
            if time.time() - self.escape_start < 2.0:
                self.twist.linear.x = -0.2
                self.twist.angular.z = 0.0
                rospy.logwarn("Retrocediendo para escapar")
            else:
                self.state = "EXPLORE"

        elif self.state == "EXPLORE":
            # Rotación exploratoria hacia el lado más libre
            self.twist.linear.x = 0.0
            if left_min > right_min:
                self.twist.angular.z = 0.5
                rospy.logwarn("Explorando con giro a la izquierda")
            else:
                self.twist.angular.z = -0.5
                rospy.logwarn("Explorando con giro a la derecha")

            if front_min > self.safe_distance:
                self.state = "FORWARD"
                rospy.loginfo("Espacio encontrado, avanzando")

        self.cmd_pub.publish(self.twist)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        nav = SmartExploreNavigator()
        nav.run()
    except rospy.ROSInterruptException:
        pass