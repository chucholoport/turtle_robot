#!/usr/bin/env python3
"""
Proyecto: Turtle Robot Control desde ROS hacia Arduino
Autor: Jesús López
Fecha: 25/11/2025

Descripción:
Este script en Python actúa como nodo principal del robot diferencial.
Publica mensajes geometry_msgs/Twist en el tópico /cmd_vel para mover
el robot, y se suscribe al tópico /wheel_rpm para leer las RPM
calculadas por el Arduino.

Entorno:
- Ubuntu 20.04
- ROS Noetic
- Arduino UNO / Mega 2560 con rosserial_arduino
- Paquete turtle_robot

Flujo ROS:
1. Este nodo publica mensajes Twist en /cmd_vel.
2. El puente rosserial transmite el mensaje al Arduino.
3. El Arduino controla los motores y calcula las RPM.
4. El Arduino publica /wheel_rpm.
5. Este nodo recibe y muestra las RPM en consola.

Ejemplo de ejecución:
    chmod +x scripts/turtle_robot.py
    rosrun turtle_robot turtle_robot.py

Ejemplo de publicación manual:
    rostopic pub /cmd_vel geometry_msgs/Twist "linear: {x: 0.5}" "angular: {z: 0.0}"

Objetivo didáctico:
- Integrar control y retroalimentación en un robot diferencial.
- Practicar publisher + subscriber en un mismo nodo.
- Visualizar datos reales provenientes del hardware.
"""

import rospy
from geometry_msgs.msg import Twist
from std_msgs.msg import Float32MultiArray


class TurtleRobotNode:

    def __init__(self):

        # Inicializa nodo
        rospy.init_node('turtle_robot_node', anonymous=True)

        # Publisher → movimiento
        self.cmd_pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

        # Subscriber → RPM desde Arduino
        rospy.Subscriber('/wheel_rpm', Float32MultiArray, self.rpm_callback)

        rospy.loginfo("Nodo turtle_robot iniciado")

    # ==============================
    # Callback RPM
    # ==============================
    def rpm_callback(self, msg):
        if len(msg.data) >= 2:
            left_rpm = msg.data[0]
            right_rpm = msg.data[1]
            rospy.loginfo(f"RPM -> Left: {left_rpm:.2f} | Right: {right_rpm:.2f}")

    # ==============================
    # Envío de comando
    # ==============================
    def send_command(self, linear=0.5, angular=0.0):

        msg = Twist()
        msg.linear.x = linear
        msg.angular.z = angular

        rospy.loginfo(f"Publicando cmd_vel: linear.x={linear} angular.z={angular}")
        self.cmd_pub.publish(msg)


def main():

    robot = TurtleRobotNode()
    rate = rospy.Rate(1)  # 1 Hz

    while not rospy.is_shutdown():
        robot.send_command(linear=0.5, angular=0.0)
        rate.sleep()


if __name__ == '__main__':
    try:
        main()
    except rospy.ROSInterruptException:
        pass
