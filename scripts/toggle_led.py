#!/usr/bin/env python3
"""
Proyecto: Toggle LED desde ROS hacia Arduino Uno
Autor: Jesús López
Fecha: 25/11/2025

Descripción:
Este script en Python actúa como publisher en ROS. Envía mensajes
std_msgs/Bool al tópico /toggle_led, que son recibidos por el Arduino Uno
a través de rosserial. El LED conectado al pin 13 se enciende o apaga
según el valor publicado.

Entorno:
- Ubuntu 20.04
- ROS Noetic
- Arduino Uno con rosserial_arduino
- Submódulo turtle_robot_sketchbook en branch feature/arduino_uno

Flujo ROS:
1. Este nodo Python publica mensajes Bool en el tópico /toggle_led.
2. El puente rosserial (rosrun rosserial_python serial_node.py /dev/ttyUSB0)
   transmite los mensajes al Arduino Uno por USB.
3. El Arduino, como subscriber, recibe el mensaje y enciende/apaga el LED.
4. Se puede alternar automáticamente o controlar manualmente el estado.

Ejemplo de ejecución:
    chmod +x scripts/toggle_led.py
    rosrun COYOTE_ROBOT toggle_led.py

Ejemplo de publicación manual:
    rostopic pub /toggle_led std_msgs/Bool "data: true"
    rostopic pub /toggle_led std_msgs/Bool "data: false"

Objetivo didáctico:
- Mostrar cómo un nodo Python en ROS puede controlar hardware real.
- Practicar la comunicación publisher → subscriber entre ROS y Arduino.
- Documentar claramente el entorno y flujo para reproducibilidad.
"""

import rospy
from std_msgs.msg import Bool

def led_callback(pub, msg):
    rospy.loginfo(f"Publicando LED: {msg.data}")
    pub.publish(msg)

def toggle_led():
    # Inicializa el nodo ROS
    rospy.init_node('toggle_led_publisher', anonymous=True)

    # Publisher en el tópico /toggle_led
    pub = rospy.Publisher('/toggle_led', Bool, queue_size=10)

    rospy.loginfo("Type 'on' or 'off' to control LED")
        
    while not rospy.is_shutdown():
        # Interfaz para usuario
        command = input(">> ").strip().lower()

        # Encendido
        if command == "on":
            led_callback(pub, Bool(data=True))
        # Apagado
        elif command == "off":
            led_callback(pub, Bool(data=False))
        # Salida
        elif command == "q":
            rospy.loginfo("Saliendo.")
            break
        # Invalido
        else:
            rospy.logwarn("Invalid command. Use 'on' or 'off'")


if __name__ == '__main__':
    try:
        toggle_led()
    except rospy.ROSInterruptException:
        pass
