import rclpy
from rclpy.node import Node

from std_msgs.msg import Bool
from std_srvs.srv import Empty

import random

class Sensor(Node):
    def __init__(self):
        super().__init__('sensor')

        self.declare_parameter('jam_probability', 0.05)
        self.declare_parameter('error_probability', 0.05)
        self.declare_parameter('timer_period', 1.0)

        self.jam_probability = self.get_parameter('jam_probability').value
        self.error_probablity = self.get_parameter('error_probability').value
        self.timer_period = self.get_parameter('timer_period').value

        self.state = True

        self.publisher = self.create_publisher(Bool, f'{self.get_name()}_state', 10)

        self.timer = self.create_timer(self.timer_period, self.callback)

        self.restart_srv = self.create_service(Empty, f'restart_{self.get_name()}', self.restart_callback)

    def callback(self):
        msg = Bool()
        
        if random.random() < self.jam_probability:
            self.timer.cancel()
            return

        if random.random() < self.error_probablity:
            self.state = False

        msg.data = self.state

        self.publisher.publish(msg)
        self.get_logger().info(f'Publishing: {msg.data}')

    def restart_callback(self, request, response):
        self.state = True
        self.timer.reset()

        self.get_logger().info('Fixed')

        return response

def main():
    rclpy.init()

    sensor = Sensor()

    rclpy.spin(sensor)

    sensor.destroy_node()
    rclpy.shutdown()
