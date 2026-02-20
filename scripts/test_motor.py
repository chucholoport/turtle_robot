#!/usr/bin/env python3
"""
Proyecto: Test Motor desde ROS hacia Arduino Mega 2560
Autor: Jesús López
Fecha: 25/11/2025

Descripción:
Este script en Python actúa como publisher en ROS. Envía mensajes
geometry_msgs/Twist al tópico /cmd_vel, que son recibidos por el Arduino
a través de rosserial. El campo linear.x se usa para controlar la velocidad
del motor. En este test, se publica siempre un valor positivo para que el
motor gire continuamente.

Entorno:
- Ubuntu 20.04
- ROS Noetic
- Arduino Uno/Mega 2560 con rosserial_arduino
- Submódulo turtle_robot_sketchbook

Flujo ROS:
1. Este nodo Python publica mensajes Twist en el tópico /cmd_vel.
2. El puente rosserial transmite los mensajes al Arduino por USB.
3. El Arduino, como subscriber, recibe el mensaje y activa el motor.
4. El motor gira mientras se publiquen valores positivos en linear.x.

Ejemplo de ejecución:
    chmod +x scripts/test_motor.py
    rosrun turtle_robot test_motor.py

Ejemplo de publicación manual:
    rostopic pub /cmd_vel geometry_msgs/Twist "linear: {x: 1.0}" "angular: {z: 0.0}"

Objetivo didáctico:
- Mostrar cómo un nodo Python en ROS puede controlar un motor real.
- Practicar la comunicación publisher → subscriber entre ROS y Arduino.
- Documentar claramente el entorno y flujo para reproducibilidad.
"""

import rospy
from geometry_msgs.msg import Twist
from functools import partial

# Variables globales para recordar último valor
last_linear = None
last_angular = None

def cmd_callback(pub, msg):
    global last_linear, last_angular

    lin = msg.linear.x
    ang = msg.angular.z

    # Publicar solo si cambió respecto al último valor
    if lin != last_linear or ang != last_angular:
        rospy.loginfo(f"Recibido cmd_vel: linear.x={lin:.2f} angular.z={ang:.2f}")
        pub.publish(msg)
        last_linear, last_angular = lin, ang
        
    # Filtrar silencios redundantes (mensajes con 0 por latencia)
    if lin == 0.0 and ang == 0.0:
        return


def test_motor():
    # Inicializa el nodo ROS
    rospy.init_node('test_motor_publisher', anonymous=True)

    # Publisher en el tópico /cmd_vel
    pub = rospy.Publisher('/cmd_vel', Twist, queue_size=10)

    # Subscriber → comandos desde teleop_keyboard
    rospy.Subscriber('/cmd_vel', Twist, partial(cmd_callback, pub))

    # rate = rospy.Rate(1)  # 1 Hz → un mensaje por segundo

    # while not rospy.is_shutdown():
    #     msg = Twist()
    #     msg.linear.x = 1.0   # valor positivo → motor siempre ON
    #     msg.angular.z = 0.0  # sin giro angular
    #     rospy.loginfo(f"Publicando cmd_vel: linear.x={msg.linear.x}")
    #     pub.publish(msg)
    #     rate.sleep()

if __name__ == '__main__':
    try:
        test_motor()
        rospy.spin()
    except rospy.ROSInterruptException:
        pass