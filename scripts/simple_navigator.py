#!/usr/bin/env python3
import rospy
from sensor_msgs.msg import LaserScan
from geometry_msgs.msg import Twist

class SimpleNavigator:
    def __init__(self):
        rospy.init_node('reactive_navigator', anonymous=True)
        
        # Publisher para enviar comandos de velocidad
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)
        
        # Subscriber para leer el LIDAR
        rospy.Subscriber('/scan', LaserScan, self.laser_callback)
        
        self.twist = Twist()
        self.safe_distance = 0.5  # metros
        rospy.loginfo("Reactive Navigator iniciado. Esperando datos de LIDAR...")
        
    def laser_callback(self, data):
        # Dividimos el escaneo en sectores: frente, izquierda, derecha
        front = min(min(data.ranges[0:20]), min(data.ranges[-20:]))  # frente
        left  = min(data.ranges[80:100])                             # izquierda
        right = min(data.ranges[260:280])                            # derecha

        rospy.loginfo(f"Front: {front:.2f} m, Left: {left:.2f} m, Right: {right:.2f} m")

        if front > self.safe_distance:
            # Camino libre: avanzar
            self.twist.linear.x = 0.2
            self.twist.angular.z = 0.0
        else:
            # Obstáculo enfrente: decidir hacia dónde girar
            self.twist.linear.x = 0.0
            if left > right:
                self.twist.angular.z = 0.5  # girar izquierda
            else:
                self.twist.angular.z = -0.5 # girar derecha

        self.cmd_pub.publish(self.twist)

    def run(self):
        rospy.spin()

if __name__ == '__main__':
    try:
        navigator = SimpleNavigator()
        navigator.run()
    except rospy.ROSInterruptException:
        pass