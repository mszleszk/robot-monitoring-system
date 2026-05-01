import rclpy
from rclpy.node import Node

from interfaces.srv import ComponentError
from std_srvs.srv import Empty

class ErrorHandler(Node):
    
    def __init__(self):
        super().__init__('error_handler')

        self.declare_parameter('sensors', ['sensor'])

        self.sensors = self.get_parameter('sensors').value

        self.component_error_srv = self.create_service(
            ComponentError, 
            'component_error', 
            self.component_error_callback
        )

        self.sensor_clients = {}

        for sensor in self.sensors:
            self.sensor_clients[sensor] = self.create_client(Empty, f'restart_{sensor}')



    def component_error_callback(self, request, response):
        self.get_logger().info(f'Fixing {request.sensor_name}')

        client = self.sensor_clients[request.sensor_name]

        if not client.wait_for_service(timeout_sec=1.0):
            return
        
        client.call_async(Empty.Request())

        return response
        

def main():
    rclpy.init()

    error_handler = ErrorHandler()

    rclpy.spin(error_handler)

    error_handler.destroy_node()
    rclpy.shutdown()